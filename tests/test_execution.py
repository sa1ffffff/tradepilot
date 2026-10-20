"""Maker-first execution against a fake ccxt client -- no network."""
import dataclasses

import ccxt
import pytest

from config import Config
from bot.costs import passive_cost, round_trip, taker_cost
from bot.exchange import OkxExchange


class FakeClient:
    """Fills post-only orders according to a script; market orders always fill."""

    def __init__(self, maker_fills):
        self.maker_fills = list(maker_fills)  # fraction filled per post-only attempt
        self.orders, self.created = {}, []

    def fetch_order_book(self, symbol, limit):
        return {"bids": [[100.0, 1]], "asks": [[100.1, 1]]}

    def create_order(self, symbol, type_, side, amount, price=None, params=None):
        oid = str(len(self.created) + 1)
        self.created.append((type_, side, amount, (params or {}).get("postOnly", False)))
        if type_ == "limit":
            frac = self.maker_fills.pop(0) if self.maker_fills else 0.0
            if frac is None:
                raise ccxt.InvalidOrder("post only would cross")
            filled, px, rate = amount * frac, price, 0.0008
            status = "closed" if frac >= 1 else "open"
        else:
            filled, px, rate, status = amount, 100.2, 0.001, "closed"
        fee_ccy = "BTC" if side == "buy" else "USDT"
        fee_cost = filled * rate if side == "buy" else filled * px * rate
        self.orders[oid] = {"id": oid, "status": status, "filled": filled, "average": px,
                            "fee": {"cost": fee_cost, "currency": fee_ccy}}
        return {"id": oid}

    def fetch_order(self, oid, symbol):
        return self.orders[oid]

    def cancel_order(self, oid, symbol):
        self.orders[oid]["status"] = "canceled"


def make_ex(maker_fills, **cfg_kw):
    ex = OkxExchange.__new__(OkxExchange)  # skip __init__: no keys, no network
    ex.cfg = dataclasses.replace(Config(), maker_wait_seconds=0, maker_attempts=3, **cfg_kw)
    ex.client = FakeClient(maker_fills)
    ex.market = {"limits": {"amount": {"min": 0.00001}}}
    ex.base, ex.quote = "BTC", "USDT"
    return ex


def test_full_maker_fill_uses_no_market_order():
    ex = make_ex([1.0])
    f = ex.buy(0.01)
    assert f["filled"] == pytest.approx(0.01) and f["maker_share"] == 1.0
    assert [c[0] for c in ex.client.created] == ["limit"]
    assert f["fee_base"] == pytest.approx(0.01 * 0.0008)


def test_partial_maker_then_market_fallback():
    ex = make_ex([0.5, 0.0, 0.0])
    f = ex.buy(0.01)
    assert f["filled"] == pytest.approx(0.01)
    assert f["maker_share"] == pytest.approx(0.5)
    assert [c[0] for c in ex.client.created] == ["limit", "limit", "limit", "market"]
    assert ex.client.created[-1][2] == pytest.approx(0.005)  # only the remainder goes to market
    assert f["average"] == pytest.approx((0.005 * 100.0 + 0.005 * 100.2) / 0.01)


def test_post_only_rejection_is_retried():
    ex = make_ex([None, 1.0])
    f = ex.sell(0.01)
    assert f["maker_share"] == 1.0 and len(ex.client.created) == 2


def test_urgent_sell_goes_straight_to_market():
    ex = make_ex([1.0])
    f = ex.sell(0.01, urgent=True)
    assert [c[0] for c in ex.client.created] == ["market"] and f["maker_share"] == 0.0


def test_taker_mode_never_posts_limits():
    ex = make_ex([1.0], execution="taker")
    ex.buy(0.01)
    assert [c[0] for c in ex.client.created] == ["market"]


def test_cost_model():
    cfg = Config(execution="maker", maker_fee=0.0008, taker_fee=0.001, slippage_bps=2,
                 maker_fill_rate=0.7)
    assert taker_cost(cfg) == pytest.approx(0.0012)
    assert passive_cost(cfg) == pytest.approx(0.7 * 0.0008 + 0.3 * 0.0012)
    assert round_trip(dataclasses.replace(cfg, execution="taker")) == pytest.approx(0.0024)
