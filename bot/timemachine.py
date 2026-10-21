"""The Time Machine: replays a strategy's honest track record thousands of times
to show the range of outcomes it can produce, before (and while) it trades.

Read-only analysis. It never talks to an account and nothing in the trading
bots imports it.

Inputs are out-of-sample trades: the walk-forward trades from research.py,
never trades from parameters fitted on the same data. Each trade is reduced to
its R multiple (P&L / amount risked), so the replay can be run at any risk per
trade: a trade of R changes equity by risk_fraction x R.

Two replays:
- trade bootstrap (one strategy): draw the next N trades at random, with
  replacement, from the strategy's own history;
- month bootstrap (portfolio): draw whole calendar months, taking every
  strategy's trades from that month together. Crypto coins tend to crash
  together; resampling months keeps that, where shuffling each coin's trades
  separately would make a portfolio look safer than it is.
Neither models the live bot's margin cap or daily loss limit, which would
skip some trades in busy periods.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Replay:
    final: np.ndarray        # equity multiple after the horizon, per path
    max_dd: np.ndarray       # worst peak-to-trough drop, as a positive fraction
    streak: np.ndarray       # longest run of losing trades
    trades: np.ndarray       # trades taken per path


def _walk(r_paths: list[np.ndarray], risk: float) -> Replay:
    n = len(r_paths)
    final, max_dd = np.ones(n), np.zeros(n)
    streak, count = np.zeros(n, dtype=int), np.zeros(n, dtype=int)
    for i, rs in enumerate(r_paths):
        eq = np.cumprod(1 + risk * np.clip(rs, -1 / risk, None))  # can't lose more than everything
        curve = np.concatenate([[1.0], eq])
        peak = np.maximum.accumulate(curve)
        final[i] = curve[-1]
        max_dd[i] = float(((peak - curve) / peak).max())
        run = best = 0
        for r in rs:
            run = run + 1 if r < 0 else 0
            best = max(best, run)
        streak[i], count[i] = best, len(rs)
    return Replay(final, max_dd, streak, count)


def trade_bootstrap(r: np.ndarray, n_trades: int, risk: float, paths: int = 10_000,
                    seed: int = 19) -> Replay:
    """The next n_trades drawn with replacement from r, `paths` times."""
    rng = np.random.default_rng(seed)
    if len(r) == 0 or n_trades == 0:
        return _walk([np.array([])] * paths, risk)
    draws = rng.choice(r, size=(paths, n_trades), replace=True)
    return _walk(list(draws), risk)


def month_bootstrap(month_trades: list[np.ndarray], months: int, risk: float,
                    paths: int = 10_000, seed: int = 19) -> Replay:
    """Each path strings together `months` historical months drawn with
    replacement; a month brings every strategy's trades from that month, in
    the order they closed."""
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(month_trades), size=(paths, months))
    return _walk([np.concatenate([month_trades[m] for m in row]) for row in picks], risk)


def months_of(trades_by_strategy: dict[str, list]) -> list[np.ndarray]:
    """All strategies' R multiples grouped by the calendar month they closed in,
    ordered by close time within a month; months with no trades included."""
    rows = [(t.exit_time, t.R) for ts in trades_by_strategy.values() for t in ts]
    if not rows:
        return [np.array([])]
    df = pd.DataFrame(rows, columns=["time", "R"]).sort_values("time")
    month = df["time"].dt.tz_localize(None).dt.to_period("M")
    span = pd.period_range(month.min(), month.max(), freq="M")
    groups = {p: g["R"].to_numpy() for p, g in df.groupby(month)}
    return [groups.get(p, np.array([])) for p in span]


def summary(rep: Replay) -> dict:
    ret = (rep.final - 1) * 100
    return {
        "median_return_pct": round(float(np.median(ret)), 1),
        "bad_case_return_pct": round(float(np.percentile(ret, 5)), 1),     # 1 path in 20 is worse
        "good_case_return_pct": round(float(np.percentile(ret, 95)), 1),
        "p_loss_pct": round(float((rep.final < 1).mean() * 100), 1),
        "median_max_dd_pct": round(float(np.median(rep.max_dd) * 100), 1),
        "bad_max_dd_pct": round(float(np.percentile(rep.max_dd, 95) * 100), 1),
        "p_dd_over_20_pct": round(float((rep.max_dd > 0.20).mean() * 100), 1),
        "p_dd_over_35_pct": round(float((rep.max_dd > 0.35).mean() * 100), 1),
        "bad_losing_streak": int(np.percentile(rep.streak, 95)),
        "median_trades": int(np.median(rep.trades)),
    }


def trade_odds(trades: list) -> dict:
    """How this strategy's trades have ended: what to expect from the next one."""
    if not trades:
        return {"trades": 0}
    r = np.array([t.R for t in trades])
    reasons = pd.Series([t.reason for t in trades])
    share = lambda k: round(float((reasons == k).mean() * 100), 1)  # noqa: E731
    return {
        "trades": len(trades),
        "win_pct": round(float((r > 0).mean() * 100), 1),
        "stop_pct": share("stop"),
        "tp_pct": share("tp"),
        "signal_pct": share("signal"),
        "avg_R": round(float(r.mean()), 2),
        "median_R": round(float(np.median(r)), 2),
        "avg_win_R": round(float(r[r > 0].mean()), 2) if (r > 0).any() else 0.0,
        "avg_loss_R": round(float(r[r < 0].mean()), 2) if (r < 0).any() else 0.0,
        "worst_R": round(float(r.min()), 2),
    }
