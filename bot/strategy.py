"""Signal generation: EMA crossover with an ATR-based stop distance.

The strategy is deliberately simple and deterministic. It is the thing you
will replace or refine later; everything around it (risk, execution) stays
the same. Signals are only ever read off *closed* bars -- the caller is
responsible for not passing the still-forming candle.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Signal:
    action: str          # "buy" or "sell"
    time: pd.Timestamp   # close time of the bar that produced it
    price: float         # close of that bar
    atr: float           # ATR at that bar, for stop sizing


def add_indicators(df: pd.DataFrame, fast: int, slow: int, atr_period: int) -> pd.DataFrame:
    """Return a copy of df with ema_fast, ema_slow and atr columns."""
    out = df.copy()
    out["ema_fast"] = out["close"].ewm(span=fast, adjust=False).mean()
    out["ema_slow"] = out["close"].ewm(span=slow, adjust=False).mean()

    prev_close = out["close"].shift(1)
    true_range = pd.concat([
        out["high"] - out["low"],
        (out["high"] - prev_close).abs(),
        (out["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    out["atr"] = true_range.rolling(atr_period).mean()
    return out


def cross(prev: pd.Series, last: pd.Series) -> str | None:
    """'buy' if the fast EMA crossed above the slow one between prev and last,
    'sell' if it crossed below, else None. Shared by the live bot and the backtest
    so the two can never disagree about what a signal is."""
    if prev["ema_fast"] <= prev["ema_slow"] and last["ema_fast"] > last["ema_slow"]:
        return "buy"
    if prev["ema_fast"] >= prev["ema_slow"] and last["ema_fast"] < last["ema_slow"]:
        return "sell"
    return None


def generate_signal(df: pd.DataFrame, fast: int, slow: int, atr_period: int) -> Signal | None:
    """Look for an EMA cross between the last two closed bars.

    Expects df to contain only closed bars. Returns a Signal on the bar where
    the fast EMA crosses the slow EMA, otherwise None.
    """
    if len(df) < slow + atr_period + 2:
        return None

    d = add_indicators(df, fast, slow, atr_period)
    prev, last = d.iloc[-2], d.iloc[-1]

    if pd.isna(last["atr"]):
        return None

    action = cross(prev, last)
    if action is None:
        return None

    return Signal(
        action=action,
        time=last["time"],
        price=float(last["close"]),
        atr=float(last["atr"]),
    )
