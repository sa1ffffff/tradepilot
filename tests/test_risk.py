import dataclasses

from config import Config
from bot.risk import RiskManager

CFG = Config(risk_fraction=0.01, max_notional_usd=50.0, max_daily_loss_usd=20.0, taker_fee=0.0,
             slippage_bps=0.0, max_cost_per_r=0)


def test_size_respects_notional_cap():
    r = RiskManager(CFG)
    d = r.evaluate_entry(price=60000, stop_distance=200, equity=1000, kill=False)
    assert d.allowed
    assert d.size * 60000 <= CFG.max_notional_usd + 1e-6


def test_kill_switch_blocks():
    r = RiskManager(CFG)
    assert not r.evaluate_entry(60000, 200, 1000, kill=True).allowed


def test_daily_loss_blocks():
    r = RiskManager(CFG)
    r.record_pnl(-25)  # beyond the -20 limit
    assert r.daily_loss_hit()
    assert not r.evaluate_entry(60000, 200, 1000, kill=False).allowed


def test_duplicate_tracking():
    r = RiskManager(CFG)
    assert not r.is_duplicate("k")
    r.remember("k")
    assert r.is_duplicate("k")


def test_rejects_zero_or_nan_stop():
    r = RiskManager(CFG)
    assert not r.evaluate_entry(60000, 0, 1000, kill=False).allowed
    assert not r.evaluate_entry(60000, float("nan"), 1000, kill=False).allowed


def test_uncapped_sizing_scales_with_risk():
    big = dataclasses.replace(CFG, max_notional_usd=1e15)
    r = RiskManager(big)
    d = r.evaluate_entry(price=60000, stop_distance=2000, equity=1000, kill=False)
    # risk budget 10 / stop distance 2000 = 0.005 base ($300, within equity)
    assert abs(d.size - 0.005) < 1e-6


def test_spot_size_never_exceeds_equity():
    big = dataclasses.replace(CFG, max_notional_usd=1e15)
    r = RiskManager(big)
    # risk-based size would be 0.05 BTC = $3000 on $1000 equity -> capped
    d = r.evaluate_entry(price=60000, stop_distance=200, equity=1000, kill=False)
    assert d.size * 60000 <= 1000 + 1e-6


def test_state_roundtrip():
    r = RiskManager(CFG)
    r.roll_day(__import__("datetime").date(2026, 10, 21))
    r.record_pnl(-5)
    r.remember("a")
    r2 = RiskManager(CFG)
    r2.load_dict(r.to_dict())
    assert r2.realized_pnl_today == -5 and r2.is_duplicate("a")


def test_cost_gate_blocks_stops_too_tight_for_fees():
    cfg = dataclasses.replace(CFG, execution="taker", taker_fee=0.001, slippage_bps=0.0,
                              max_cost_per_r=0.2, max_notional_usd=1e15)
    r = RiskManager(cfg)
    # round trip 0.2% of 60000 = 120; 20% of a 300 stop = 60 -> blocked
    assert r.evaluate_entry(60000, 300, 1000, kill=False).reason == "stop too tight for trading costs"
    # a 1200 stop: 20% = 240 >= 120 -> allowed
    assert r.evaluate_entry(60000, 1200, 1000, kill=False).allowed
