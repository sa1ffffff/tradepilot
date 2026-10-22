"""A local dashboard for both bots. Read-only: it never places, changes or
cancels anything, and never reads API keys.

    python dashboard.py            # then open http://127.0.0.1:8765
    (or double-click start_dashboard.bat)

Every click of Update re-reads the logs and state files and fetches the
latest OKX demo prices (public data) to value open positions.
"""
from __future__ import annotations

import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from config import Config
from bot.lock import is_held

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8765


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


def trades(events: list[dict], bot: str, default_symbol: str) -> list[dict]:
    """Closed trades from exit_filled events, newest first."""
    out = []
    for e in events:
        if e.get("msg") != "exit_filled":
            continue
        out.append({
            "time": e["ts"], "bot": bot, "symbol": e.get("symbol", default_symbol),
            "side": e.get("side", "long"), "entry": e.get("entry"), "exit": e.get("price"),
            "pnl": e.get("pnl", 0.0), "reason": e.get("reason", ""),
        })
    return out[::-1]


def summarise(closed: list[dict], since: datetime) -> dict:
    pnls = [t["pnl"] for t in closed if datetime.fromisoformat(t["time"]) >= since]
    wins = sum(p > 0 for p in pnls)
    return {"pnl": round(sum(pnls), 2), "trades": len(pnls), "wins": wins}


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


def live_prices(cfg, symbols: list[str]) -> dict:
    """Last OKX demo price per symbol, or {} if OKX can't be reached."""
    if not symbols:
        return {}
    try:
        import ccxt
        client = ccxt.okx({"enableRateLimit": True, "hostname": cfg.okx_hostname, "timeout": 8000})
        if cfg.demo:
            client.set_sandbox_mode(True)  # demo prices, which is what the bots trade at
        return {s: float(client.fetch_ticker(s)["last"]) for s in symbols}
    except Exception:
        return {}


def status() -> dict:
    cfg = Config()
    os.chdir(HERE)
    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    spot_log = read_log(os.path.join(cfg.log_dir, "bot.log"))
    fut_log = read_log(os.path.join(cfg.log_dir, "futures.log"))
    spot_state = read_json(cfg.state_file)
    fut_state = read_json(cfg.fut_state_file)
    spot_start, fut_start = last_started(spot_log), last_started(fut_log)
    spot_symbol = (spot_start or {}).get("symbol", cfg.symbol)

    positions = []
    sp = spot_state.get("position")
    if sp:
        positions.append({"bot": "Spot", "symbol": spot_symbol, "side": "long", "dir": 1,
                          "entry": sp["entry"], "size": sp["size"], "stop": sp["stop"],
                          "leverage": 1, "opened": sp.get("opened")})
    for sym, slot in (fut_state.get("slots") or {}).items():
        p = slot.get("position")
        if p:
            positions.append({"bot": "Futures", "symbol": sym, "side": p["side"], "dir": p["dir"],
                              "entry": p["entry"], "size": p["size"], "stop": p["stop"],
                              "leverage": p.get("leverage", 1), "opened": p.get("opened")})
    prices = live_prices(cfg, sorted({p["symbol"] for p in positions}))
    for p in positions:
        px = prices.get(p["symbol"])
        p["price"] = px
        p["unrealized"] = round(p["dir"] * (px - p["entry"]) * p["size"], 2) if px else None

    closed = sorted(trades(spot_log, "Spot", spot_symbol) + trades(fut_log, "Futures", ""),
                    key=lambda t: t["time"], reverse=True)
    spot_closed = [t for t in closed if t["bot"] == "Spot"]
    fut_closed = [t for t in closed if t["bot"] == "Futures"]
    errors_24h = [e for e in spot_log + fut_log
                  if e.get("level") in ("ERROR", "WARNING")
                  and datetime.fromisoformat(e["ts"]) >= now - timedelta(hours=24)]

    return {
        "now": now.isoformat(),
        "demo": cfg.demo,
        "bots": {
            "spot": {"running": is_held(cfg.state_file),
                     "since": (spot_start or {}).get("ts"),
                     "strategy": (spot_start or {}).get("strategy", ""),
                     "market": f"{spot_symbol} {(spot_start or {}).get('timeframe', '')}".strip()},
            "futures": {"running": is_held(cfg.fut_state_file),
                        "since": (fut_start or {}).get("ts"),
                        "slots": (fut_start or {}).get("strategies", [])},
        },
        "today": {"spot": summarise(spot_closed, day_start), "futures": summarise(fut_closed, day_start)},
        "all_time": {"spot": summarise(spot_closed, datetime.min.replace(tzinfo=timezone.utc)),
                     "futures": summarise(fut_closed, datetime.min.replace(tzinfo=timezone.utc))},
        "positions": positions,
        "prices_ok": bool(prices) or not positions,
        "trades": closed[:30],
        "errors_24h": len(errors_24h),
        "last_error": (errors_24h[-1].get("exc", "").strip().splitlines()
                       or [f'{errors_24h[-1]["msg"]} {errors_24h[-1].get("symbol", "")}'.strip()])[-1][:200]
        if errors_24h else None,
        "health": health_note(os.path.join(cfg.log_dir, "health.md")),
        "kill_switch": os.path.exists(cfg.kill_file),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "dashboard.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/status":
            try:
                self._send(200, json.dumps(status(), default=str).encode(), "application/json")
            except Exception as e:  # show the problem on the page instead of a blank screen
                self._send(500, json.dumps({"error": repr(e)}).encode(), "application/json")
        else:
            self._send(404, b"not found", "text/plain")

    def log_message(self, *args):  # keep the console quiet
        pass


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)  # this PC only
    url = f"http://127.0.0.1:{PORT}"
    print(f"Dashboard running at {url}  (Ctrl-C to stop)")
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
