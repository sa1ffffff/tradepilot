import numpy as np
import pandas as pd

from bot.strategy import generate_signal


def _frame(closes):
    n = len(closes)
    closes = np.array(closes, dtype=float)
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC"),
        "open": closes,
        "high": closes * 1.001,
        "low": closes * 0.999,
        "close": closes,
        "volume": np.ones(n),
    })


def test_buy_on_upward_cross():
    # flat baseline (EMAs equal) then a jump on the final bar -> fast crosses above slow
    closes = [100.0] * 60 + [130.0]
    sig = generate_signal(_frame(closes), fast=9, slow=21, atr_period=14)
    assert sig is not None and sig.action == "buy"
    assert sig.atr > 0


def test_sell_on_downward_cross():
    closes = [100.0] * 60 + [70.0]
    sig = generate_signal(_frame(closes), fast=9, slow=21, atr_period=14)
    assert sig is not None and sig.action == "sell"


def test_no_signal_without_cross():
    closes = list(np.linspace(100, 160, 80))  # steady uptrend, no cross on last bar
    sig = generate_signal(_frame(closes), fast=9, slow=21, atr_period=14)
    assert sig is None


def test_none_when_too_short():
    assert generate_signal(_frame([100, 101, 102]), 9, 21, 14) is None
