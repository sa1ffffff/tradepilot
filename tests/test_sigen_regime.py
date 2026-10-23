"""SiGen regime filter: chop measures, who gets held back, and the switch-on rule."""
import numpy as np
import pandas as pd

from bot import sigen, sigen_regime as g
from tests.test_sigen import _samples, _scan_result


def _df(close):
    close = np.asarray(close, float)
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=len(close), freq="4h", tz="UTC"),
                         "open": close, "high": close * 1.002, "low": close * 0.998, "close": close,
                         "volume": np.ones(len(close))})


def test_efficiency_ratio_tells_trend_from_chop():
    trend = g.efficiency(pd.Series(np.arange(100, 200, dtype=float)), 30).iloc[-1]
    chop = g.efficiency(pd.Series(100 + np.tile([0.0, 1.0], 50)), 30).iloc[-1]
    assert trend == 1.0 and chop < 0.05
    c_trend = g.choppiness(_df(np.arange(100, 200))).iloc[-1]
    c_chop = g.choppiness(_df(100 + np.tile([0.0, 1.0], 50))).iloc[-1]
    assert c_chop > 61.8 > 38.2 > c_trend


def test_only_trend_strategies_in_chop_are_held_back():
    chop = _df(100 + np.tile([0.0, 1.0, 0.5, 1.5], 150))
    rule = {"measure": "er_30", "side": "below", "threshold": 0.2}
    on, shadow = {"mode": "on", "rule": rule}, {"mode": "shadow", "rule": rule}
    assert g.at(chop, len(chop) - 1, "donchian_breakout", on)["held_back"]
    assert not g.at(chop, len(chop) - 1, "bollinger_reversion", on)["would_hold"]   # reversion wants chop
    s = g.at(chop, len(chop) - 1, "supertrend", shadow)
    assert s["would_hold"] and not s["held_back"]                                   # trial tags, never blocks
    assert not g.is_choppy({"er_30": None}, rule)                                   # missing data: let it through


def test_filter_on_turns_entries_into_held_signals():
    model = sigen.Model(sigen.Model.train(_samples(1500)).d)
    res = _scan_result("futures")
    rule = {"measure": "er_30", "side": "below", "threshold": 2.0}   # everything counts as choppy
    seen = set()
    for cut in (700, 820, 950, 1100, 1199):
        from tests.test_console import _frame
        df = _frame(1200).iloc[:cut + 1].reset_index(drop=True)
        plain = sigen.signal_for(res, model, df, sigen.configs()["futures"])
        held = sigen.signal_for(res, model, df, sigen.configs()["futures"], {"mode": "on", "rule": rule})
        if plain["state"] in ("entry", "armed"):
            assert held["state"] == "held" and held["instruction"].startswith("Skip this one")
            seen.add(plain["state"])
        else:
            assert held["state"] == plain["state"]
    assert seen


def test_switch_on_needs_every_check():
    rows = []
    rng = np.random.default_rng(2)
    t0 = pd.Timestamp("2024-01-01", tz="UTC")
    for k in range(2000):   # choppy entries are worse in both halves: the filter should pass
        er = rng.uniform(0, 0.6)
        rows.append({"market": "futures", "coin": "X", "strategy": "supertrend", "trend": True,
                     "time": t0 + pd.Timedelta(hours=4 * k), "side": "long",
                     "R": rng.normal(-0.4 if er < 0.15 else 0.3, 1.0), "er_30": er, "er_60": er,
                     "chop_14": 50.0, "adx_14": 25.0})
    h = pd.DataFrame(rows)
    cut = h["time"].iloc[int(len(h) * g.CALIBRATE)]
    best, _ = g.calibrate(h[h["time"] < cut])
    assert best["measure"].startswith("er") and best["gain_r"] > 0
    val = h[h["time"] >= cut]
    drop = g.held(val, best)
    assert val["R"][~drop].mean() - val["R"].mean() >= g.MIN_GAIN_R and g.luck(val, drop, n=500) >= g.LUCK
