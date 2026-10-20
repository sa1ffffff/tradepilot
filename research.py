"""Strategy research: which strategy, if any, has an edge out of sample?

For every symbol x timeframe x strategy it runs an anchored walk-forward test:

    history split into 5 equal segments  S0 S1 S2 S3 S4
    fold 1: pick params on S0        -> trade S1 with them
    fold 2: pick params on S0..S1    -> trade S2
    fold 3: pick params on S0..S2    -> trade S3
    fold 4: pick params on S0..S3    -> trade S4

Only the S1..S4 results (80% of the data, never seen when the params were
chosen) are reported. "auto" is the same process choosing among *all*
strategies each fold -- the honest estimate of what this research would do
for you going forward.

    python research.py                         # BTC+ETH, 15m/1h/4h, 365 days
    python research.py --symbols BTC/USDT --timeframes 1h --days 180
    python research.py --save                  # write the best passing strategy to strategy.json

Public candles only; no API keys, no account access.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

import pandas as pd

from config import Config
from bot.data import load_history
from bot.engine import metrics, simulate
from bot.strategies import STRATEGIES, grid, signals

FOLDS = 4
MIN_TRAIN_TRADES = 10


def score(trades) -> float:
    """t-statistic of per-trade returns: rewards consistency, not one lucky trade."""
    if len(trades) < MIN_TRAIN_TRADES:
        return float("-inf")
    s = pd.Series([t.ret_pct for t in trades])
    return float(s.mean() / s.std(ddof=1) * len(s) ** 0.5) if s.std(ddof=1) > 0 else float("-inf")


def pick(candidates, train_end_time):
    """Best spec by score on its trades that closed before train_end_time.
    candidates: (spec, trades over the full history) pairs."""
    best, best_score = None, float("-inf")
    for spec, full_trades in candidates:
        sc = score([t for t in full_trades if t.exit_time < train_end_time])
        if sc > best_score:
            best, best_score = spec, sc
    return best


def walk_forward(df: pd.DataFrame, candidates, cfg) -> dict:
    n = len(df)
    seg = n // (FOLDS + 1)
    equity = cfg.backtest_start_equity
    oos_trades, curve, folds = [], [], []
    for k in range(FOLDS):
        lo, hi = seg * (k + 1), (seg * (k + 2) if k < FOLDS - 1 else n)
        spec = pick(candidates, df["time"].iloc[lo])
        start_eq = equity
        if spec is None:
            curve += [equity] * (hi - lo)
            folds.append({"chosen": None, "return_pct": 0.0})
            continue
        sig = signals(df, spec)  # recomputed rather than kept: ~120 frames per dataset add up
        trades, c, equity = simulate(sig, spec, cfg, lo, hi, equity)
        oos_trades += trades
        curve += c
        folds.append({"chosen": spec.label(), "return_pct": round((equity / start_eq - 1) * 100, 2)})

    m = metrics(oos_trades, curve, cfg.backtest_start_equity, equity,
                float(df["close"].iloc[seg]), float(df["close"].iloc[-1]))
    m["folds_positive"] = sum(f["return_pct"] > 0 for f in folds)
    m["folds"] = folds
    m["verdict"] = verdict(m)
    return m


def verdict(m: dict) -> str:
    if m["trades"] < 30:
        return "too few trades"
    if m["total_return_pct"] > 0 and m["profit_factor"] >= 1.2 and m["folds_positive"] >= 3:
        return "CANDIDATE"
    return "no edge"


def research(cfg, symbols, timeframes, days, offline):
    rows = []
    for symbol in symbols:
        for tf in timeframes:
            df = load_history(cfg, symbol, tf, days, refresh=not offline)
            print(f"  {symbol} {tf}: {len(df)} bars "
                  f"{df['time'].iloc[0]:%Y-%m-%d} -> {df['time'].iloc[-1]:%Y-%m-%d}", flush=True)
            everything = []
            for name in STRATEGIES:
                cands = []
                for spec in grid(name):
                    cands.append((spec, simulate(signals(df, spec), spec, cfg)[0]))
                everything += cands
                rows.append({"symbol": symbol, "timeframe": tf, "strategy": name,
                             **walk_forward(df, cands, cfg), "_cands": cands, "_df": df})
            rows.append({"symbol": symbol, "timeframe": tf, "strategy": "auto",
                         **walk_forward(df, everything, cfg), "_cands": everything, "_df": df})
    return rows


COLS = [("symbol", 9), ("timeframe", 4), ("strategy", 19), ("trades", 6), ("win_rate_pct", 6),
        ("profit_factor", 6), ("avg_trade_pct", 7), ("total_return_pct", 8),
        ("max_drawdown_pct", 7), ("buy_hold_pct", 7), ("folds_positive", 5), ("verdict", 14)]
HEAD = ["symbol", "tf", "strategy", "trades", "win%", "PF", "avg%", "return%", "maxDD%",
        "B&H%", "folds+", "verdict"]


def table(rows) -> str:
    lines = ["  ".join(h.ljust(w) for h, (_, w) in zip(HEAD, COLS))]
    for r in rows:
        lines.append("  ".join(str(r[k]).ljust(w) for k, w in COLS))
    return "\n".join(lines)


def write_report(rows, args, cfg) -> str:
    os.makedirs("reports", exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    path = os.path.join("reports", f"research_{stamp}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Research run {stamp} UTC\n\n")
        f.write(f"{args.days} days, {FOLDS}-fold anchored walk-forward, fee {cfg.fee_rate:.2%}/side, "
                f"slippage {cfg.slippage_bps} bps/side, risk {cfg.risk_fraction:.1%}/trade. "
                "All figures are out-of-sample (last 80% of the period).\n\n")
        f.write("```\n" + table(rows) + "\n```\n\n## Parameters chosen per fold\n\n")
        for r in rows:
            f.write(f"- **{r['symbol']} {r['timeframe']} {r['strategy']}**: " +
                    "; ".join(f"{fd['chosen'] or 'nothing qualified'} -> {fd['return_pct']}%"
                              for fd in r["folds"]) + "\n")
    return path


def save_best(rows, cfg, force: bool) -> None:
    passing = [r for r in rows if r["verdict"] == "CANDIDATE" and r["strategy"] != "auto"]
    if not passing:
        if not force:
            print("\n  No strategy passed out of sample, so strategy.json was NOT written.\n"
                  "  (--save --force writes the best-scoring one anyway, for plumbing tests only.)")
            return
        passing = sorted((r for r in rows if r["strategy"] != "auto"),
                         key=lambda r: r["total_return_pct"], reverse=True)[:1]
    best = max(passing, key=lambda r: r["t_stat"])
    # final params: the same selection rule, now on the whole history
    spec = pick(best["_cands"], best["_df"]["time"].iloc[-1] + pd.Timedelta(days=1))
    out = {
        "symbol": best["symbol"], "timeframe": best["timeframe"], **spec.to_dict(),
        "evidence": {k: best[k] for k in ("trades", "win_rate_pct", "profit_factor",
                                          "total_return_pct", "max_drawdown_pct",
                                          "folds_positive", "verdict")},
        "researched": datetime.now(timezone.utc).isoformat(timespec="minutes"),
    }
    with open(cfg.strategy_file, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Wrote {cfg.strategy_file}: {best['symbol']} {best['timeframe']} {spec.label()}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbols", default="BTC/USDT,ETH/USDT")
    p.add_argument("--timeframes", default="15m,1h,4h")
    p.add_argument("--days", type=int, default=365)
    p.add_argument("--offline", action="store_true", help="use cached candles only")
    p.add_argument("--save", action="store_true", help="write the best passing strategy to strategy.json")
    p.add_argument("--force", action="store_true", help="with --save: write even if nothing passed")
    args = p.parse_args()
    cfg = Config()

    print(f"\n  Research: {args.days} days, walk-forward out-of-sample\n")
    rows = research(cfg, args.symbols.split(","), args.timeframes.split(","), args.days, args.offline)
    print("\n" + table(rows))
    print(f"\n  Report: {write_report(rows, args, cfg)}")
    if args.save:
        save_best(rows, cfg, args.force)


if __name__ == "__main__":
    main()
