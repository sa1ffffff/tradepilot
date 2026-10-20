"""Runner logic against a fake exchange -- no network, no keys."""
import dataclasses

import numpy as np
import pandas as pd
import pytest

from config import Config
from bot import runner
from bot.risk import RiskManager
from bot.strategies import StrategySpec, default_spec

SPEC = default_spec()


class FakeLog:
    def __init__(self):
        self.events = []

    def _rec(self, msg, fields=None):
        self.events.append(msg)

    info = warning = error = exception = _rec


class FakeExchange:
    def __init__(self, closes, base_held=0.0, price=None):
        n = len(closes)
        closes = np.array(closes, dtype=float)
        self.df = pd.DataFrame({
            "time": pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC"),
            "open": closes, "high": closes * 1.001, "low": closes * 0.999,
            "close": closes, "volume": np.ones(n),
        })
        self.base = base_held          # e.g. the BTC an OKX demo account starts with
        self.quote = 10_000.0
        self.price = price if price is not None else float(closes[-1])
        self.orders = []

    def fetch_closed_ohlcv(self, bars):
        return self.df

    def last_price(self):
        return self.price

    def equity_quote(self):
        return self.quote

    def base_balance(self):
        return self.base

    def _fill(self, side, amount):
        self.orders.append((side, amount))
        fee_base = amount * 0.001 if side == "buy" else 0.0
        fee_quote = 0.0 if side == "buy" else amount * self.price * 0.001
        self.base += (amount - fee_base) if side == "buy" else -amount
        return {"id": str(len(self.orders)), "status": "closed", "filled": amount,
                "average": self.price, "fee_base": fee_base,
                "fee_quote": fee_quote + fee_base * self.price}

    def buy(self, amount):
        return self._fill("buy", amount)

    def sell(self, amount, urgent=False):
        self.last_sell_urgent = urgent
        return self._fill("sell", amount)


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # KILL / state.json land in a temp dir
    return dataclasses.replace(Config(), max_notional_usd=50.0, max_daily_loss_usd=20.0,
                               risk_fraction=0.01, min_base_size=1e-5)


BUY = [100.0] * 80 + [130.0]
SELL = [100.0] * 80 + [70.0]


def test_preexisting_wallet_balance_is_not_treated_as_position(cfg):
    ex = FakeExchange(BUY, base_held=1.0)  # demo account pre-funded with 1 BTC
    state = {"position": None, "risk": {}}
    runner.step(cfg, SPEC, ex, RiskManager(cfg), state, FakeLog())
    assert ex.orders and ex.orders[0][0] == "buy"
    assert ex.orders[0][1] * 130 <= cfg.max_notional_usd + 1e-6
    assert state["position"] is not None


def test_sell_signal_never_sells_holdings_the_bot_did_not_buy(cfg):
    ex = FakeExchange(SELL, base_held=1.0)
    runner.step(cfg, SPEC, ex, RiskManager(cfg), {"position": None, "risk": {}}, FakeLog())
    assert ex.orders == []


def test_round_trip_records_pnl_and_persists(cfg):
    ex = FakeExchange(BUY, base_held=1.0)
    risk = RiskManager(cfg)
    state = {"position": None, "risk": {}}
    runner.step(cfg, SPEC, ex, risk, state, FakeLog())
    bought = state["position"]["size"]

    ex.df = FakeExchange(SELL).df
    ex.price = 120.0
    runner.step(cfg, SPEC, ex, risk, state, FakeLog())
    assert ex.orders[-1] == ("sell", bought)  # only what the bot bought
    assert state["position"] is None
    assert risk.realized_pnl_today < 0
    assert runner.load_state(cfg.state_file)["position"] is None


def test_stop_closes_position_between_signals(cfg):
    ex = FakeExchange(BUY)
    risk = RiskManager(cfg)
    state = {"position": None, "risk": {}}
    runner.step(cfg, SPEC, ex, risk, state, FakeLog())
    ex.df = FakeExchange([100.0] * 80).df  # no signal at all
    ex.price = state["position"]["stop"] - 1
    log = FakeLog()
    runner.step(cfg, SPEC, ex, risk, state, log)
    assert state["position"] is None and "exit_filled" in log.events


def test_same_bar_buy_is_not_repeated(cfg):
    ex = FakeExchange(BUY)
    risk = RiskManager(cfg)
    state = {"position": None, "risk": {}}
    runner.step(cfg, SPEC, ex, risk, state, FakeLog())
    state["position"] = None  # pretend the fill was lost
    runner.step(cfg, SPEC, ex, risk, state, FakeLog())
    assert len(ex.orders) == 1


def test_kill_switch_blocks_entry(cfg):
    open(cfg.kill_file, "w").close()
    ex = FakeExchange(BUY)
    runner.step(cfg, SPEC, ex, RiskManager(cfg), {"position": None, "risk": {}}, FakeLog())
    assert ex.orders == []


def test_daily_loss_survives_restart(cfg):
    risk = RiskManager(cfg)
    risk.roll_day(pd.Timestamp.now(tz="UTC").date())
    risk.record_pnl(-25)
    runner.save_state(cfg.state_file, {"position": None, "risk": risk.to_dict()})

    fresh = RiskManager(cfg)
    fresh.load_dict(runner.load_state(cfg.state_file)["risk"])
    ex = FakeExchange(BUY)
    runner.step(cfg, SPEC, ex, fresh, {"position": None, "risk": {}}, FakeLog())
    assert ex.orders == []


def test_take_profit_closes_position(cfg):
    spec = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=2.0, tp_r=1.0)
    ex = FakeExchange(BUY)
    risk = RiskManager(cfg)
    state = {"position": None, "risk": {}}
    runner.step(cfg, spec, ex, risk, state, FakeLog())
    assert state["position"]["tp"] > state["position"]["entry"]
    ex.price = state["position"]["tp"] + 1
    runner.step(cfg, spec, ex, risk, state, FakeLog())
    assert state["position"] is None and risk.realized_pnl_today > 0


def test_load_strategy_overrides_symbol_and_timeframe(cfg):
    import json
    with open(cfg.strategy_file, "w") as f:
        json.dump({"symbol": "ETH/USDT", "timeframe": "1h", "name": "supertrend",
                   "params": {"mult": 3.0, "trend": 0}, "stop_atr": 2.5, "tp_r": None}, f)
    c, spec = runner.load_strategy(cfg)
    assert (c.symbol, c.timeframe, spec.name, spec.stop_atr) == ("ETH/USDT", "1h", "supertrend", 2.5)
