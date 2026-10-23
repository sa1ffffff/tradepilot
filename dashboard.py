"""The Tradepilot console: a local web app for both bots.

    python dashboard.py            # this PC only: http://127.0.0.1:8765
    python dashboard.py --lan      # also your phone, on the same Wi-Fi (token-protected)
    (or double-click start_dashboard.bat)

It reads the logs and state files, fetches public OKX demo candles and prices,
and explains what every strategy sees on the latest closed bar. It never reads
the API keys: to stop a bot or close a position it leaves a request in
control/ and the bot carries it out itself (bot/control.py). Starting a bot
launches the same `python -m bot.runner` you would type.

The UI is a React app in web/ (built to web/dist with `npm run build`).
"""
from __future__ import annotations

import json
import mimetypes
import os
import re
import secrets
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from config import Config
from bot import control
from bot.lock import is_held

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "web", "dist")
PORT = 8765
TOKEN_FILE = os.path.join(HERE, "control", "dashboard_token")
BOT_MODULES = {"spot": "bot.runner", "futures": "bot.futures_runner"}


# --- reading logs and state ---------------------------------------------------
def read_log(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def last_started(events: list[dict]) -> dict | None:
    starts = [e for e in events if e.get("msg") == "started"]
    return starts[-1] if starts else None


LABEL_RE = re.compile(r"^(?P<name>\w+)\((?P<params>[^)]*)\) stop=(?P<stop>[\d.]+)ATR "
                      r"(?:tp=(?P<tp>[\d.]+)R|no tp)(?P<shorts> \+shorts)?$")


def parse_label(label: str):
    """StrategySpec from the label the bots log ('supertrend(mult=3.0,trend=200) stop=2.0ATR ...')."""
    from bot.strategies import StrategySpec
    m = LABEL_RE.match(label.strip())
    if not m:
        return None
    params = {}
    for kv in filter(None, m["params"].split(",")):
        k, v = kv.split("=")
        params[k] = float(v) if "." in v else int(v)
    try:
        return StrategySpec.from_dict({"name": m["name"], "params": params, "stop_atr": float(m["stop"]),
                                       "tp_r": float(m["tp"]) if m["tp"] else None,
                                       "shorts": bool(m["shorts"])})
    except ValueError:
        return None


def strategy_slots(cfg: Config) -> list[dict]:
    """What each bot is set up to trade (from .env), with research evidence."""
    from bot.futures_runner import load_futures_strategy
    from bot.futures import futures_cfg
    from bot.runner import load_strategy
    from bot.explain import rule_text
    slots = []
    try:
        scfg, spec = load_strategy(cfg)
        d = read_json(cfg.strategy_file)
        slots.append({"bot": "spot", "symbol": scfg.symbol, "timeframe": scfg.timeframe,
                      "spec": spec.to_dict(), "label": spec.label(), "rule": rule_text(spec),
                      "evidence": d.get("evidence"), "risk_fraction": cfg.risk_fraction,
                      "file": cfg.strategy_file})
    except Exception:
        pass
    fcfg = futures_cfg(cfg)
    for path in [p.strip() for p in fcfg.strategy_file.split(",") if p.strip()]:
        try:
            c, spec = load_futures_strategy(fcfg, path)
        except BaseException:  # load_futures_strategy raises SystemExit on a bad file
            continue
        d = read_json(path)
        slots.append({"bot": "futures", "symbol": c.symbol, "timeframe": c.timeframe,
                      "spec": spec.to_dict(), "label": spec.label(), "rule": rule_text(spec),
                      "evidence": d.get("evidence"), "risk_fraction": c.fut_risk_fraction,
                      "file": path, "trail_start_r": c.fut_trail_start_r})
    return slots


def trades(events: list[dict], bot: str, default_symbol: str, default_tf: str) -> list[dict]:
    """Closed round trips (entry_filled ... exit_filled), oldest first."""
    open_by_sym: dict[str, dict] = {}
    label, tf_by_sym = "", {}
    out = []
    for e in events:
        msg = e.get("msg")
        if msg == "started":
            if bot == "spot":
                label = e.get("strategy", "")
                tf_by_sym[e.get("symbol", default_symbol)] = (e.get("timeframe", default_tf), label)
            for s in e.get("strategies", []):
                sym, tf, lab = s.split(" ", 2)
                tf_by_sym[sym] = (tf, lab)
        elif msg == "entry_filled":
            sym = e.get("symbol", default_symbol)
            tf, lab = tf_by_sym.get(sym, (default_tf, label))
            risk = e.get("risk_usd") or abs(e["price"] - e["stop"]) * e["size"] if e.get("stop") else None
            open_by_sym[sym] = {"entry_time": e["ts"], "bar": e.get("bar"), "symbol": sym, "bot": bot,
                                "side": e.get("side", "long"), "entry": e["price"], "size": e["size"],
                                "stop": e.get("stop"), "tp": e.get("tp"), "leverage": e.get("leverage", 1),
                                "risk_usd": risk, "timeframe": tf, "strategy": lab,
                                "entry_maker_share": e.get("maker_share"),
                                "slippage_bps": round((e["price"] / e["signal_close"] - 1) * 1e4 *
                                                      (1 if e.get("side", "long") == "long" else -1), 2)
                                if e.get("signal_close") else None}
        elif msg == "exit_filled":
            sym = e.get("symbol", default_symbol)
            t = open_by_sym.pop(sym, None) or {
                "entry_time": None, "bar": None, "symbol": sym, "bot": bot, "side": e.get("side", "long"),
                "entry": e.get("entry"), "size": e.get("size"), "stop": None, "tp": None,
                "leverage": e.get("leverage", 1), "risk_usd": None, "timeframe": default_tf,
                "strategy": label, "entry_maker_share": None, "slippage_bps": None}
            pnl = float(e.get("pnl", 0.0))
            t.update({"exit_time": e["ts"], "exit": e.get("price"), "pnl": round(pnl, 2),
                      "reason": e.get("reason", ""), "exit_maker_share": e.get("maker_share"),
                      "r": round(pnl / t["risk_usd"], 2) if t.get("risk_usd") else None})
            t["id"] = f"{bot}:{sym}:{t['exit_time']}"
            out.append(t)
    return out


def open_entries(events: list[dict], default_symbol: str) -> dict[str, dict]:
    """The entry_filled event behind each still-open position, by symbol."""
    cur: dict[str, dict] = {}
    for e in events:
        if e.get("msg") == "entry_filled":
            cur[e.get("symbol", default_symbol)] = e
        elif e.get("msg") == "exit_filled":
            cur.pop(e.get("symbol", default_symbol), None)
    return cur


ACTIVITY = {"entry_filled", "exit_filled", "entry_skipped", "entry_unfilled", "entry_retry",
            "stop_trailed", "trail_hit", "stop_missing_replacing", "stop_failed_closing",
            "liq_inside_stop_closing", "foreign_position", "position_missing", "started", "stopped",
            "error", "network_error"}


def activity(spot_log: list[dict], fut_log: list[dict], limit: int = 400) -> list[dict]:
    """Order and decision history: every fill, skip, stop move, start/stop and error."""
    rows = []
    for bot, log in (("spot", spot_log), ("futures", fut_log)):
        for e in log:
            if e.get("msg") not in ACTIVITY:
                continue
            row = {k: v for k, v in e.items() if k not in ("exc",)}
            row["bot"] = bot
            if e.get("exc"):
                row["error"] = e["exc"].strip().splitlines()[-1][:300]
            rows.append(row)
    rows.sort(key=lambda r: r["ts"], reverse=True)
    return rows[:limit]


def health_note(path: str) -> dict:
    if not os.path.exists(path):
        return {"title": "No health checks yet", "status": "", "lines": []}
    with open(path, encoding="utf-8") as f:
        sections = f.read().split("\n## ")
    last = sections[-1].lstrip("# ").strip().splitlines()
    title = last[0] if last else ""
    status = "ATTENTION" if "ATTENTION" in title else ("OK" if "OK" in title else "")
    return {"title": title, "status": status,
            "lines": [l.lstrip("- ").strip() for l in last[1:] if l.strip()]}


# --- public market data, cached -----------------------------------------------
_client_lock = threading.Lock()
_client = None
_cache: dict[tuple, tuple[float, object]] = {}


def market_client(cfg: Config):
    global _client
    with _client_lock:
        if _client is None:
            import ccxt
            _client = ccxt.okx({"enableRateLimit": True, "hostname": cfg.okx_hostname, "timeout": 10000})
            if cfg.demo:
                _client.set_sandbox_mode(True)  # demo prices, which is what the bots trade at
        return _client


def cached(key: tuple, ttl: float, fn):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    val = fn()
    _cache[key] = (time.time(), val)
    return val


def candles(cfg: Config, symbol: str, tf: str, bars: int):
    from bot.data import fetch_closed
    return cached(("candles", symbol, tf, bars), 45,
                  lambda: fetch_closed(market_client(cfg), symbol, tf, bars))


def live_prices(cfg: Config, symbols: list[str]) -> dict:
    out = {}
    for s in symbols:
        try:
            out[s] = cached(("ticker", s), 8, lambda s=s: float(market_client(cfg).fetch_ticker(s)["last"]))
        except Exception:
            pass
    return out


# --- status ---------------------------------------------------------------------
def bot_status(cfg: Config, bot: str, log: list[dict]) -> dict:
    state_file = cfg.state_file if bot == "spot" else cfg.fut_state_file
    start = last_started(log) or {}
    hb = control.read_heartbeat(bot, HERE)
    running = is_held(state_file)
    stops = [e for e in log if e.get("msg") == "stopped"]
    out_file = os.path.join(HERE, cfg.log_dir, f"{bot}.out")
    return {"running": running, "since": start.get("ts") if running else None,
            "last_started": start.get("ts"), "last_stopped": stops[-1]["ts"] if stops else None,
            "heartbeat": hb.get("ts") if running else None, "pid": hb.get("pid") if running else None,
            "equity": hb.get("equity"), "poll_seconds": hb.get("poll_seconds", cfg.poll_seconds),
            "stop_pending": control.stop_requested(bot, HERE),
            "launch_log": tail(out_file, 6)}


def tail(path: str, n: int) -> list[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return [l.rstrip() for l in f.readlines()[-n:]]
    except OSError:
        return []


def status() -> dict:
    cfg = Config()
    os.chdir(HERE)
    now = datetime.now(timezone.utc)
    day = now.date().isoformat()

    spot_log = read_log(os.path.join(cfg.log_dir, "bot.log"))
    fut_log = read_log(os.path.join(cfg.log_dir, "futures.log"))
    spot_state = read_json(cfg.state_file)
    fut_state = read_json(cfg.fut_state_file)
    spot_start = last_started(spot_log) or {}
    spot_symbol = spot_start.get("symbol", cfg.symbol)
    slots = strategy_slots(cfg)
    slot_by = {(s["bot"], s["symbol"]): s for s in slots}

    positions = []
    entries = {"spot": open_entries(spot_log, spot_symbol), "futures": open_entries(fut_log, "")}
    sp = spot_state.get("position")
    if sp:
        positions.append({"bot": "spot", "symbol": spot_symbol, "side": "long", "dir": 1, **sp,
                          "leverage": 1})
    for sym, slot in (fut_state.get("slots") or {}).items():
        p = slot.get("position")
        if p:
            positions.append({"bot": "futures", "symbol": sym, **p})
    prices = live_prices(cfg, sorted({p["symbol"] for p in positions}))
    closes = control.pending_closes(HERE)
    for p in positions:
        px = prices.get(p["symbol"])
        e = entries[p["bot"]].get(p["symbol"], {})
        risk = e.get("risk_usd") or abs(p["entry"] - p["stop"]) * p["size"]
        p["price"] = px
        p["unrealized"] = round(p["dir"] * (px - p["entry"]) * p["size"], 2) if px else None
        p["r_now"] = round(p["unrealized"] / risk, 2) if px and risk else None
        p["risk_usd"] = round(risk, 2)
        p["liq_price"] = e.get("liq_price")
        p["entry_time"] = e.get("ts")
        p["timeframe"] = slot_by.get((p["bot"], p["symbol"]), {}).get("timeframe")
        p["close_pending"] = any(c["bot"] == p["bot"] and c["symbol"] == p["symbol"] for c in closes)

    closed = trades(spot_log, "spot", spot_symbol, spot_start.get("timeframe", cfg.timeframe)) + \
        trades(fut_log, "futures", "", "")
    closed.sort(key=lambda t: t["exit_time"])
    realized_today = {b: control.pnl_today(f, day) for b, f in
                      (("spot", cfg.state_file), ("futures", cfg.fut_state_file))}
    errors_24h = [e for e in spot_log + fut_log if e.get("level") in ("ERROR", "WARNING")
                  and datetime.fromisoformat(e["ts"]) >= now - timedelta(hours=24)]
    tgt = control.target(HERE)
    combined = sum(realized_today.values())
    unreal = sum(p["unrealized"] or 0 for p in positions)
    wins = [t for t in closed if t["pnl"] > 0]
    losses = [t for t in closed if t["pnl"] <= 0]
    equity = {b: control.read_heartbeat(b, HERE).get("equity") for b in BOT_MODULES}
    return {
        "now": now.isoformat(), "demo": cfg.demo,
        "bots": {"spot": bot_status(cfg, "spot", spot_log), "futures": bot_status(cfg, "futures", fut_log)},
        "kill_switch": os.path.exists(cfg.kill_file),
        "target": {**tgt, "realized_today": round(combined, 2),
                   "reached": bool(tgt["daily_target_usd"] and combined >= tgt["daily_target_usd"])},
        "limits": {"spot_daily_loss": cfg.max_daily_loss_usd, "futures_daily_loss": cfg.fut_max_daily_loss_usd,
                   "spot_max_notional": cfg.max_notional_usd, "futures_risk": cfg.fut_risk_fraction,
                   "futures_max_margin": cfg.fut_max_margin_fraction, "futures_max_leverage": cfg.fut_max_leverage},
        "pnl": {"today": {k: round(v, 2) for k, v in realized_today.items()},
                "today_total": round(combined, 2), "unrealized": round(unreal, 2),
                "all_time": round(sum(t["pnl"] for t in closed), 2),
                "trades": len(closed), "wins": len(wins),
                "gross_win": round(sum(t["pnl"] for t in wins), 2),
                "gross_loss": round(sum(t["pnl"] for t in losses), 2),
                "curve": curve(closed)},
        "equity": equity,
        "positions": positions,
        "prices_ok": bool(prices) or not positions,
        "slots": slots,
        "errors_24h": len(errors_24h),
        "last_error": (errors_24h[-1].get("exc", "").strip().splitlines()
                       or [f'{errors_24h[-1]["msg"]} {errors_24h[-1].get("symbol", "")}'.strip()])[-1][:200]
        if errors_24h else None,
        "health": health_note(os.path.join(cfg.log_dir, "health.md")),
    }


def curve(closed: list[dict]) -> list[list]:
    total, out = 0.0, []
    for t in closed:
        total += t["pnl"]
        out.append([t["exit_time"], round(total, 2)])
    return out


def all_trades() -> list[dict]:
    cfg = Config()
    os.chdir(HERE)
    spot_log = read_log(os.path.join(cfg.log_dir, "bot.log"))
    start = last_started(spot_log) or {}
    out = trades(spot_log, "spot", start.get("symbol", cfg.symbol), start.get("timeframe", cfg.timeframe)) + \
        trades(read_log(os.path.join(cfg.log_dir, "futures.log")), "futures", "", "")
    return sorted(out, key=lambda t: t["exit_time"], reverse=True)


def all_activity() -> list[dict]:
    cfg = Config()
    os.chdir(HERE)
    return activity(read_log(os.path.join(cfg.log_dir, "bot.log")),
                    read_log(os.path.join(cfg.log_dir, "futures.log")))


# --- analysis ---------------------------------------------------------------------
def analysis(bot: str, symbol: str, at: str | None = None, trade_id: str | None = None) -> dict:
    """The strategy's view of the latest closed bar, or of the bar a past trade was taken on."""
    import pandas as pd
    from bot.explain import analyse
    from bot.strategies import StrategySpec, warmup_bars
    cfg = Config()
    os.chdir(HERE)
    slot = next((s for s in strategy_slots(cfg) if s["bot"] == bot and s["symbol"] == symbol), None)
    trade = next((t for t in all_trades() if t["id"] == trade_id), None) if trade_id else None
    if trade:
        spec, tf = parse_label(trade["strategy"]), trade["timeframe"]
        if spec is None and slot:
            spec, tf = StrategySpec.from_dict(slot["spec"]), slot["timeframe"]
    elif slot:
        spec, tf = StrategySpec.from_dict(slot["spec"]), slot["timeframe"]
    else:
        raise LookupError(f"no {bot} strategy for {symbol}")
    if spec is None:
        raise LookupError("can't tell which strategy took this trade")

    warm = warmup_bars(spec)
    view = 160
    if trade and trade.get("bar"):
        from bot.explain import TF_MINUTES
        bar_t = pd.Timestamp(trade["bar"])
        tf_min = TF_MINUTES.get(tf, 60)
        since_bars = int((datetime.now(timezone.utc) - bar_t.to_pydatetime()).total_seconds() / 60 / tf_min)
        bars = min(warm + since_bars + 40, 3000)
        df = candles(cfg, symbol, tf, bars)
        upto = df[df["time"] <= bar_t]
        after = df[df["time"] > bar_t]
        if len(upto) < 50:
            raise LookupError("not enough candle history for this trade")
        res = analyse(upto, spec, tf, bars=view)
        # show what happened next too, up to the exit and a little after
        exit_t = pd.Timestamp(trade["exit_time"]) if trade.get("exit_time") else None
        later = after if exit_t is None else after[after["time"] <= exit_t + pd.Timedelta(minutes=tf_min * 12)]
        res["after"] = [[int(r.time.timestamp()), float(r.open), float(r.high), float(r.low), float(r.close),
                         float(r.volume)] for r in later.itertuples()]
        full = pd.concat([upto, later])
        lines_full = analyse(full, spec, tf, bars=len(later) + view)
        res["lines"], res["panes"], res["signals"] = lines_full["lines"], lines_full["panes"], lines_full["signals"]
        res["candles"] = res["candles"] + res["after"]
        res["trade"] = trade
    else:
        df = candles(cfg, symbol, tf, warm + view)
        fut_state = read_json(cfg.fut_state_file)
        pos = (read_json(cfg.state_file).get("position") if bot == "spot"
               else ((fut_state.get("slots") or {}).get(symbol) or {}).get("position"))
        if pos and bot == "spot":
            pos = {**pos, "dir": 1}
        res = analyse(df, spec, tf, position=pos, bars=view,
                      trail_start_r=(slot or {}).get("trail_start_r", 2.0))
        res["position"] = pos
    res.update({"bot": bot, "symbol": symbol, "timeframe": tf, "label": spec.label()})
    # live fills on this chart: same market and timeframe (old test-slot trades ran on 5m)
    mine = [trade] if trade else [t for t in all_trades() if t["symbol"] == symbol and t["timeframe"] == tf]
    res["fills"] = [{"time": t["entry_time"], "kind": "entry", "side": t["side"], "price": t["entry"]}
                    for t in mine if t["entry_time"]] + \
                   [{"time": t["exit_time"], "kind": "exit", "side": t["side"], "price": t["exit"],
                     "reason": t["reason"]} for t in mine]
    return res


def analysis_overview() -> list[dict]:
    """Headline of every strategy at once, for the overview."""
    cfg = Config()
    os.chdir(HERE)

    def one(s):
        try:
            a = analysis(s["bot"], s["symbol"])
            return {"bot": s["bot"], "symbol": s["symbol"], "timeframe": s["timeframe"],
                    "headline": a["headline"], "mood": a["mood"], "sides": a["sides"],
                    "close": a["close"], "bar_time": a["bar_time"], "next_decision": a["next_decision"],
                    "spark": [c[4] for c in a["candles"][-48:]], "label": a["label"]}
        except Exception as e:
            return {"bot": s["bot"], "symbol": s["symbol"], "timeframe": s["timeframe"],
                    "error": str(e)[:200], "label": s["label"]}

    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(one, strategy_slots(cfg)))


# --- SiGen ------------------------------------------------------------------------
# Signals are for trading anywhere, so they read the real OKX market (public data),
# not the demo prices the bots trade at.
_prod_client = None


def prod_client(cfg: Config):
    global _prod_client
    with _client_lock:
        if _prod_client is None:
            import ccxt
            _prod_client = ccxt.okx({"enableRateLimit": True, "hostname": cfg.okx_hostname, "timeout": 10000})
        return _prod_client


def sigen_fetch(symbol: str, tf: str, bars: int):
    from bot.data import fetch_closed
    return cached(("prod-candles", symbol, tf, bars), 240,
                  lambda: fetch_closed(prod_client(Config()), symbol, tf, bars))


def sigen_status() -> dict:
    from bot import sigen
    prog = sigen.read(HERE, "progress.json") or {"state": "never"}
    if prog.get("state") == "running" and not is_held(sigen.path(HERE, "scan")):
        prog = {**prog, "state": "error", "error": "The scan stopped before it finished. "
                + " ".join(tail(os.path.join(HERE, "logs", "sigen_scan.out"), 1))}
    scan = sigen.read(HERE, "scan.json")
    from bot import sigen_regime
    rg = sigen_regime.load(HERE)
    regime = {k: rg.get(k) for k in ("enabled", "reason", "rule", "shadow", "trades", "trend_trades", "from", "to",
                                     "calibrate_until", "checks", "generated_at")}
    if rg.get("validation"):
        v = rg["validation"]
        regime["validation"] = {k: v[k] for k in ("all", "kept", "held_back", "gain_r", "luck_beaten_pct")}
    if rg.get("replay", {}).get("signals"):
        regime["replay"] = rg["replay"]
    return {"terms": sigen.acceptance(HERE), "terms_text": sigen.TERMS, "scan": prog, "regime": regime if rg else None,
            "generated_at": scan.get("generated_at"), "coins": scan.get("coins", [])}


def sigen_signals(market: str) -> dict:
    """Cached per 4h candle (and per scan), so every page load doesn't refetch 25 coins."""
    from bot import sigen
    if market not in sigen.MARKETS:
        raise LookupError(f"unknown market {market}")
    scan_file = sigen.path(HERE, "scan.json")
    mtime = os.path.getmtime(scan_file) if os.path.exists(scan_file) else 0
    bar = int(time.time() // (4 * 3600))
    return cached(("sigen", market, bar, mtime), 4 * 3600,
                  lambda: sigen.live(market, HERE, fetch=sigen_fetch))


def sigen_chart(market: str, coin: str) -> dict:
    from bot import sigen
    from bot.explain import analyse
    from bot.strategies import StrategySpec, warmup_bars
    res = next((r for r in sigen.read(HERE, "scan.json").get("results", [])
                if r["market"] == market and r["coin"] == coin and r.get("chosen")), None)
    if res is None:
        raise LookupError(f"no SiGen strategy for {coin} {market}")
    spec = StrategySpec.from_dict(res["chosen"]["spec"])
    df = sigen_fetch(res["symbol"], sigen.TIMEFRAME, warmup_bars(spec) + 300)
    a = analyse(df, spec, sigen.TIMEFRAME, bars=160)
    for item in a["lines"] + a["panes"]:   # chart legend in the same plain words as the signal
        item["name"] = sigen.plain(item["name"])
    a.update({"bot": market, "symbol": res["symbol"], "timeframe": sigen.TIMEFRAME, "label": spec.label(),
              "fills": []})
    return a


def sigen_record() -> int:
    """Log this candle's new signals in both markets (bot/sigen_journal.py)."""
    from bot import sigen, sigen_journal
    if not os.path.exists(sigen.path(HERE, "scan.json")):
        return 0
    added = 0
    for m in sigen.MARKETS:
        res = sigen_signals(m)
        added += len(sigen_journal.record(res.get("signals", []), HERE, scan_at=res.get("generated_at")))
    return added


def sigen_recorder() -> None:
    """Background thread: after every 4h close, compute and log the signals, whether or not
    anyone has the page open, so the journal has every signal as it was issued."""
    last = None
    while True:
        bar = int(time.time() // (4 * 3600))
        if bar != last and time.time() - bar * 4 * 3600 > 90:   # give OKX a moment to close the candle
            try:
                sigen_record()
                last = bar
            except Exception as e:  # network blips: try again next minute
                print(f"SiGen recorder: {e!r}"[:200])
        time.sleep(60)


def sigen_journal_report() -> dict:
    from bot import sigen, sigen_journal
    jf = sigen.path(HERE, sigen_journal.FILE)
    mtime = os.path.getmtime(jf) if os.path.exists(jf) else 0
    return cached(("sigen-journal", mtime, int(time.time() // 300)), 300,
                  lambda: sigen_journal.report(HERE, fetch=sigen_fetch))


def start_sigen_scan() -> dict:
    from bot import sigen
    if is_held(sigen.path(HERE, "scan")):
        return {"ok": True, "message": "A scan is already running."}
    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    out = open(os.path.join(HERE, "logs", "sigen_scan.out"), "a", encoding="utf-8")
    out.write(f"\n--- scan started from the console {datetime.now(timezone.utc).isoformat()} ---\n")
    out.flush()
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
    subprocess.Popen([sys.executable, "-m", "bot.sigen", "scan"], cwd=HERE, stdout=out, stderr=subprocess.STDOUT,
                     stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
    for _ in range(40):
        time.sleep(0.25)
        if is_held(sigen.path(HERE, "scan")):
            return {"ok": True, "message": "Scan started. It takes a few minutes."}
    return {"ok": False, "message": "The scan didn't start. " + " ".join(tail(os.path.join(HERE, "logs", "sigen_scan.out"), 2))}


# --- controls -----------------------------------------------------------------
def start_bot(bot: str) -> dict:
    cfg = Config()
    state_file = cfg.state_file if bot == "spot" else cfg.fut_state_file
    if is_held(os.path.join(HERE, state_file)):
        return {"ok": True, "message": f"The {bot} bot is already running."}
    if not cfg.demo:
        return {"ok": False, "message": "DEMO=false in .env; the console only starts demo bots."}
    control.clear_stop(bot, HERE)
    out = open(os.path.join(HERE, cfg.log_dir, f"{bot}.out"), "a", encoding="utf-8")
    out.write(f"\n--- started from the console {datetime.now(timezone.utc).isoformat()} ---\n")
    out.flush()
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
    subprocess.Popen([sys.executable, "-m", BOT_MODULES[bot]], cwd=HERE, stdout=out, stderr=subprocess.STDOUT,
                     stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
    for _ in range(40):  # it takes the lock once its checks pass
        time.sleep(0.25)
        if is_held(os.path.join(HERE, state_file)):
            return {"ok": True, "message": f"The {bot} bot started."}
    lines = tail(os.path.join(HERE, cfg.log_dir, f"{bot}.out"), 4)
    return {"ok": False, "message": f"The {bot} bot didn't start. " + (lines[-1] if lines else "")}


def stop_bot(bot: str, force: bool = False) -> dict:
    cfg = Config()
    state_file = os.path.join(HERE, cfg.state_file if bot == "spot" else cfg.fut_state_file)
    if not is_held(state_file):
        control.clear_stop(bot, HERE)
        return {"ok": True, "message": f"The {bot} bot isn't running."}
    if force:
        pid = control.read_heartbeat(bot, HERE).get("pid")
        if not pid:
            return {"ok": False, "message": "No process id known for this bot; stop it in its own window."}
        try:
            os.kill(int(pid), signal.SIGTERM)  # on Windows this is TerminateProcess
        except OSError as e:
            return {"ok": False, "message": f"Couldn't end process {pid}: {e}"}
        control.clear_stop(bot, HERE)
        return {"ok": True, "message": f"Process {pid} ended."}
    control.request_stop(bot, HERE)
    for _ in range(60):  # the bot checks every second between polls
        time.sleep(0.5)
        if not is_held(state_file):
            return {"ok": True, "message": f"The {bot} bot stopped."}
    return {"ok": True, "pending": True,
            "message": f"Stop requested; the {bot} bot will stop when its current poll finishes."}


def set_kill(on: bool) -> dict:
    cfg = Config()
    path = os.path.join(HERE, cfg.kill_file)
    if on:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"engaged from the console {datetime.now(timezone.utc).isoformat()}\n")
    elif os.path.exists(path):
        os.remove(path)
    return {"ok": True, "message": "New entries paused." if on else "New entries allowed again."}


def close_position(bot: str, symbol: str) -> dict:
    cfg = Config()
    state_file = os.path.join(HERE, cfg.state_file if bot == "spot" else cfg.fut_state_file)
    if not is_held(state_file):
        return {"ok": False, "message": f"The {bot} bot isn't running, so it can't close the position. "
                                        "Start it first (its stop stays in place meanwhile)."}
    control.request_close(bot, symbol, HERE)
    for _ in range(60):
        time.sleep(0.5)
        if not control.close_requested(bot, symbol, HERE):
            return {"ok": True, "message": f"{symbol} close sent by the {bot} bot."}
    return {"ok": True, "pending": True, "message": "Close requested; the bot will do it on its next check."}


def assess_target(usd: float, funds: float | None) -> dict:
    from bot.target import assess
    cfg = Config()
    os.chdir(HERE)
    slots = strategy_slots(cfg)
    if not funds:
        funds = control.read_heartbeat("futures", HERE).get("equity") or 0
    daily = min(cfg.max_daily_loss_usd + cfg.fut_max_daily_loss_usd, 10 ** 9)
    return assess(usd, float(funds), slots, daily)


# --- HTTP -----------------------------------------------------------------------
def lan_token() -> str:
    tok = control.read_json(TOKEN_FILE).get("token")
    if not tok:
        tok = secrets.token_urlsafe(18)
        control.write_json(TOKEN_FILE, {"token": tok})
    return tok


class Handler(BaseHTTPRequestHandler):
    token: str | None = None   # set when serving on the LAN

    def _send(self, code: int, body: bytes, ctype: str, extra: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, data) -> None:
        # numpy scalars (np.bool_, np.float64) become plain JSON values, not strings like "False"
        self._send(code, json.dumps(data, default=lambda o: o.item() if hasattr(o, "item") else str(o)).encode(),
                   "application/json")

    def _local(self) -> bool:
        return self.client_address[0] in ("127.0.0.1", "::1")

    def _authorised(self, query: dict) -> bool:
        if self._local() or not self.token:
            return True
        cookie = self.headers.get("Cookie", "")
        got = (query.get("token", [None])[0] or self.headers.get("X-Token")
               or dict(c.strip().split("=", 1) for c in cookie.split(";") if "=" in c).get("tp_token"))
        return bool(got) and secrets.compare_digest(got, self.token)

    def do_GET(self):  # noqa: N802
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if not self._authorised(q):
            return self._send(401, b"Open the link with ?token=... shown in the console window.", "text/plain")
        extra = {}
        if q.get("token") and self.token:
            extra["Set-Cookie"] = f"tp_token={self.token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=31536000"
        try:
            if url.path == "/api/status":
                return self._json(200, status())
            if url.path == "/api/trades":
                return self._json(200, all_trades())
            if url.path == "/api/activity":
                return self._json(200, all_activity())
            if url.path == "/api/analysis":
                return self._json(200, analysis(q["bot"][0], q["symbol"][0], trade_id=q.get("trade", [None])[0]))
            if url.path == "/api/overview":
                return self._json(200, analysis_overview())
            if url.path == "/api/target/assess":
                funds = q.get("funds", [None])[0]
                return self._json(200, assess_target(float(q["usd"][0]), float(funds) if funds else None))
            if url.path == "/api/sigen":
                return self._json(200, sigen_status())
            if url.path in ("/api/sigen/signals", "/api/sigen/chart", "/api/sigen/journal", "/api/sigen/journal.csv"):
                from bot import sigen
                if not sigen.acceptance(HERE)["accepted"]:  # signals only after the declaration
                    return self._json(403, {"error": "accept the SiGen terms first"})
                if url.path == "/api/sigen/signals":
                    res = sigen_signals(q["market"][0])
                    from bot import sigen_journal
                    sigen_journal.record(res.get("signals", []), HERE, scan_at=res.get("generated_at"))
                    return self._json(200, res)
                if url.path == "/api/sigen/journal":
                    return self._json(200, sigen_journal_report())
                if url.path == "/api/sigen/journal.csv":
                    from bot import sigen_journal
                    body = sigen_journal.to_csv(sigen_journal_report()["signals"]).encode()
                    name = f"sigen-signal-report-{datetime.now(timezone.utc):%Y%m%d}.csv"
                    return self._send(200, body, "text/csv; charset=utf-8",
                                      {"Content-Disposition": f'attachment; filename="{name}"'})
                return self._json(200, sigen_chart(q["market"][0], q["coin"][0]))
        except LookupError as e:
            return self._json(404, {"error": str(e)})
        except Exception as e:  # show the problem on the page instead of a blank screen
            return self._json(500, {"error": repr(e)[:300]})
        self._static(url.path, extra)

    def do_POST(self):  # noqa: N802
        url = urlparse(self.path)
        if not self._authorised(parse_qs(url.query)):
            return self._json(401, {"error": "not authorised"})
        # a custom header can't be sent cross-site without a CORS preflight, which we never
        # answer: so another website open in the browser can't press these buttons
        if self.headers.get("X-Tradepilot") != "1":
            return self._json(403, {"error": "missing X-Tradepilot header"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except json.JSONDecodeError:
            return self._json(400, {"error": "bad JSON"})
        m = re.fullmatch(r"/api/bots/(spot|futures)/(start|stop|force-stop)", url.path)
        try:
            if m:
                bot, action = m.groups()
                res = start_bot(bot) if action == "start" else stop_bot(bot, force=action == "force-stop")
                return self._json(200, res)
            if url.path == "/api/kill":
                return self._json(200, set_kill(bool(body.get("on"))))
            if url.path == "/api/positions/close":
                if body.get("bot") not in BOT_MODULES or not body.get("symbol"):
                    return self._json(400, {"error": "bot and symbol required"})
                return self._json(200, close_position(body["bot"], str(body["symbol"])))
            if url.path == "/api/target":
                usd = body.get("daily_target_usd")
                usd = float(usd) if usd not in (None, "", 0) else None
                if usd is not None and usd <= 0:
                    return self._json(400, {"error": "target must be positive"})
                control.set_target(usd, bool(body.get("close_open")), HERE)
                return self._json(200, {"ok": True, "message": f"Daily target set to ${usd:,.2f}." if usd
                                        else "Daily target cleared."})
            if url.path == "/api/sigen/accept":
                from bot import sigen
                try:
                    sigen.accept(str(body.get("name", "")), list(body.get("statements") or []),
                                 str(body.get("version", "")), HERE)
                except ValueError as e:
                    return self._json(400, {"error": str(e)})
                return self._json(200, {"ok": True, "message": "Terms accepted. Welcome to SiGen."})
            if url.path == "/api/sigen/scan":
                return self._json(200, start_sigen_scan())
            if url.path == "/api/sigen/backfill":
                from bot import sigen_journal
                days = max(1, min(90, int(body.get("days") or 30)))
                n = sigen_journal.backfill(HERE, days, fetch=sigen_fetch)
                return self._json(200, {"ok": True, "message": f"Replayed {n} signal{'s' if n != 1 else ''} "
                                        f"from the last {days} days." if n else "No new signals to replay."})
        except Exception as e:
            return self._json(500, {"error": repr(e)[:300]})
        self._json(404, {"error": "unknown action"})

    def _static(self, path: str, extra: dict) -> None:
        if not os.path.isdir(DIST):
            return self._send(503, b"The console isn't built yet: run `npm install` and `npm run build` in web/.",
                              "text/plain")
        rel = os.path.normpath(path.lstrip("/")) if path not in ("", "/") else "index.html"
        full = os.path.join(DIST, rel)
        if rel.startswith("..") or not os.path.isfile(full):
            full = os.path.join(DIST, "index.html")  # single-page app: unknown paths get the app
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype.endswith("javascript"):
            ctype += "; charset=utf-8"
        with open(full, "rb") as f:
            body = f.read()
        if full.endswith("index.html"):
            self._send(200, body, ctype, extra)
        else:  # hashed asset names: safe to cache
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):  # keep the console quiet
        pass


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no traffic is sent; picks the outward interface
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> None:
    os.chdir(HERE)
    lan = "--lan" in sys.argv
    if lan:
        Handler.token = lan_token()
    server = ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Tradepilot console at {url}  (Ctrl-C to stop)")
    if lan:
        print(f"On your phone (same Wi-Fi): http://{lan_ip()}:{PORT}/?token={Handler.token}")
        print("Keep that link private: it can start and stop the bots.")
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=sigen_recorder, daemon=True, name="sigen-recorder").start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
