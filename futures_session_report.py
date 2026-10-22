"""After a futures demo run: did each futures strategy trade the way its backtest says?

    python futures_session_report.py                       # FUT_STRATEGY_FILE, since the first "started"
    python futures_session_report.py --since 2026-11-01T00:00
    python futures_session_report.py --files strategies/futures_test_btc_5m_swap.json

For every strategy it replays the same hours on OKX's demo candles with the
same code research uses (signals_ls + simulate_ls), then matches live trades to
backtest trades by signal bar and side. A backtest entry the bot didn't take is
explained where the log can: the bot was down then, or it skipped the entry on
purpose (margin room, daily loss limit, kill switch). Only unexplained
mismatches suggest the backtest isn't a faithful model of the bot.

Writes reports/futures_session_<date>.md. Public candles only; no account access.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

import pandas as pd

from config import Config
from bot.data import fetch_closed, public_client
from bot.engine import simulate_ls
from bot.futures import futures_cfg
from bot.futures_runner import load_futures_strategy
from bot.lock import is_held
from bot.strategies import signals_ls, warmup_bars
from demo_report import read


def live_trades(events: list[dict], symbol: str, since: pd.Timestamp) -> list[dict]:
    out, open_ = [], None
    for e in events:
        if e.get("symbol") != symbol or pd.Timestamp(e["ts"]) < since:
            continue
        if e["msg"] == "entry_filled":
            open_ = {"bar": e.get("bar"), "side": e.get("side"), "entry": e["price"],
                     "signal_close": e.get("signal_close"), "exit": None, "reason": "open", "pnl": 0.0}
            out.append(open_)
        elif e["msg"] == "exit_filled" and open_ is not None:
            open_.update(exit=e["price"], reason=e.get("reason", ""), pnl=e.get("pnl", 0.0))
            open_ = None
    return out


def active_spans(events: list[dict], strategy: str, until: pd.Timestamp) -> list[tuple]:
    """When this exact strategy ("SYMBOL TF label", as the 'started' line lists it)
    was running: from each 'started' that lists it to that process's 'stopped' or,
    after a kill, its last log line."""
    spans, cur, last = [], None, None
    for e in events:
        ts = pd.Timestamp(e["ts"])
        if e["msg"] == "started":
            if cur is not None:
                spans.append((cur, last))
            cur = ts if strategy in e.get("strategies", []) else None
        elif e["msg"] == "stopped" and cur is not None:
            spans.append((cur, ts))
            cur = None
        last = ts
    if cur is not None:
        spans.append((cur, until))
    return spans


def match(live: list[dict], bt: list, tf: pd.Timedelta, spans, skipped: dict) -> dict:
    """Pair live and backtest trades by (signal bar, side); explain the leftovers."""
    lv = {(t["bar"], t["side"]): t for t in live if t.get("bar")}
    bk = {(t.entry_time.isoformat(), t.side): t for t in bt}
    rows = []
    for key in sorted(set(lv) | set(bk)):
        l, b = lv.get(key), bk.get(key)
        row = {"bar": key[0], "side": key[1], "live": l, "bt": b, "status": "matched", "why": ""}
        if l and not b:
            row["status"] = "only live"
        elif b and not l:
            acted = pd.Timestamp(key[0]) + tf  # the bot acts when the signal bar closes
            if not any(a <= acted <= z for a, z in spans):
                row.update(status="explained", why="strategy wasn't running then")
            elif key[0] in skipped:
                row.update(status="explained", why=f"bot skipped it: {skipped[key[0]]}")
            else:
                row["status"] = "only backtest"
        rows.append(row)
    return {"rows": rows,
            "matched": sum(r["status"] == "matched" for r in rows),
            "explained": sum(r["status"] == "explained" for r in rows),
            "only_live": sum(r["status"] == "only live" for r in rows),
            "only_bt": sum(r["status"] == "only backtest" for r in rows)}


def px(v: float) -> str:
    return f"{v:,.1f}" if v >= 1000 else f"{v:,.4f}" if v >= 1 else f"{v:.5g}"


def bps(a, b):
    return (a / b - 1) * 1e4 if a and b else None


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    p = argparse.ArgumentParser()
    p.add_argument("--log", default=os.path.join("logs", "futures.log"))
    p.add_argument("--since", help="ISO time (UTC); default: first 'started' in the log")
    p.add_argument("--files", help="comma-separated strategy files (default: FUT_STRATEGY_FILE)")
    args = p.parse_args()

    base = futures_cfg(Config())
    events = read(args.log)
    if not events:
        raise SystemExit(f"no log at {args.log}; run the futures bot first")
    starts = [e for e in events if e["msg"] == "started"]
    since = pd.Timestamp(args.since, tz="UTC") if args.since else pd.Timestamp((starts or events)[0]["ts"])
    running = is_held(base.state_file)
    until = pd.Timestamp.now(tz="UTC") if running else pd.Timestamp(events[-1]["ts"])
    files = [f.strip() for f in (args.files or base.strategy_file).split(",") if f.strip()]

    client = public_client(base.okx_hostname)
    if base.demo:
        client.set_sandbox_mode(True)  # replay on the demo candles the bot actually saw

    out = [f"# Futures session report", "",
           f"Window: {since:%Y-%m-%d %H:%M} → {until:%Y-%m-%d %H:%M} UTC "
           f"({'bot running' if running else 'bot stopped; window ends at its last log line'}). "
           f"Replayed on OKX {'demo' if base.demo else 'live'} candles.", ""]
    totals = {"matched": 0, "explained": 0, "only_live": 0, "only_bt": 0}
    traded_symbols = {e.get("symbol") for e in events if e["msg"] == "entry_filled"}
    covered = set()

    for path in files:
        cfg, spec = load_futures_strategy(base, path)
        covered.add(cfg.symbol)
        tf = pd.Timedelta(seconds=client.parse_timeframe(cfg.timeframe))
        spans = active_spans(events, f"{cfg.symbol} {cfg.timeframe} {spec.label()}", until)
        slot_since = max(since, spans[0][0]) if spans else since
        bars = int((until - slot_since) / tf) + warmup_bars(spec) + 3
        df = fetch_closed(client, cfg.symbol, cfg.timeframe, bars)
        df = df[df["time"] + tf <= until]
        sig = signals_ls(df, spec)
        start = int((sig["time"] >= slot_since.floor("min")).idxmax())
        bt, _, _ = simulate_ls(sig, spec, cfg, start=start)
        live = live_trades(events, cfg.symbol, since)
        skipped = {e.get("bar"): e.get("reason", "") for e in events
                   if e["msg"] == "entry_skipped" and e.get("symbol") == cfg.symbol}
        m = match(live, bt, tf, spans, skipped)
        for k in totals:
            totals[k] += m[k]

        out += [f"## {cfg.symbol.replace(':USDT', '')} {cfg.timeframe}: {spec.label()}", ""]
        if not m["rows"]:
            out += ["No signals in this window (live or backtest).", ""]
            continue
        out += ["| Signal bar (UTC) | Side | Status | Live entry → exit | Backtest entry → exit | Entry diff | Live P&L |",
                "|---|---|---|---|---|---|---|"]
        for r in m["rows"]:
            l, b = r["live"], r["bt"]
            lt = f"{px(l['entry'])} → {px(l['exit'])} ({l['reason']})" if l and l["exit"] else (
                f"{px(l['entry'])} → open" if l else "–")
            bt_txt = f"{px(b.entry)} → {px(b.exit)} ({b.reason})" if b else "–"
            diff = bps(l["entry"], b.entry) if l and b else None
            diff_txt = f"{diff:+.1f} bps" if diff is not None else "–"
            pnl_txt = f"{l['pnl']:+.2f}" if l and l["exit"] else "–"
            status = r["status"] + (f": {r['why']}" if r["why"] else "")
            out.append(f"| {r['bar'][:16].replace('T', ' ')} | {r['side']} | {status} | {lt} | {bt_txt} | "
                       f"{diff_txt} | {pnl_txt} |")
        out.append("")

    missing = sorted(s for s in traded_symbols - covered if s)
    out += ["## Summary", "",
            f"- Entries matched: **{totals['matched']}**; explained by downtime or a deliberate skip: "
            f"{totals['explained']}; only live: **{totals['only_live']}**; only backtest: **{totals['only_bt']}**."]
    if totals["only_live"] or totals["only_bt"]:
        out.append("- Unexplained mismatches mean the bot and the backtest disagree: investigate them "
                   "before trusting research results for that strategy.")
    elif totals["matched"]:
        out.append("- Every live entry matched the backtest, so research is a faithful model of this bot.")
    if missing:
        out.append(f"- Live trades on {', '.join(missing)} aren't covered by these strategy files; "
                   "pass that strategy with --files to check them.")
    out.append("- Exits can differ a little: live stops trigger on the traded price between bars, and "
               "a strategy's settings (trailing stop, size) may have changed during the window.")

    text = "\n".join(out) + "\n"
    print(text)
    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", f"futures_session_{datetime.now(timezone.utc):%Y-%m-%d}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
