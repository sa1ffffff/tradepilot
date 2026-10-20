"""Bar-by-bar simulation of a strategy, shared by backtest.py and research.py.

Execution model (kept identical to the live runner):
- signals are read at a bar's close and filled at that close;
- entries, signal exits and take-profits pay bot.costs.passive_cost (maker
  limit with market fallback); stop exits pay taker fee + slippage;
- the stop and take-profit rest from the bar after entry; if a bar opens
  through them the fill is the open; if one bar touches both, the stop wins;
- entries whose stop is too tight for the costs are skipped (MAX_COST_PER_R);
- size = risk_fraction of equity against the stop, capped at available cash.
The live bot's daily loss limit and $ notional cap are not applied here, so
results measure the strategy itself.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from bot.costs import passive_cost, taker_cost, too_costly
from bot.risk import position_size
from bot.strategies import StrategySpec, signals


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry: float
    exit: float
    size: float
    pnl: float
    ret_pct: float      # pnl as % of equity at entry
    R: float            # pnl / amount risked
    reason: str         # signal | stop | tp | end


def simulate(sig: pd.DataFrame, spec: StrategySpec, cfg, start: int = 0, end: int | None = None,
             equity: float | None = None) -> tuple[list[Trade], list[float], float]:
    """Run over bars [start, end) of a frame produced by strategies.signals()."""
    end = len(sig) if end is None else end
    equity = cfg.backtest_start_equity if equity is None else equity
    t = sig["time"].to_numpy()
    o, h, l, c = (sig[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    a = sig["atr"].to_numpy(dtype=float)
    ent, ex = sig["entry"].to_numpy(), sig["exit"].to_numpy()
    passive, urgent = passive_cost(cfg), taker_cost(cfg)

    trades: list[Trade] = []
    curve: list[float] = []
    pos = None

    def close(i: int, px: float, reason: str) -> None:
        nonlocal equity, pos
        proceeds = pos["size"] * px * (1 - (urgent if reason == "stop" else passive))
        equity += proceeds
        pnl = proceeds - pos["cost"]
        trades.append(Trade(pd.Timestamp(pos["time"]), pd.Timestamp(t[i]), pos["entry"], px,
                            pos["size"], pnl, 100 * pnl / pos["equity"],
                            pnl / pos["risk"] if pos["risk"] else 0.0, reason))
        pos = None

    for i in range(start, end):
        if pos is not None:
            if l[i] <= pos["stop"]:
                close(i, min(o[i], pos["stop"]), "stop")
            elif pos["tp"] is not None and h[i] >= pos["tp"]:
                close(i, max(o[i], pos["tp"]), "tp")

        if pos is not None and ex[i]:
            close(i, c[i], "signal")
        elif pos is None and ent[i] and a[i] > 0:
            px = c[i]
            dist = spec.stop_atr * a[i]
            if dist < px and not too_costly(cfg, px, dist):
                size = position_size(equity, px, dist, cfg.risk_fraction, float("inf"), urgent)
                cost = size * px * (1 + passive)
                pos = {"time": t[i], "entry": px, "size": size, "cost": cost, "equity": equity,
                       "risk": size * dist, "stop": px - dist,
                       "tp": px + spec.tp_r * dist if spec.tp_r else None}
                equity -= cost

        curve.append(equity + (pos["size"] * c[i] * (1 - passive) if pos else 0.0))

    if pos is not None:
        close(end - 1, c[end - 1], "end")
        curve[-1] = equity
    return trades, curve, equity


def run(df: pd.DataFrame, spec: StrategySpec, cfg) -> tuple[list[Trade], list[float], float]:
    return simulate(signals(df, spec), spec, cfg)


def metrics(trades: list[Trade], curve: list[float], start_equity: float, end_equity: float,
            first_close: float, last_close: float) -> dict:
    curve_arr = np.array(curve) if curve else np.array([start_equity])
    peak = np.maximum.accumulate(curve_arr)
    rets = np.array([tr.ret_pct for tr in trades])
    wins = rets[rets > 0]
    gross_loss = -sum(tr.pnl for tr in trades if tr.pnl < 0)
    gross_win = sum(tr.pnl for tr in trades if tr.pnl > 0)
    return {
        "trades": len(trades),
        "stopped_out": sum(tr.reason == "stop" for tr in trades),
        "win_rate_pct": round(100 * len(wins) / len(trades), 1) if trades else 0.0,
        "avg_trade_pct": round(float(rets.mean()), 3) if trades else 0.0,
        "avg_R": round(float(np.mean([tr.R for tr in trades])), 3) if trades else 0.0,
        "profit_factor": round(gross_win / gross_loss, 2) if gross_loss else (float("inf") if gross_win else 0.0),
        "t_stat": round(float(rets.mean() / rets.std(ddof=1) * np.sqrt(len(rets))), 2)
                  if len(rets) > 1 and rets.std(ddof=1) > 0 else 0.0,
        "total_return_pct": round((end_equity / start_equity - 1) * 100, 2),
        "max_drawdown_pct": round(float(((curve_arr - peak) / peak).min() * 100), 2),
        "buy_hold_pct": round((last_close / first_close - 1) * 100, 2),
        "final_equity": round(end_equity, 2),
    }
