"""Long-only spot strategies.

Each strategy maps closed candles + parameters to two boolean columns:
`entry` (go long at this bar's close if flat) and `exit` (close the long at
this bar's close). Stops and take-profits are not part of a strategy; the
engine applies them from the `stop_atr` / `tp_r` settings, identically in the
backtest and the live bot.

The research tool, the backtest and the live runner all call `signals()`, so
what is tested is exactly what trades.
"""
from __future__ import annotations

import dataclasses
import itertools
from dataclasses import dataclass, field

import pandas as pd

from bot import indicators as ind

ATR_PERIOD = 14


def _ema_cross(df, fast, slow):
    f, s = ind.ema(df["close"], fast), ind.ema(df["close"], slow)
    return ind.crossed_above(f, s), ind.crossed_below(f, s), slow * 3


def _trend_pullback(df, trend, rsi_entry, rsi_exit):
    """Uptrend (close above a long EMA) + RSI dipping and recovering through
    rsi_entry. Exit on RSI strength or when the trend breaks."""
    t = ind.ema(df["close"], trend)
    r = ind.rsi(df["close"], 14)
    entry = (df["close"] > t) & ind.crossed_above(r, rsi_entry)
    exit_ = (r > rsi_exit) | (df["close"] < t)
    return entry, exit_, trend * 3


def _donchian_breakout(df, entry_n, exit_n, trend):
    """Close breaks the prior entry_n-bar high in an uptrend; exit on a break
    of the prior exit_n-bar low (classic turtle rules, long side)."""
    hi = df["high"].rolling(entry_n).max().shift(1)
    lo = df["low"].rolling(exit_n).min().shift(1)
    entry = df["close"] > hi
    if trend:
        entry &= df["close"] > ind.ema(df["close"], trend)
    return entry, df["close"] < lo, max(entry_n, trend * 3)


def _bollinger_reversion(df, k, trend):
    """Close falls below the lower band then closes back inside it; exit at
    the middle band."""
    lower, mid, _ = ind.bollinger(df["close"], 20, k)
    entry = ind.crossed_above(df["close"], lower)
    if trend:
        entry &= df["close"] > ind.ema(df["close"], trend)
    return entry, df["close"] >= mid, max(20, trend * 3)


def _supertrend(df, mult, trend):
    up = ind.supertrend_up(df, 10, mult)
    entry = up & ~up.shift(1, fill_value=False)
    if trend:
        entry &= df["close"] > ind.ema(df["close"], trend)
    return entry, ~up, max(30, trend * 3)


# --- cost-aware variants for 1h/4h ----------------------------------------
# Fewer, longer trades: a slow higher-timeframe trend filter, an ADX trend-strength
# gate so chop is skipped, and exits that let winners run. Each trade then risks
# more relative to the fixed per-trade fee.

def _ema_cross_adx(df, fast, slow, adx_min):
    f, s = ind.ema(df["close"], fast), ind.ema(df["close"], slow)
    entry = ind.crossed_above(f, s) & (ind.adx(df) > adx_min)
    return entry, ind.crossed_below(f, s), slow * 3


def _breakout_htf(df, entry_n, trend):
    """Donchian breakout only in a long-horizon uptrend with a trending ADX;
    exit on a break of the prior 20-bar low."""
    hi = df["high"].rolling(entry_n).max().shift(1)
    lo = df["low"].rolling(20).min().shift(1)
    entry = (df["close"] > hi) & (df["close"] > ind.ema(df["close"], trend)) & (ind.adx(df) > 20)
    return entry, df["close"] < lo, trend * 2


def _pullback_htf(df, trend, rsi_entry):
    """Buy an RSI dip recovering through rsi_entry while price holds above both a
    long-horizon and a 50-bar EMA; exit on RSI > 75 or loss of the long trend."""
    t = ind.ema(df["close"], trend)
    r = ind.rsi(df["close"], 14)
    entry = (df["close"] > t) & (df["close"] > ind.ema(df["close"], 50)) & ind.crossed_above(r, rsi_entry)
    return entry, (r > 75) | (df["close"] < t), trend * 2


def _chandelier_trend(df, trend, mult):
    """Enter when price reclaims a trend EMA with ADX confirming; trail out with
    a chandelier exit so the trade can run."""
    t = ind.ema(df["close"], trend)
    entry = ind.crossed_above(df["close"], t) & (ind.adx(df) > 20)
    return entry, df["close"] < ind.chandelier_long(df, 22, mult), trend * 2


@dataclass(frozen=True)
class StrategyDef:
    fn: object
    grid: dict          # signal parameters to search
    defaults: dict
    risk_grid: dict = field(default_factory=lambda: {"stop_atr": [2.0, 3.0], "tp_r": [None, 3.0]})


STRATEGIES: dict[str, StrategyDef] = {
    "ema_cross": StrategyDef(
        _ema_cross,
        {"fast": [9, 20], "slow": [21, 50, 100]},
        {"fast": 9, "slow": 21},
    ),
    "trend_pullback": StrategyDef(
        _trend_pullback,
        {"trend": [100, 200], "rsi_entry": [30, 40], "rsi_exit": [65, 75]},
        {"trend": 200, "rsi_entry": 40, "rsi_exit": 70},
    ),
    "donchian_breakout": StrategyDef(
        _donchian_breakout,
        {"entry_n": [20, 55], "exit_n": [10, 20], "trend": [0, 200]},
        {"entry_n": 20, "exit_n": 10, "trend": 200},
    ),
    "bollinger_reversion": StrategyDef(
        _bollinger_reversion,
        {"k": [2.0, 2.5], "trend": [0, 200]},
        {"k": 2.0, "trend": 200},
    ),
    "supertrend": StrategyDef(
        _supertrend,
        {"mult": [2.0, 3.0], "trend": [0, 200]},
        {"mult": 3.0, "trend": 0},
    ),
    "ema_cross_adx": StrategyDef(
        _ema_cross_adx,
        {"fast": [20], "slow": [50, 100], "adx_min": [20, 25]},
        {"fast": 20, "slow": 50, "adx_min": 20},
    ),
    "breakout_htf": StrategyDef(
        _breakout_htf,
        {"entry_n": [20, 55], "trend": [400, 800]},
        {"entry_n": 55, "trend": 400},
    ),
    "pullback_htf": StrategyDef(
        _pullback_htf,
        {"trend": [400, 800], "rsi_entry": [35, 45]},
        {"trend": 400, "rsi_entry": 40},
    ),
    "chandelier_trend": StrategyDef(
        _chandelier_trend,
        {"trend": [100, 200], "mult": [2.5, 3.5]},
        {"trend": 200, "mult": 3.0},
    ),
}


@dataclass(frozen=True)
class StrategySpec:
    """A fully specified strategy: what research saves and the bot runs."""
    name: str
    params: dict
    stop_atr: float = 2.0
    tp_r: float | None = None
    shorts: bool = False      # futures only: also trade the mirrored short signals

    def to_dict(self) -> dict:
        return {"name": self.name, "params": self.params, "stop_atr": self.stop_atr, "tp_r": self.tp_r,
                "shorts": self.shorts}

    @classmethod
    def from_dict(cls, d: dict) -> "StrategySpec":
        if d["name"] not in STRATEGIES:
            raise ValueError(f"unknown strategy {d['name']!r}; known: {', '.join(STRATEGIES)}")
        return cls(d["name"], dict(d.get("params", {})), float(d.get("stop_atr", 2.0)), d.get("tp_r"),
                   bool(d.get("shorts", False)))

    def label(self) -> str:
        p = ",".join(f"{k}={v}" for k, v in self.params.items())
        tp = f"tp={self.tp_r}R" if self.tp_r else "no tp"
        return f"{self.name}({p}) stop={self.stop_atr}ATR {tp}" + (" +shorts" if self.shorts else "")


def default_spec() -> StrategySpec:
    return StrategySpec("ema_cross", dict(STRATEGIES["ema_cross"].defaults), 2.0, None)


def signals(df: pd.DataFrame, spec: StrategySpec) -> pd.DataFrame:
    """Return df with entry, exit and atr columns. Entries are suppressed
    during indicator warm-up."""
    entry, exit_, warmup = STRATEGIES[spec.name].fn(df, **spec.params)
    out = df.copy()
    out["atr"] = ind.atr(df, ATR_PERIOD)
    ok = pd.Series(range(len(df)), index=df.index) >= warmup
    out["entry"] = (entry.fillna(False) & ok).astype(bool)
    out["exit"] = exit_.fillna(False).astype(bool)
    return out


def invert(df: pd.DataFrame) -> pd.DataFrame:
    """The chart upside down: price -> 1/price, highs and lows swapped. A rule's
    long signals on this chart are its short signals on the real one (a breakout
    becomes a breakdown, a trend filter flips, a trailing stop moves above price),
    without a second set of parameters to tune."""
    out = df.copy()
    out["open"], out["close"] = 1 / df["open"], 1 / df["close"]
    out["high"], out["low"] = 1 / df["low"], 1 / df["high"]
    return out


def signals_ls(df: pd.DataFrame, spec: StrategySpec) -> pd.DataFrame:
    """signals() plus short_entry / short_exit columns (all False unless spec.shorts)."""
    out = signals(df, spec)
    if spec.shorts:
        inv = signals(invert(df), spec)
        out["short_entry"] = inv["entry"].to_numpy()
        out["short_exit"] = inv["exit"].to_numpy()
    else:
        out["short_entry"] = False
        out["short_exit"] = False
    return out


def warmup_bars(spec: StrategySpec) -> int:
    """Bars the live bot must fetch so indicators match the backtest."""
    return max(int(v) for v in list(spec.params.values()) + [50] if isinstance(v, (int, float))) * 3 + 50


def grid_ls(name: str) -> list[StrategySpec]:
    """Futures grid: every spec long-only and long+short."""
    return [dataclasses.replace(s, shorts=sh) for s in grid(name) for sh in (False, True)]


def grid(name: str) -> list[StrategySpec]:
    s = STRATEGIES[name]
    keys = list(s.grid) + list(s.risk_grid)
    values = list(s.grid.values()) + list(s.risk_grid.values())
    specs = []
    for combo in itertools.product(*values):
        p = dict(zip(keys, combo))
        if name == "ema_cross" and p["fast"] >= p["slow"]:
            continue
        stop, tp = p.pop("stop_atr"), p.pop("tp_r")
        specs.append(StrategySpec(name, p, stop, tp))
    return specs
