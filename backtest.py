"""Backtest the strategy + risk sizing over historical candles.

By default it runs on the synthetic sample data (no network, no keys) so you
can see the whole pipeline work:

    python make_sample_data.py
    python backtest.py

To test on real OKX candles instead (needs ccxt + internet, no keys required
for public market data):

    python backtest.py --live --symbol BTC/USDT --timeframe 1h --limit 1000

Sizing note: the backtest sizes purely by risk-fraction against the ATR stop,
so the numbers reflect the *strategy's* edge. The live bot additionally caps
per-trade notional (MAX_NOTIONAL_USD) to keep real risk tiny while you verify.
"""
from __future__ import annotations

import argparse
import dataclasses

import numpy as np
import pandas as pd

from config import Config
from bot.risk import RiskManager
from bot.strategy import add_indicators, cross


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["time"])
    return df


def load_live(cfg: Config, limit: int) -> pd.DataFrame:
    """Public OKX candles, paged forward from `limit` bars ago (OKX returns at
    most 300 per request, so one call would silently cap --limit)."""
    import ccxt
    from bot.exchange import candles_to_df

    client = ccxt.okx({"enableRateLimit": True})
    tf_ms = client.parse_timeframe(cfg.timeframe) * 1000
    now = client.milliseconds()
    since = now - limit * tf_ms
    rows: dict[int, list] = {}
    while since < now:
        batch = client.fetch_ohlcv(cfg.symbol, cfg.timeframe, since=since, limit=300)
        if not batch:
            break
        for r in batch:
            rows[r[0]] = r
        if batch[-1][0] + tf_ms <= since:
            break
        since = batch[-1][0] + tf_ms
    closed = [rows[t] for t in sorted(rows) if t + tf_ms <= now]  # drop the forming candle
    return candles_to_df(closed[-limit:])


def run(df: pd.DataFrame, cfg: Config) -> dict:
    # uncap notional for evaluation; live keeps the cap
    eval_cfg = dataclasses.replace(cfg, max_notional_usd=1e15)
    risk = RiskManager(eval_cfg)

    d = add_indicators(df, cfg.ema_fast, cfg.ema_slow, cfg.atr_period).reset_index(drop=True)
    warmup = cfg.ema_slow + cfg.atr_period + 2

    equity = cfg.backtest_start_equity  # cash; an open position is valued separately
    position = None  # dict(entry, size, stop, risk, cost) when long
    trades: list[dict] = []
    curve: list[float] = []

    def close(price: float, reason: str) -> None:
        nonlocal equity, position
        proceeds = position["size"] * price
        fee = proceeds * cfg.fee_rate
        equity += proceeds - fee
        pnl = proceeds - fee - position["cost"]  # cost includes the entry fee
        risk.record_pnl(pnl)
        trades.append({"entry": position["entry"], "exit": price, "pnl": pnl, "reason": reason,
                       "R": pnl / position["risk"] if position["risk"] else 0.0})
        position = None

    for i in range(warmup, len(d)):
        row, prev = d.iloc[i], d.iloc[i - 1]
        price, atr = float(row["close"]), float(row["atr"])
        if np.isnan(atr):
            continue
        risk.roll_day(row["time"].date())

        # the stop rests from the bar after entry; a gap through it fills at the open
        if position is not None and float(row["low"]) <= position["stop"]:
            close(min(float(row["open"]), position["stop"]), "stop")

        signal = cross(prev, row)
        if signal == "buy" and position is None:
            dec = risk.evaluate_entry(price, atr, equity / (1 + cfg.fee_rate), kill=False)
            if dec.allowed:
                notional = dec.size * price
                fee = notional * cfg.fee_rate
                equity -= notional + fee
                position = {"entry": price, "size": dec.size, "stop": price - dec.stop_distance,
                            "risk": dec.size * dec.stop_distance, "cost": notional + fee}
        elif signal == "sell" and position is not None:
            close(price, "signal")

        curve.append(equity + (position["size"] * price if position else 0.0))

    if position is not None:  # close at last price for reporting
        close(float(d.iloc[-1]["close"]), "end")
        curve.append(equity)

    return _metrics(trades, curve, equity, cfg, d)


def _metrics(trades: list[dict], curve: list[float], final: float, cfg: Config,
             d: pd.DataFrame) -> dict:
    curve_arr = np.array(curve) if curve else np.array([cfg.backtest_start_equity])
    peak = np.maximum.accumulate(curve_arr)
    max_dd = float(((curve_arr - peak) / peak).min() * 100) if len(curve_arr) else 0.0

    pnls = [t["pnl"] for t in trades]
    rs = [t["R"] for t in trades]
    wins = [p for p in pnls if p > 0]
    bh = (float(d.iloc[-1]["close"]) / float(d.iloc[0]["close"]) - 1) * 100

    return {
        "trades": len(trades),
        "stopped_out": sum(1 for t in trades if t["reason"] == "stop"),
        "win_rate_pct": round(100 * len(wins) / len(trades), 1) if trades else 0.0,
        "avg_R": round(float(np.mean(rs)), 3) if rs else 0.0,
        "total_R": round(float(np.sum(rs)), 2) if rs else 0.0,
        "total_return_pct": round((final / cfg.backtest_start_equity - 1) * 100, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "buy_hold_pct": round(bh, 2),
        "final_equity": round(final, 2),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true", help="fetch real OKX candles instead of sample data")
    p.add_argument("--csv", default="data/sample_ohlcv.csv")
    p.add_argument("--symbol")
    p.add_argument("--timeframe")
    p.add_argument("--limit", type=int, default=1000)
    args = p.parse_args()

    cfg = Config()
    if args.symbol:
        cfg = dataclasses.replace(cfg, symbol=args.symbol)
    if args.timeframe:
        cfg = dataclasses.replace(cfg, timeframe=args.timeframe)

    df = load_live(cfg, args.limit) if args.live else load_csv(args.csv)
    m = run(df, cfg)

    print(f"\n  Backtest: {cfg.symbol} {cfg.timeframe}  ({len(df)} bars)")
    print(f"  {'-' * 44}")
    print(f"  Trades            {m['trades']}")
    print(f"  Stopped out       {m['stopped_out']}")
    print(f"  Win rate          {m['win_rate_pct']} %")
    print(f"  Avg R / trade     {m['avg_R']}")
    print(f"  Total R           {m['total_R']}")
    print(f"  Total return      {m['total_return_pct']} %   (risk-fraction sized)")
    print(f"  Max drawdown      {m['max_drawdown_pct']} %")
    print(f"  Buy & hold        {m['buy_hold_pct']} %")
    print(f"  Final equity      {m['final_equity']}\n")


if __name__ == "__main__":
    main()
