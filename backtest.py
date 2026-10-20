"""Backtest one strategy over historical candles.

By default it runs the strategy in strategy.json (or the EMA 9/21 fallback)
on the synthetic sample data, so you can see the pipeline work with no network:

    python make_sample_data.py
    python backtest.py

On real OKX candles (public data, no keys):

    python backtest.py --live --days 90
    python backtest.py --live --strategy donchian_breakout --timeframe 1h

This is a single in-sample run -- good for checking behaviour, not for judging
an edge. Use research.py for that.
"""
from __future__ import annotations

import argparse
import dataclasses

import pandas as pd

from config import Config
from bot.data import load_history
from bot.engine import metrics, run
from bot.runner import load_strategy
from bot.strategies import STRATEGIES, StrategySpec


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true", help="real OKX candles instead of sample data")
    p.add_argument("--csv", default="data/sample_ohlcv.csv")
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--symbol")
    p.add_argument("--timeframe")
    p.add_argument("--strategy", choices=list(STRATEGIES), help="default params for this strategy "
                   "instead of strategy.json")
    args = p.parse_args()

    cfg, spec = load_strategy(Config())
    if args.strategy:
        spec = StrategySpec(args.strategy, dict(STRATEGIES[args.strategy].defaults))
    if args.symbol:
        cfg = dataclasses.replace(cfg, symbol=args.symbol)
    if args.timeframe:
        cfg = dataclasses.replace(cfg, timeframe=args.timeframe)

    if args.live:
        df = load_history(cfg, cfg.symbol, cfg.timeframe, args.days)
    else:
        df = pd.read_csv(args.csv, parse_dates=["time"])
    trades, curve, equity = run(df, spec, cfg)
    m = metrics(trades, curve, cfg.backtest_start_equity, equity,
                float(df["close"].iloc[0]), float(df["close"].iloc[-1]))

    print(f"\n  Backtest: {cfg.symbol} {cfg.timeframe}  ({len(df)} bars)  in-sample")
    print(f"  {spec.label()}")
    print(f"  {'-' * 44}")
    print(f"  Trades            {m['trades']}  ({m['stopped_out']} stopped out)")
    print(f"  Win rate          {m['win_rate_pct']} %")
    print(f"  Profit factor     {m['profit_factor']}")
    print(f"  Avg trade         {m['avg_trade_pct']} % of equity")
    print(f"  Total return      {m['total_return_pct']} %")
    print(f"  Max drawdown      {m['max_drawdown_pct']} %")
    print(f"  Buy & hold        {m['buy_hold_pct']} %")
    print(f"  Final equity      {m['final_equity']}\n")


if __name__ == "__main__":
    main()
