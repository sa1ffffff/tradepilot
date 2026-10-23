"""SiGen journal: signals are logged once, as issued, and judged by their own plan."""
import numpy as np
import pandas as pd

from bot import sigen, sigen_journal as j
from bot.strategies import STRATEGIES, StrategySpec

SPEC = StrategySpec("donchian_breakout", dict(STRATEGIES["donchian_breakout"].defaults), 2.0, 2.0).to_dict()


def _df(after: list[float], flat: int = 400) -> pd.DataFrame:
    close = np.r_[np.full(flat, 100.0), after]
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=len(close), freq="4h", tz="UTC"),
                         "open": close, "high": close * 1.004, "low": close * 0.996, "close": close,
                         "volume": np.ones(len(close))})


def _rec(df, **kw) -> dict:
    t = df["time"].iloc[399]
    rec = {"id": "x", "market": "spot", "coin": "TST", "symbol": "TST/USDT", "direction": "long", "spec": SPEC,
           "entry_bar": t.isoformat(), "valid_from": (t + j.BAR).isoformat(), "valid_until": (t + 2 * j.BAR).isoformat(),
           "entry": 100.0, "stop": 98.0, "target": 104.0, "chase_limit": 100.6}
    return {**rec, **kw}


def test_target_hit_is_correct():
    df = _df([100.5, 101.5, 102.5, 103.5, 104.0, 105.0])
    o = j.follow(_rec(df), df, sigen.configs()["spot"])
    assert o["status"] == "won" and o["exit_reason"] == "tp" and o["result_r"] == 2.0
    assert o["entry_window"] == {"next_open": 100.5, "enterable": True} and o["mfe_r"] == 2.0


def test_exit_rule_and_stop_make_it_wrong():
    df = _df([99.0, 98.0, 97.0])   # the 20-bar-low exit fires on the first close below the range
    o = j.follow(_rec(df), df, sigen.configs()["spot"])
    assert o["status"] == "lost" and o["exit_reason"] == "signal" and o["result_r"] == -0.5
    gap = _df([96.0])              # opens straight through the stop: filled at the open, worse than -1R
    o = j.follow(_rec(gap), gap, sigen.configs()["spot"])
    assert o["exit_reason"] == "stop" and o["result_r"] == -2.0


def test_short_signal_and_still_open():
    df = _df([99.3, 99.9, 99.7])
    o = j.follow(_rec(df, direction="short", stop=102.0, target=96.0, chase_limit=99.4), df, sigen.configs()["spot"])
    assert o["status"] == "open" and o["bars_held"] == 3 and o["r_now"] > 0
    assert o["entry_window"]["enterable"] is False   # the next candle opened past the chase limit


def _sig(state="entry", bar="2026-03-01T00:00:00+00:00"):
    return {"state": state, "market": "futures", "coin": "TST", "symbol": "TST/USDT:USDT", "direction": "long",
            "strategy": "donchian_breakout", "label": "x", "spec": SPEC, "timeframe": "4h", "entry_bar": bar,
            "signal_time": bar, "valid_from": bar, "valid_until": bar, "entry": 100.0, "stop": 98.0,
            "initial_stop": 98.0, "target": None, "chase_limit": 100.6, "trail": None, "exit_rule": "x",
            "instruction": "Go long", "rule": "r", "confidence": {"score": 70, "label": "Medium"},
            "accuracy": {"win_rate_pct": 40.0, "expected_win_rate_pct": 41.0, "trades": 50, "profit_factor": 1.5}}


def test_signals_are_logged_once_and_late_ones_are_marked(tmp_path):
    root = str(tmp_path)
    assert j.record([_sig(), _sig("armed", "2026-03-02T00:00:00+00:00")], root) == ["futures:TST:2026-03-01T00:00:00+00:00:long"]
    assert j.record([_sig()], root) == []                      # same signal on a later page load
    j.record([_sig("holding", "2026-03-03T00:00:00+00:00")], root)
    recs = j.load(root)
    late = recs["futures:TST:2026-03-03T00:00:00+00:00:long"]
    assert late["late"] and late["valid_from"] == "2026-03-03T04:00:00+00:00"
    assert not recs["futures:TST:2026-03-01T00:00:00+00:00:long"]["late"]


def test_summary_and_csv():
    rows = [{"source": "live", "outcome": {"status": s, "verdict": j.VERDICT[s], "result_r": r},
             "tested": {"win_rate_pct": 40.0}} for s, r in (("won", 2.0), ("lost", -1.0), ("lost", -1.0))]
    s = j.summary(rows)["live"]
    assert s["closed"] == 3 and s["win_rate_pct"] == 33.3 and s["total_r"] == 0.0 and s["tested_win_rate_pct"] == 40.0
    df = _df([100.5 + k for k in range(10)])
    rec = {**_rec(df), "source": "live", "late": False, "strategy": "donchian_breakout",
           "confidence": {"score": 70}, "tested": {"win_rate_pct": 40.0}}
    rec["outcome"] = {**j.follow(rec, df, sigen.configs()["spot"]), "verdict": "Correct"}
    text = j.to_csv([rec])
    assert text.splitlines()[0].startswith("id,source") and "Correct" in text and ",tp," in text
