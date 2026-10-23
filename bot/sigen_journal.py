"""SiGen signal journal: every signal as it was issued, and what happened next.

    python -m bot.sigen record        # log this candle's new signals (the console does this itself)
    python -m bot.sigen backfill      # replay the last 30 days, marked as replays
    python -m bot.sigen report        # how logged signals turned out

A signal is written down the moment it is issued: entry, stop-loss, target,
exit rule, the chase limit, and the confidence and tested win rate shown at the
time. Nothing in a record changes afterwards, so a report can't flatter the
past with hindsight. Records made after the entry candle (the console was off
when it fired) are marked late.

Judging a signal: it is followed candle by candle with its own plan, the same
rules the backtest uses. The stop-loss rests from the next candle, the target
likewise, the exit rule fires on a close, and on futures the stop trails once
the trade is 2R in profit. The result is in R (the distance from entry to the
first stop), before fees. A signal is correct if it ended above +0.05R, wrong
below -0.05R, and break-even in between. It is still open until one of those
exits happens. The report also gives how far price went for and against it
(MFE / MAE) and whether the next candle opened inside the chase limit, which
says whether you could still have got in.

Replays (backfill) run today's chosen strategy over recent candles. The
strategy was picked on data that includes those weeks, so replays show how
signals look and resolve, not live accuracy. They are reported separately.
"""
from __future__ import annotations

import csv
import io
import threading
from datetime import datetime, timezone

import pandas as pd

from bot import sigen

FILE = "journal.json"
BAR = pd.Timedelta(minutes=240)
FLAT_R = 0.05
_lock = threading.Lock()   # the console logs from its recorder thread and from page loads

FROZEN = ("market", "coin", "symbol", "direction", "strategy", "label", "spec", "timeframe", "entry_bar",
          "signal_time", "valid_from", "valid_until", "entry", "target", "chase_limit", "trail", "exit_rule",
          "instruction", "rule")


def load(root: str = ".") -> dict:
    return sigen.read(root, FILE).get("signals", {})


def save(root: str, signals: dict) -> None:
    sigen.write(root, FILE, {"signals": signals})


def key(s: dict) -> str:
    return f"{s['market']}:{s['coin']}:{s['entry_bar']}:{s['direction']}"


def snapshot(s: dict, source: str, scan_at: str | None) -> dict:
    late = s["state"] != "entry"
    rec = {k: s.get(k) for k in FROZEN}
    rec.update(id=key(s), source=source, late=late and source == "live",
               stop=s.get("initial_stop") or s["stop"],
               confidence={"score": s["confidence"]["score"], "label": s["confidence"]["label"]},
               tested={k: s["accuracy"][k] for k in ("win_rate_pct", "expected_win_rate_pct", "trades",
                                                      "profit_factor")},
               scan_generated_at=scan_at,
               recorded_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    if late:  # the issue window is the entry candle's, whenever we noticed it
        close = pd.Timestamp(s["entry_bar"]) + BAR
        rec["valid_from"], rec["valid_until"] = close.isoformat(), (close + BAR).isoformat()
    return rec


def record(signals: list[dict], root: str = ".", source: str = "live", scan_at: str | None = None) -> list[str]:
    """Add newly issued signals (entries, and active ones we haven't logged yet)."""
    with _lock:
        return _record(signals, root, source, scan_at)


def _record(signals, root, source, scan_at):
    journal = load(root)
    added = []
    for s in signals:
        if s.get("state") not in ("entry", "holding") or not s.get("entry_bar") or s.get("stop") is None:
            continue
        k = key(s)
        if k not in journal:
            journal[k] = snapshot(s, source, scan_at)
            added.append(k)
    if added:
        save(root, journal)
    return added


# --- following a signal forward ---------------------------------------------------------
def follow(rec: dict, df: pd.DataFrame, cfg) -> dict:
    """Walk the signal's own plan forward from its entry candle. df: closed candles."""
    from bot.futures import trail_params, trail_stop
    from bot.strategies import StrategySpec, signals_ls
    spec = StrategySpec.from_dict(rec["spec"])
    fut = rec["market"] == "futures"
    times = pd.Index(df["time"])
    i = times.get_indexer([pd.Timestamp(rec["entry_bar"])])[0]
    if i < 0:
        return {"status": "no data", "note": "the entry candle is outside the downloaded history"}
    sig = signals_ls(df, spec)  # spot specs have shorts off, so their short columns stay False
    d = 1 if rec["direction"] == "long" else -1
    entry, stop0, tp = rec["entry"], rec["stop"], rec.get("target")
    risk = abs(entry - stop0)
    if not risk > 0:
        return {"status": "no data", "note": "the signal has no stop distance"}
    o, h, l, c = (sig[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    a = sig["atr"].to_numpy(dtype=float)
    lx, le = sig["exit"].to_numpy(), sig["entry"].to_numpy()
    sx, se = sig["short_exit"].to_numpy(), sig["short_entry"].to_numpy()
    start_r, trail_atr = trail_params(spec, cfg) if fut else (0.0, 0.0)
    stop, extreme, mfe, mae = stop0, entry, 0.0, 0.0
    out = None
    for k in range(i + 1, len(sig)):
        worst, best = (l[k], h[k]) if d > 0 else (h[k], l[k])
        if d * (worst - stop) <= 0:
            px = min(o[k], stop) if d > 0 else max(o[k], stop)
            out = (k, px, "trailing stop" if stop != stop0 else "stop")
        elif tp is not None and d * (best - tp) >= 0:
            px = max(o[k], tp) if d > 0 else min(o[k], tp)
            out = (k, px, "tp")
        # how far price went for and against it; on a stop candle assume the stop came first
        if out and out[2] != "tp":
            mae = min(mae, d * (out[1] - entry) / risk)
        else:
            mfe = max(mfe, d * ((out[1] if out else best) - entry) / risk)
            mae = min(mae, d * (worst - entry) / risk)
        if out:
            break
        if (d > 0 and (lx[k] or se[k])) or (d < 0 and (sx[k] or le[k])):
            out = (k, c[k], "signal")
            break
        extreme = max(extreme, h[k]) if d > 0 else min(extreme, l[k])
        stop = trail_stop(d, entry, risk, stop, extreme, a[k], start_r, trail_atr) if fut else stop

    nxt = i + 1 if i + 1 < len(sig) else None
    window = None
    if nxt is not None and rec.get("chase_limit"):
        window = {"next_open": float(o[nxt]), "enterable": bool(d * (o[nxt] - rec["chase_limit"]) <= 0)}
    base = {"mfe_r": round(mfe, 2), "mae_r": round(mae, 2), "entry_window": window, "trail_moved": bool(stop != stop0)}
    if out is None:
        r_now = d * (c[-1] - entry) / risk
        return {**base, "status": "open", "r_now": round(r_now, 2), "price": float(c[-1]), "stop_now": float(stop),
                "bars_held": len(sig) - 1 - i, "as_of": (pd.Timestamp(df["time"].iloc[-1]) + BAR).isoformat()}
    k, px, reason = out
    r = d * (px - entry) / risk
    status = "won" if r > FLAT_R else "lost" if r < -FLAT_R else "flat"
    return {**base, "status": status, "exit_price": float(px), "exit_reason": reason, "result_r": round(r, 2),
            "move_pct": round(d * (px / entry - 1) * 100, 2), "bars_held": k - i,
            "exit_time": (pd.Timestamp(df["time"].iloc[k]) + BAR).isoformat()}


VERDICT = {"won": "Correct", "lost": "Wrong", "flat": "Break-even", "open": "Still open", "no data": "Can't tell yet"}


def evaluate(root: str = ".", fetch=None) -> list[dict]:
    from bot.strategies import StrategySpec, warmup_bars
    journal = load(root)
    if not journal:
        return []
    cfgs = sigen.configs()
    if fetch is None:
        from bot.data import fetch_closed, public_client
        client = public_client(cfgs["spot"].okx_hostname)
        fetch = lambda s, tf, n: fetch_closed(client, s, tf, n)  # noqa: E731
    now = pd.Timestamp.now(tz="UTC")
    by_symbol: dict[str, list[dict]] = {}
    for rec in journal.values():
        by_symbol.setdefault(rec["symbol"], []).append(rec)
    out = []
    for symbol, recs in by_symbol.items():
        oldest = min(pd.Timestamp(r["entry_bar"]) for r in recs)
        warm = max(warmup_bars(StrategySpec.from_dict(r["spec"])) for r in recs)
        n = min(warm + int((now - oldest) / BAR) + 5, 4000)
        try:
            df = fetch(symbol, sigen.TIMEFRAME, n)
            err = None
        except Exception as e:
            df, err = None, repr(e)[:160]
        for rec in recs:
            res = follow(rec, df, cfgs[rec["market"]]) if df is not None else {"status": "no data", "note": err}
            out.append({**rec, "outcome": {**res, "verdict": VERDICT[res["status"]]}})
    out.sort(key=lambda r: r["entry_bar"], reverse=True)
    return out


def summary(rows: list[dict]) -> dict:
    def block(rs):
        closed = [r for r in rs if r["outcome"]["status"] in ("won", "lost", "flat")]
        won = [r for r in closed if r["outcome"]["status"] == "won"]
        rr = [r["outcome"]["result_r"] for r in closed]
        exp = [r["tested"]["win_rate_pct"] for r in closed]
        return {"signals": len(rs), "closed": len(closed), "open": sum(r["outcome"]["status"] == "open" for r in rs),
                "won": len(won), "lost": sum(r["outcome"]["status"] == "lost" for r in closed),
                "flat": sum(r["outcome"]["status"] == "flat" for r in closed),
                "win_rate_pct": round(100 * len(won) / len(closed), 1) if closed else None,
                "tested_win_rate_pct": round(sum(exp) / len(exp), 1) if exp else None,
                "avg_r": round(float(sum(rr)) / len(rr), 2) if rr else None, "total_r": round(float(sum(rr)), 2) if rr else 0.0}
    return {src: block([r for r in rows if r["source"] == src]) for src in ("live", "replay")}


def report(root: str = ".", fetch=None) -> dict:
    rows = evaluate(root, fetch)
    return {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "summary": summary(rows),
            "signals": rows, "flat_r": FLAT_R, "chase_r": sigen.CHASE_R}


CSV_COLS = ["id", "source", "late", "market", "coin", "direction", "strategy", "entry_bar", "valid_from",
            "valid_until", "entry", "stop", "target", "chase_limit", "confidence", "tested_win_rate_pct",
            "status", "verdict", "exit_time", "exit_price", "exit_reason", "result_r", "mfe_r", "mae_r",
            "bars_held", "next_open", "enterable"]


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(CSV_COLS)
    for r in rows:
        o = r["outcome"]
        win = o.get("entry_window") or {}
        w.writerow([r["id"], r["source"], r.get("late"), r["market"], r["coin"], r["direction"], r["strategy"],
                    r["entry_bar"], r["valid_from"], r["valid_until"], r["entry"], r["stop"], r.get("target"),
                    r.get("chase_limit"), r["confidence"]["score"], r["tested"]["win_rate_pct"], o["status"],
                    o["verdict"], o.get("exit_time"), o.get("exit_price"), o.get("exit_reason"),
                    o.get("result_r", o.get("r_now")), o.get("mfe_r"), o.get("mae_r"), o.get("bars_held"),
                    win.get("next_open"), win.get("enterable")])
    return buf.getvalue()


# --- replay -----------------------------------------------------------------------------
def backfill(root: str = ".", days: int = 30, fetch=None) -> int:
    """Signals today's strategies would have issued over the last `days`, logged as replays."""
    from bot.engine import simulate, simulate_ls
    from bot.strategies import StrategySpec, signals, signals_ls, warmup_bars
    doc = sigen.read(root, "scan.json")
    if not doc:
        return 0
    cfgs = sigen.configs()
    if fetch is None:
        from bot.data import fetch_closed, public_client
        client = public_client(cfgs["spot"].okx_hostname)
        fetch = lambda s, tf, n: fetch_closed(client, s, tf, n)  # noqa: E731
    models = {m: sigen.Model(sigen.read(root, f"model_{m}.json")) for m in sigen.MARKETS}
    with _lock:
        return _backfill(doc, cfgs, fetch, models, root, days)


def _backfill(doc, cfgs, fetch, models, root, days):
    from bot.engine import simulate, simulate_ls
    from bot.strategies import StrategySpec, signals, signals_ls, warmup_bars
    journal = load(root)
    since = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    added = 0
    for res in doc["results"]:
        if not res.get("chosen"):
            continue
        m, cfg = res["market"], cfgs[res["market"]]
        spec = StrategySpec.from_dict(res["chosen"]["spec"])
        warm = warmup_bars(spec)
        live_window = warm + 300
        try:
            df = fetch(res["symbol"], sigen.TIMEFRAME, live_window + days * 6 + 10)
        except Exception:
            continue
        sig = signals_ls(df, spec) if m == "futures" else signals(df, spec)
        trades, _, _ = (simulate_ls if m == "futures" else simulate)(sig, spec, cfg)
        times = pd.Index(df["time"])
        for t in trades:
            if t.entry_time < since:
                continue
            i = times.get_indexer([t.entry_time])[0]
            window = df.iloc[max(0, i + 1 - live_window):i + 1].reset_index(drop=True)
            s = sigen.signal_for(res, models[m], window, cfg)   # exactly what the page showed then
            if s["state"] != "entry" or key(s) in journal:
                continue
            journal[key(s)] = snapshot(s, "replay", doc["generated_at"])
            added += 1
    if added:
        save(root, journal)
    return added
