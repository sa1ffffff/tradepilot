"""Dashboard controls: request files, daily target, close requests, analysis, risk estimate."""
import json
import time

import numpy as np
import pandas as pd
import pytest

from bot import control, explain, runner
from bot import futures_runner as fr
from bot.risk import RiskManager
from bot.strategies import STRATEGIES, StrategySpec, signals_ls
from bot.target import assess
from tests.test_futures import SPEC as FSPEC, FakeFutures, Log, fcfg, new_state  # noqa: F401
from tests.test_runner import BUY, SPEC, FakeExchange, FakeLog, cfg  # noqa: F401


def test_request_files_round_trip(tmp_path):
    root = str(tmp_path)
    control.request_close("futures", "ADA/USDT:USDT", root)
    assert control.close_requested("futures", "ADA/USDT:USDT", root)
    assert [(r["bot"], r["symbol"]) for r in control.pending_closes(root)] == [("futures", "ADA/USDT:USDT")]
    control.clear_close("futures", "ADA/USDT:USDT", root)
    assert control.pending_closes(root) == []
    control.request_stop("spot", root)
    assert control.stop_requested("spot", root) and not control.stop_requested("futures", root)


def test_wait_wakes_early_on_a_request(tmp_path):
    root = str(tmp_path)
    control.request_stop("spot", root)
    t = time.monotonic()
    control.wait(30, "spot", root)
    assert time.monotonic() - t < 1.5


def test_target_counts_both_bots_and_ignores_other_days(tmp_path):
    root = str(tmp_path)
    other = tmp_path / "state_futures.json"
    today = pd.Timestamp.now(tz="UTC").date().isoformat()
    other.write_text(json.dumps({"risk": {"day": today, "realized_pnl_today": 10.0}}))
    control.set_target(15.0, root=root)
    assert control.target_reached(control.combined_pnl_today(4.0, str(other)), root) is None
    assert control.target_reached(control.combined_pnl_today(5.0, str(other)), root) == 15.0
    other.write_text(json.dumps({"risk": {"day": "2000-01-01", "realized_pnl_today": 99.0}}))
    assert control.combined_pnl_today(5.0, str(other)) == 5.0


def _ahead(cfg, pnl):
    risk = RiskManager(cfg)
    risk.roll_day(pd.Timestamp.now(tz="UTC").date())
    risk.record_pnl(pnl)
    return risk


def test_spot_target_blocks_entry(cfg):
    control.set_target(1.0)
    ex, log = FakeExchange(BUY), FakeLog()
    runner.step(cfg, SPEC, ex, _ahead(cfg, 2.0), {"position": None, "risk": {}}, log)
    assert ex.orders == [] and "entry_skipped" in log.events


def test_spot_close_request_closes_the_position(cfg):
    ex, risk, state = FakeExchange(BUY), RiskManager(cfg), {"position": None, "risk": {}}
    runner.step(cfg, SPEC, ex, risk, state, FakeLog())
    assert state["position"] is not None
    control.request_close("spot", cfg.symbol)
    runner.step(cfg, SPEC, ex, risk, state, FakeLog())
    assert state["position"] is None and ex.orders[-1][0] == "sell"
    assert not control.close_requested("spot", cfg.symbol)


def test_futures_target_blocks_entry(fcfg):
    control.set_target(1.0)
    ex, log = FakeFutures([100.0] * 80 + [70.0]), Log()
    fr.step(fcfg, FSPEC, ex, _ahead(fcfg, 3.0), new_state(fcfg), log)
    assert ex.pos is None
    assert any(m == "entry_skipped" and "target" in f["reason"] for m, f in log.events)


def test_futures_close_request_and_target_close(fcfg):
    ex, risk, store, log = FakeFutures([100.0] * 80 + [70.0]), RiskManager(fcfg), new_state(fcfg), Log()
    fr.step(fcfg, FSPEC, ex, risk, store, log)
    assert store.slot(fcfg.symbol)["position"] is not None
    assert not fr.handle_requests(fcfg, ex, risk, store, log)       # nothing asked
    control.request_close("futures", fcfg.symbol)
    assert fr.handle_requests(fcfg, ex, risk, store, log)
    assert store.slot(fcfg.symbol)["position"] is None and ex.pos is None
    assert not control.close_requested("futures", fcfg.symbol)
    assert [f["reason"] for m, f in log.events if m == "exit_filled"] == ["manual"]



def test_futures_target_with_close_open_flattens(fcfg):
    ex, risk, store, log = FakeFutures([100.0] * 80 + [70.0]), RiskManager(fcfg), new_state(fcfg), Log()
    fr.step(fcfg, FSPEC, ex, risk, store, log)
    control.set_target(1.0, close_open=False)
    assert not fr.handle_requests(fcfg, ex, _ahead(fcfg, 5.0), store, log)   # target alone: keep it
    control.set_target(1.0, close_open=True)
    assert fr.handle_requests(fcfg, ex, _ahead(fcfg, 5.0), store, log)
    assert [f["reason"] for m, f in log.events if m == "exit_filled"] == ["daily target"]


def _frame(n=600, seed=3):
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="4h", tz="UTC"),
                         "open": close, "high": close * 1.004, "low": close * 0.996, "close": close,
                         "volume": np.ones(n)})


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_every_strategy_explains_itself(name):
    spec = StrategySpec(name, dict(STRATEGIES[name].defaults), 2.0, 3.0, shorts=True)
    a = explain.analyse(_frame(), spec, "4h", bars=100)
    assert set(a["sides"]) == {"long", "short"} and a["headline"] and a["rule"]
    assert len(a["candles"]) == 100 and all(c["detail"] for s in a["sides"].values() for c in s["checks"])
    assert pd.Timestamp(a["next_decision"]) - pd.Timestamp(a["bar_time"]) == pd.Timedelta(hours=8)


@pytest.mark.parametrize("name", ["donchian_breakout", "supertrend", "ema_cross", "bollinger_reversion"])
def test_explanation_agrees_with_the_signal(name):
    """On a bar where the strategy fired, the explainer says every check held."""
    spec = StrategySpec(name, dict(STRATEGIES[name].defaults), 2.0, None, True)
    df = _frame(1200)
    sig = signals_ls(df, spec)
    for col, side in (("entry", "long"), ("short_entry", "short")):
        fired = np.flatnonzero(sig[col].to_numpy())
        if not len(fired):
            continue
        a = explain.analyse(df.iloc[:int(fired[-1]) + 1], spec, "4h", bars=50)
        assert a["sides"][side]["ready"] and all(c["ok"] for c in a["sides"][side]["checks"]), \
            a["sides"][side]["checks"]
        assert a["mood"] == "signal"


def test_target_assessment_is_monotonic():
    slots = [{"label": "x", "risk_fraction": 0.02,
              "evidence": {"trades": 120, "win_rate_pct": 45.0, "profit_factor": 1.6}}] * 8
    easy = assess(5, 1000, slots, 400, days=3000)
    hard = assess(150, 1000, slots, 400, days=3000)
    assert easy["ok"] and easy["p_hit_day"] > hard["p_hit_day"]
    assert hard["verdict"] == "unlikely" and hard["target_pct"] == 15.0
    assert not assess(5, 1000, [{"label": "x", "risk_fraction": 0.02, "evidence": {}}], 400)["ok"]
