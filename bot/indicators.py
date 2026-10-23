"""Indicators, computed the way TradingView computes them (RMA-smoothed RSI and
ATR), so a strategy prototyped on a TradingView chart gives the same values here.
Every value at bar i uses only bars <= i -- no lookahead."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rma(s: pd.Series, n: int) -> pd.Series:
    """Wilder's moving average (TradingView ta.rma)."""
    return s.ewm(alpha=1 / n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = rma(delta.clip(lower=0), n)
    loss = rma(-delta.clip(upper=0), n)
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(100.0)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return rma(tr, n)


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    return mid - k * sd, mid, mid + k * sd


def supertrend_up(df: pd.DataFrame, n: int = 10, mult: float = 3.0) -> pd.Series:
    """True while Supertrend is in an uptrend (TradingView ta.supertrend)."""
    return supertrend(df, n, mult)[0]


def supertrend(df: pd.DataFrame, n: int = 10, mult: float = 3.0) -> tuple[pd.Series, pd.Series]:
    """(uptrend flag, the Supertrend line: the lower band in an uptrend, the upper in a downtrend)."""
    hl2 = ((df["high"] + df["low"]) / 2).to_numpy()
    a = atr(df, n).to_numpy()
    close = df["close"].to_numpy()
    upper = hl2 + mult * a
    lower = hl2 - mult * a
    up = np.ones(len(df), dtype=bool)
    for i in range(1, len(df)):
        if not (lower[i] > lower[i - 1] or close[i - 1] < lower[i - 1]):
            lower[i] = lower[i - 1]
        if not (upper[i] < upper[i - 1] or close[i - 1] > upper[i - 1]):
            upper[i] = upper[i - 1]
        if up[i - 1]:
            up[i] = close[i] >= lower[i]
        else:
            up[i] = close[i] > upper[i]
    line = np.where(up, lower, upper)
    return pd.Series(up, index=df.index), pd.Series(line, index=df.index)


def crossed_above(a: pd.Series, b) -> pd.Series:
    b_prev = b.shift(1) if isinstance(b, pd.Series) else b
    return (a > b) & (a.shift(1) <= b_prev)


def crossed_below(a: pd.Series, b) -> pd.Series:
    b_prev = b.shift(1) if isinstance(b, pd.Series) else b
    return (a < b) & (a.shift(1) >= b_prev)


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Wilder's ADX (TradingView ta.dmi): trend strength regardless of direction."""
    up = df["high"].diff()
    down = -df["low"].diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    a = atr(df, n)
    plus_di = 100 * rma(plus_dm, n) / a
    minus_di = 100 * rma(minus_dm, n) / a
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return rma(dx.fillna(0), n)


def chandelier_long(df: pd.DataFrame, n: int = 22, mult: float = 3.0) -> pd.Series:
    """Trailing stop level for longs: highest high of n bars minus mult x ATR(n)."""
    return df["high"].rolling(n).max() - mult * atr(df, n)
