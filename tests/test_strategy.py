import numpy as np
import pandas as pd
import pytest

from bot import indicators as ind
from bot.strategies import STRATEGIES, StrategySpec, default_spec, grid, signals


def frame(closes, spread=0.001):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC"),
        "open": closes, "high": closes * (1 + spread), "low": closes * (1 - spread),
        "close": closes, "volume": np.ones(n),
    })


def random_walk(n=1500, seed=1):
    rng = np.random.default_rng(seed)
    return frame(100 * np.exp(np.cumsum(rng.normal(0, 0.01, n))), spread=0.004)


def test_ema_cross_buy_and_sell():
    up = signals(frame([100.0] * 80 + [130.0]), default_spec())
    assert up["entry"].iloc[-1] and not up["exit"].iloc[-1]
    down = signals(frame([100.0] * 80 + [70.0]), default_spec())
    assert down["exit"].iloc[-1] and not down["entry"].iloc[-1]


def test_no_entry_during_warmup():
    sig = signals(frame([100.0] * 20 + [130.0]), default_spec())
    assert not sig["entry"].any()


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_every_strategy_runs_and_is_causal(name):
    """Signals at bar i must not change when future bars are appended."""
    df = random_walk()
    for spec in grid(name)[:4]:
        full = signals(df, spec)
        cut = signals(df.iloc[:1000], spec)
        assert full["entry"].iloc[:1000].equals(cut["entry"])
        assert full["exit"].iloc[:1000].equals(cut["exit"])


def test_rsi_bounds_and_atr_positive():
    df = random_walk()
    r = ind.rsi(df["close"])
    assert r.between(0, 100).all()
    assert (ind.atr(df).iloc[20:] > 0).all()


def test_spec_roundtrip_and_unknown_name():
    spec = StrategySpec("trend_pullback", {"trend": 200, "rsi_entry": 40, "rsi_exit": 70}, 2.5, 2.0)
    assert StrategySpec.from_dict(spec.to_dict()) == spec
    with pytest.raises(ValueError):
        StrategySpec.from_dict({"name": "nope"})
