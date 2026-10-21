"""The Time Machine: how could the next year go for the strategies the bot runs?

    python timemachine.py                      # the futures strategies in FUT_STRATEGY_FILE
    python timemachine.py --months 6 --risk 0.01
    python timemachine.py --files strategies/supertrend_ada_4h_swap.json

For each strategy it re-runs the walk-forward test (research.py) to get its
out-of-sample trades, then replays the next --months 10,000 times:
- per strategy, by drawing its trades at random;
- for the whole portfolio, by drawing whole historical months for all coins
  at once, so coins that crash together still crash together.
Also shows how the strategy's trades have ended (stop, target, exit signal),
which is what to expect from the next one.

Read-only: cached public candles, no account access, no orders, and nothing in
the trading bots imports it. The results are a reality check built from the
past, not a forecast.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
from datetime import datetime, timezone

import numpy as np

from config import Config
from bot.data import load_history
from bot.engine import simulate, simulate_ls
from bot.futures import futures_cfg
from bot.futures_runner import load_futures_strategy
from bot.runner import load_strategy
from bot.strategies import grid, grid_ls, signals, signals_ls
from bot.timemachine import month_bootstrap, months_of, summary, trade_bootstrap, trade_odds
from research import FOLDS, walk_forward


def oos_trades(path: str, base: Config, days: int, refresh: bool):
    """(label, out-of-sample trades, years they cover) for one strategy file."""
    with open(path, encoding="utf-8") as f:
        swap = ":" in json.load(f).get("symbol", "")
    if swap:
        cfg, spec = load_futures_strategy(futures_cfg(base), path)
        sig_fn, sim_fn, grid_fn, market = signals_ls, simulate_ls, grid_ls, "swap"
    else:
        cfg, spec = load_strategy(dataclasses.replace(base, strategy_file=path))
        sig_fn, sim_fn, grid_fn, market = signals, simulate, grid, "spot"
    try:
        df = load_history(cfg, cfg.symbol, cfg.timeframe, days, refresh=refresh)
    except SystemExit:  # not cached yet
        df = load_history(cfg, cfg.symbol, cfg.timeframe, days, refresh=True)
    cands = [(s, sim_fn(sig_fn(df, s), s, cfg)[0]) for s in grid_fn(spec.name)]
    trades = walk_forward(df, cands, cfg, market)["_trades"]
    oos = df["time"].iloc[len(df) // (FOLDS + 1):]
    years = (oos.iloc[-1] - oos.iloc[0]).days / 365
    return f"{cfg.symbol.split('/')[0]} {cfg.timeframe} {spec.name}", trades, years


ROW = "{:28} {:>6} {:>9} {:>9} {:>8} {:>7} {:>7} {:>7} {:>7}"
HEAD = ROW.format("strategy", "trades", "median", "bad 1/20", "P(loss)", "med DD", "bad DD",
                  "DD>20%", "streak")


def row(label: str, s: dict) -> str:
    return ROW.format(label[:28], s["median_trades"], f"{s['median_return_pct']:+.1f}%",
                      f"{s['bad_case_return_pct']:+.1f}%", f"{s['p_loss_pct']:.0f}%",
                      f"{s['median_max_dd_pct']:.0f}%", f"{s['bad_max_dd_pct']:.0f}%",
                      f"{s['p_dd_over_20_pct']:.0f}%", s["bad_losing_streak"])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--files", help="comma-separated strategy files (default: FUT_STRATEGY_FILE)")
    p.add_argument("--months", type=int, default=12)
    p.add_argument("--risk", type=float, help="risk per trade (default: FUT_RISK_FRACTION)")
    p.add_argument("--paths", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=19)
    p.add_argument("--days", type=int, default=1095, help="history for the walk-forward")
    p.add_argument("--refresh", action="store_true", help="top up the candle cache first")
    args = p.parse_args()

    base = Config()
    files = [f.strip() for f in (args.files or futures_cfg(base).strategy_file).split(",") if f.strip()]
    risk = args.risk if args.risk is not None else base.fut_risk_fraction
    print(f"\n  Time Machine: next {args.months} months, {args.paths:,} replays, "
          f"{risk:.1%} risk per trade (seed {args.seed})\n")

    results, by_strategy = [], {}
    for path in files:
        label, trades, years = oos_trades(path, base, args.days, args.refresh)
        per_year = len(trades) / years if years else 0.0
        n_next = int(round(per_year * args.months / 12))
        r = np.array([t.R for t in trades])
        results.append((label, summary(trade_bootstrap(r, n_next, risk, args.paths, args.seed)),
                        trade_odds(trades)))
        by_strategy[label] = trades
        print(f"  {label}: {len(trades)} out-of-sample trades, ~{per_year:.0f}/year", flush=True)

    port = summary(month_bootstrap(months_of(by_strategy), args.months, risk, args.paths, args.seed))
    lines = [HEAD] + [row(lbl, s) for lbl, s, _ in results] + [row("PORTFOLIO (all together)", port)]
    legend = ("median / bad 1/20 = return in a typical replay / in a 1-in-20 bad one; P(loss) = share "
              "of replays that end down; med DD / bad DD = worst drop from a peak, typical / 1-in-20; "
              "streak = losing trades in a row, 1-in-20 bad case")
    odds = [f"{lbl:28} win {o['win_pct']}% | ended at stop {o['stop_pct']}%, target {o['tp_pct']}%, "
            f"exit signal {o['signal_pct']}% | avg win {o['avg_win_R']}R, avg loss {o['avg_loss_R']}R, "
            f"worst {o['worst_R']}R" for lbl, _, o in results if o["trades"]]
    print("\n" + "\n".join("  " + ln for ln in lines))
    print(f"\n  {legend}")
    print("\n  How trades have ended (what to expect from the next one):\n" +
          "\n".join("  " + ln for ln in odds))

    os.makedirs("reports", exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = os.path.join("reports", f"timemachine_{stamp}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# Time Machine {stamp} UTC\n\nNext {args.months} months, {args.paths:,} replays, "
                f"{risk:.1%} risk per trade, seed {args.seed}. Built from each strategy's "
                "out-of-sample walk-forward trades. Strategy rows shuffle that strategy's own trades; "
                "the portfolio row resamples whole historical months for all strategies together, so "
                "coins that fell together still fall together. Not modelled: the live margin cap and "
                "daily loss limit (both would skip some trades). A reality check, not a forecast.\n\n")
        f.write("```\n" + "\n".join(lines) + "\n```\n\n" + legend + "\n\n## How trades have ended\n\n"
                "```\n" + "\n".join(odds) + "\n```\n")
    print(f"\n  Report: {out}\n")


if __name__ == "__main__":
    main()
