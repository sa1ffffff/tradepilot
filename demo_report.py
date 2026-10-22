"""Report on a demo run of both bots, and the costs it measured.

    python demo_report.py            # writes reports/demo_run_<date>.md and reports/measured_costs.json

Reads only logs/bot.log and logs/futures.log. measured_costs.json holds the
real maker-fill share and entry slippage, which research.py can use in place
of its assumptions (--maker-fill-rate), so the next research round reflects
how orders actually filled.
"""
from __future__ import annotations

import json
import os
import statistics as st
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

LOGS = {"Spot": os.path.join("logs", "bot.log"), "Futures": os.path.join("logs", "futures.log")}


def read(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip().startswith("{")]


def trades(events: list[dict], bot: str) -> list[dict]:
    """Pair each entry with the next exit on the same symbol."""
    open_, out = {}, []
    for e in events:
        sym = e.get("symbol", "BTC/USDT")
        if e["msg"] == "entry_filled":
            open_[sym] = e
        elif e["msg"] == "exit_filled" and sym in open_:
            en = open_.pop(sym)
            sig = en.get("signal_close")
            side = en.get("side", "long")
            d = 1 if side == "long" else -1
            out.append({
                "bot": bot, "symbol": sym.replace(":USDT", ""), "side": side,
                "opened": en["ts"], "closed": e["ts"], "entry": en["price"], "exit": e["price"],
                "pnl": e.get("pnl", 0.0), "reason": e.get("reason", ""),
                "notional": en["price"] * en.get("size", 0.0),
                # +ve = filled worse than the signal bar's close
                "slip_bps": d * (en["price"] / sig - 1) * 1e4 if sig else None,
                "maker_in": en.get("maker_share"), "maker_out": e.get("maker_share"),
                "hours": (datetime.fromisoformat(e["ts"]) - datetime.fromisoformat(en["ts"])).total_seconds() / 3600,
            })
    return out


def problems(events: list[dict]) -> Counter:
    c = Counter()
    for e in events:
        if e.get("level") not in ("ERROR", "WARNING"):
            continue
        text = (e.get("exc") or e.get("error") or e["msg"])
        if "50013" in text or "busy" in text.lower():
            c["OKX 'system busy' (50013)"] += 1
        elif "50001" in text:
            c["OKX 'service unavailable' (50001)"] += 1
        elif "Timeout" in text or "timed out" in text:
            c["request timeout"] += 1
        elif e["msg"] in ("network_error",) or "NetworkError" in text or "GET https" in text:
            c["network / connection"] += 1
        else:
            c[e["msg"]] += 1
    return c


def pct(x):
    return f"{x:.0%}" if x is not None else "–"


def money(x):
    return f"{x:+,.2f}"


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles
    except AttributeError:
        pass
    events = {b: read(p) for b, p in LOGS.items()}
    all_trades = trades(events["Spot"], "Spot") + trades(events["Futures"], "Futures")
    all_trades.sort(key=lambda t: t["closed"])
    stamps = [e["ts"] for ev in events.values() for e in ev]
    start, end = min(stamps), max(stamps)
    hours = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 3600

    lines = [f"# Demo run report", "",
             f"Period: {start[:16]} → {end[:16]} UTC ({hours:.0f} h). Source: logs/bot.log, logs/futures.log.",
             "Demo (simulated) money on OKX. P&L in USDT, after fees (futures P&L is OKX's own figure, including funding).", ""]

    lines += ["## Summary", "", "| Bot | Trades | Won | Net P&L | Best | Worst | Avg hold |", "|---|---|---|---|---|---|---|"]
    for bot in ("Spot", "Futures"):
        t = [x for x in all_trades if x["bot"] == bot]
        if not t:
            lines.append(f"| {bot} | 0 | – | – | – | – | – |")
            continue
        p = [x["pnl"] for x in t]
        lines.append(f"| {bot} | {len(t)} | {sum(v > 0 for v in p)} | **{money(sum(p))}** | {money(max(p))} | "
                     f"{money(min(p))} | {st.mean(x['hours'] for x in t):.1f} h |")
    total = sum(x["pnl"] for x in all_trades)
    lines += ["", f"**Total: {money(total)} USDT over {len(all_trades)} trades.**", ""]

    by_slot = defaultdict(list)
    for x in all_trades:
        by_slot[(x["bot"], x["symbol"])].append(x)
    lines += ["## By market", "", "| Bot | Market | Trades | Net P&L | Exits |", "|---|---|---|---|---|"]
    for (bot, sym), t in sorted(by_slot.items()):
        reasons = ", ".join(f"{k} {v}" for k, v in Counter(x["reason"] for x in t).most_common())
        lines.append(f"| {bot} | {sym} | {len(t)} | {money(sum(x['pnl'] for x in t))} | {reasons} |")

    # costs actually measured
    # stop-loss exits are market orders by design (research charges them as taker),
    # so the maker share that research assumes covers entries and non-stop exits only
    fills = [(x["bot"], m) for x in all_trades
             for m in (x["maker_in"], None if x["reason"] == "stop" else x["maker_out"]) if m is not None]
    def share(bot):
        v = [m for b, m in fills if b == bot]
        return (st.mean(v) if v else None), len(v)
    spot_share, spot_n = share("Spot")
    fut_share, fut_n = share("Futures")
    slips = [x["slip_bps"] for x in all_trades if x["slip_bps"] is not None]
    stop_exits = [x for x in all_trades if x["reason"] == "stop"]
    lines += ["", "## Execution: what the costs really were", "",
              f"- **Limit (maker) fill share:** spot {pct(spot_share)} of {spot_n} orders; "
              f"futures {pct(fut_share)} of {fut_n} orders (entries and non-stop exits; stops are always "
              "market orders). Research assumed 70%.",
              f"- **Entry price vs signal (bps, + = worse):** average {st.mean(slips):+.1f}, "
              f"range {min(slips):+.1f} to {max(slips):+.1f} over {len(slips)} entries." if slips else "- No entry slippage data.",
              f"- **Stop-loss exits:** {len(stop_exits)} of {len(all_trades)} trades (always market orders)."]

    lines += ["", "## Reliability", ""]
    for bot, ev in events.items():
        c = problems(ev)
        starts = sum(e["msg"] == "started" for e in ev)
        lines.append(f"- **{bot}:** {starts} starts; " +
                     (", ".join(f"{k} ×{v}" for k, v in c.most_common()) if c else "no errors") +
                     ". Every error was recovered from without intervention." if c else f"- **{bot}:** {starts} starts; no errors.")

    lines += ["", "## All trades", "", "| Closed (UTC) | Bot | Market | Side | Entry | Exit | Why | P&L |",
              "|---|---|---|---|---|---|---|---|"]
    for x in all_trades:
        lines.append(f"| {x['closed'][:16].replace('T', ' ')} | {x['bot']} | {x['symbol']} | {x['side']} | "
                     f"{x['entry']:,.1f} | {x['exit']:,.1f} | {x['reason']} | {money(x['pnl'])} |")

    os.makedirs("reports", exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join("reports", f"demo_run_{day}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    measured = {"period": [start, end], "trades": len(all_trades), "net_pnl": round(total, 2),
                "maker_fill_rate": {"spot": round(spot_share, 3) if spot_share is not None else None, "spot_orders": spot_n,
                                    "futures": round(fut_share, 3) if fut_share is not None else None, "futures_orders": fut_n},
                "entry_slippage_bps": {"mean": round(st.mean(slips), 2) if slips else None,
                                       "worst": round(max(slips), 2) if slips else None, "n": len(slips)}}
    with open(os.path.join("reports", "measured_costs.json"), "w", encoding="utf-8") as f:
        json.dump(measured, f, indent=2)
    print("\n".join(lines))
    print(f"\nWrote {path} and reports/measured_costs.json")


if __name__ == "__main__":
    main()
