"""After a demo run: did the live bot do what the backtest says it should have?

    python session_report.py                    # since the first "started" in logs/bot.log
    python session_report.py --since 2026-10-22T09:00

It reads the bot's recorded trades from logs/bot.log, replays the same
strategy over the same hours of OKX candles, and lines the two up:
matching entries/exits, price differences (slippage), and P&L. If they match,
the backtest is a trustworthy model of the bot -- which is what lets months of
backtest, not one or two days of demo, answer "is it profitable?".
Uses public candles only; no account access.
"""
from __future__ import annotations

import argparse
import json
import os

import pandas as pd

from config import Config
from bot.data import fetch_closed, public_client
from bot.engine import simulate
from bot.runner import load_strategy
from bot.strategies import signals, warmup_bars


def read_log(path: str) -> list[dict]:
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def live_trades(events: list[dict], since: pd.Timestamp) -> list[dict]:
    trades, open_ = [], None
    for e in events:
        if pd.Timestamp(e["ts"]) < since:
            continue
        if e["msg"] == "entry_filled":
            open_ = e
        elif e["msg"] == "exit_filled" and open_ is not None:
            trades.append({"entry_bar": open_.get("bar"), "entry": open_["price"],
                           "signal_close": open_.get("signal_close"), "exit_ts": e["ts"],
                           "exit": e["price"], "reason": e["reason"], "pnl": e["pnl"],
                           # stop exits are market orders by design, so they don't count
                           "maker_shares": [open_.get("maker_share"),
                                            e.get("maker_share") if e["reason"] != "stop" else None]})
            open_ = None
    if open_ is not None:
        trades.append({"entry_bar": open_.get("bar"), "entry": open_["price"],
                       "signal_close": open_.get("signal_close"), "exit_ts": None, "exit": None,
                       "reason": "open", "pnl": 0.0})
    return trades


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--log", default=os.path.join("logs", "bot.log"))
    p.add_argument("--since", help="ISO time (UTC); default: first 'started' event in the log")
    args = p.parse_args()

    cfg, spec = load_strategy(Config())
    if not os.path.exists(args.log):
        raise SystemExit(f"no log at {args.log}; run the bot first")
    events = read_log(args.log)
    starts = [e for e in events if e["msg"] == "started"]
    since = pd.Timestamp(args.since, tz="UTC") if args.since else (
        pd.Timestamp(starts[0]["ts"]) if starts else pd.Timestamp(events[0]["ts"]))
    live = live_trades(events, since)

    client = public_client(cfg.okx_hostname)
    if cfg.demo:
        # OKX's demo market prints its own candles (same trend, different wicks);
        # replay the bot on the candles it actually saw
        client.set_sandbox_mode(True)
    hours = (pd.Timestamp.now(tz="UTC") - since).total_seconds() / 3600
    tf_hours = client.parse_timeframe(cfg.timeframe) / 3600
    df = fetch_closed(client, cfg.symbol, cfg.timeframe, int(hours / tf_hours) + warmup_bars(spec) + 2)
    sig = signals(df, spec)
    start = int((sig["time"] >= since.floor("min")).idxmax())
    bt, _, _ = simulate(sig, spec, cfg, start=start)

    print(f"\n  Session report: {cfg.symbol} {cfg.timeframe}  since {since:%Y-%m-%d %H:%M} UTC "
          f"({hours:.1f} h)\n  {spec.label()}\n")

    print("  Live (OKX demo) trades")
    for t in live:
        slip = (f"{(t['entry'] / t['signal_close'] - 1) * 1e4:+.1f} bps"
                if t.get("signal_close") else "-")
        print(f"    entry bar {t['entry_bar']}  @ {t['entry']:.2f} (slippage {slip})  -> "
              f"{t['reason']} @ {t['exit'] if t['exit'] else '-'}  pnl {t['pnl']:+.4f}")
    if not live:
        print("    none")

    print("\n  Backtest trades over the same window")
    for t in bt:
        print(f"    entry bar {t.entry_time.isoformat()}  @ {t.entry:.2f}  -> {t.reason} "
              f"@ {t.exit:.2f}  ({(t.exit / t.entry - 1) * 100:+.2f}%)")
    if not bt:
        print("    none")

    live_bars = {t["entry_bar"] for t in live}
    bt_bars = {t.entry_time.isoformat() for t in bt}
    matched = live_bars & bt_bars
    print(f"\n  Entries matched: {len(matched)}   only live: {len(live_bars - bt_bars)}   "
          f"only backtest: {len(bt_bars - live_bars)}")
    closed = [t for t in live if t["exit"]]
    print(f"  Live realized P&L: {sum(t['pnl'] for t in closed):+.4f} {cfg.symbol.split('/')[1]} "
          f"over {len(closed)} closed trades")
    shares = [m for t in live for m in t.get("maker_shares", []) if m is not None]
    if shares:
        print(f"  Maker fill share: {sum(shares) / len(shares):.0%} of orders "
              f"(research assumed {cfg.maker_fill_rate:.0%}; set MAKER_FILL_RATE to the measured "
              "value and re-run research)")
    if live_bars ^ bt_bars:
        print("  Mismatches mean the bot and the backtest disagree -- investigate those before "
              "trusting any backtest result.")
    if len(closed) < 30:
        print(f"  Note: {len(closed)} trades is far too few to judge profitability; that's "
              "what research.py's out-of-sample results are for.")
    print()


if __name__ == "__main__":
    main()
