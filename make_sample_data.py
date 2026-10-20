"""Generate synthetic OHLCV so the backtest runs with no network or API keys.

This is NOT real market data -- it only exists so you can run the backtest and
see the whole pipeline work end to end. For real results, fetch real candles
(see backtest.py --live).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd


def make(n: int = 1500, seed: int = 7, start_price: float = 60000.0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # a drifting random walk with a couple of regime changes, so EMAs actually cross
    drift = np.concatenate([
        np.full(n // 3, 0.0004),
        np.full(n // 3, -0.0005),
        np.full(n - 2 * (n // 3), 0.0003),
    ])
    rets = drift + rng.normal(0, 0.006, n)
    close = start_price * np.exp(np.cumsum(rets))

    high = close * (1 + rng.uniform(0, 0.004, n))
    low = close * (1 - rng.uniform(0, 0.004, n))
    open_ = np.concatenate([[start_price], close[:-1]])
    vol = rng.uniform(10, 100, n)
    times = pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC")

    return pd.DataFrame({
        "time": times, "open": open_, "high": high, "low": low,
        "close": close, "volume": vol,
    })


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = make()
    df.to_csv("data/sample_ohlcv.csv", index=False)
    print(f"wrote data/sample_ohlcv.csv ({len(df)} bars)")
