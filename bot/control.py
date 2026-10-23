"""Requests from the dashboard to a running bot, and the bot's heartbeat back.

The dashboard never talks to OKX with the account keys. To stop a bot or close
a position it drops a small file in control/; the bot picks it up on its next
poll, acts through its own code path (so state, P&L and stops stay consistent)
and deletes the file. Files rather than one shared JSON so the dashboard and
two bots can never overwrite each other's requests.

    control/stop_<bot>            stop the bot after the current poll
    control/close_<bot>_<symbol>  market-close that position now
    control/target.json           {"daily_target_usd": 15, "close_open": false}
    control/heartbeat_<bot>.json  written by the bot: pid, last poll, equity
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

DIR = "control"
BOTS = ("spot", "futures")


def _path(name: str, root: str = ".") -> str:
    return os.path.join(root, DIR, name)


def _sym(symbol: str) -> str:
    return symbol.replace("/", "-").replace(":", "_")


def write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


# --- stop ---------------------------------------------------------------------
def request_stop(bot: str, root: str = ".") -> None:
    write_json(_path(f"stop_{bot}", root), {"ts": datetime.now(timezone.utc).isoformat()})


def stop_requested(bot: str, root: str = ".") -> bool:
    return os.path.exists(_path(f"stop_{bot}", root))


def clear_stop(bot: str, root: str = ".") -> None:
    try:
        os.remove(_path(f"stop_{bot}", root))
    except FileNotFoundError:
        pass


# --- close a position ---------------------------------------------------------
def request_close(bot: str, symbol: str, root: str = ".") -> None:
    write_json(_path(f"close_{bot}_{_sym(symbol)}", root),
               {"symbol": symbol, "ts": datetime.now(timezone.utc).isoformat()})


def close_requested(bot: str, symbol: str, root: str = ".") -> bool:
    return os.path.exists(_path(f"close_{bot}_{_sym(symbol)}", root))


def clear_close(bot: str, symbol: str, root: str = ".") -> None:
    try:
        os.remove(_path(f"close_{bot}_{_sym(symbol)}", root))
    except FileNotFoundError:
        pass


def pending_closes(root: str = ".") -> list[dict]:
    d = os.path.join(root, DIR)
    if not os.path.isdir(d):
        return []
    out = []
    for name in os.listdir(d):
        if name.startswith("close_") and not name.endswith(".tmp"):
            req = read_json(os.path.join(d, name))
            out.append({"bot": name.split("_")[1], "symbol": req.get("symbol"), "ts": req.get("ts")})
    return out


# --- daily profit target ------------------------------------------------------
def target(root: str = ".") -> dict:
    """{"daily_target_usd": float | None, "close_open": bool}"""
    t = read_json(_path("target.json", root))
    usd = t.get("daily_target_usd")
    return {"daily_target_usd": float(usd) if usd else None,
            "close_open": bool(t.get("close_open", False)), "set_at": t.get("set_at")}


def set_target(usd: float | None, close_open: bool = False, root: str = ".") -> None:
    write_json(_path("target.json", root),
               {"daily_target_usd": usd, "close_open": close_open,
                "set_at": datetime.now(timezone.utc).isoformat()})


def pnl_today(state_file: str, day: str) -> float:
    """Realized P&L today from one bot's state file (0 if it's from another day)."""
    risk = read_json(state_file).get("risk", {})
    return float(risk.get("realized_pnl_today", 0.0)) if risk.get("day") == day else 0.0


def combined_pnl_today(own_pnl: float, other_state_file: str) -> float:
    day = datetime.now(timezone.utc).date().isoformat()
    return own_pnl + pnl_today(other_state_file, day)


def target_reached(combined_pnl: float, root: str = ".") -> float | None:
    """The target in USD if today's combined realized P&L has reached it, else None."""
    usd = target(root)["daily_target_usd"]
    return usd if usd and combined_pnl >= usd else None


# --- heartbeat ----------------------------------------------------------------
def heartbeat(bot: str, data: dict, root: str = ".") -> None:
    write_json(_path(f"heartbeat_{bot}.json", root),
               {"pid": os.getpid(), "ts": datetime.now(timezone.utc).isoformat(), **data})


def read_heartbeat(bot: str, root: str = ".") -> dict:
    return read_json(_path(f"heartbeat_{bot}.json", root))


def wait(seconds: float, bot: str, root: str = ".") -> None:
    """Sleep between polls, waking early when the dashboard asks for something,
    so Stop and Close act within a second instead of a whole poll later."""
    end = time.monotonic() + seconds
    d = os.path.join(root, DIR)
    while time.monotonic() < end:
        if os.path.isdir(d) and any(n == f"stop_{bot}" or n.startswith(f"close_{bot}_")
                                    for n in os.listdir(d)):
            return
        time.sleep(min(1.0, max(0.0, end - time.monotonic())))
