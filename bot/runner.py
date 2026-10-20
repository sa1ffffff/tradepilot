"""The live demo loop.

Long/flat spot model: a buy signal opens a long if flat, a sell signal or the
ATR stop closes it. Every entry passes through the risk gate. A file named KILL
in the working directory stops new entries (create it to halt, delete it to
resume); exits and the stop keep working while it is engaged.

The bot tracks *its own* position in a state file instead of reading the wallet
balance: OKX demo accounts come pre-funded with BTC, and a manual holding must
never be mistaken for the bot's position (or sold by it). The state file also
keeps the daily loss counter across restarts.

Run:  python -m bot.runner      (from the project root, with .env filled in)
"""
from __future__ import annotations

import dataclasses
import json
import os
import time
from datetime import datetime, timezone

from config import Config
from bot.exchange import OkxExchange
from bot.log import get_logger
from bot.risk import RiskManager
from bot.strategy import generate_signal


def kill_engaged(cfg: Config) -> bool:
    return os.path.exists(cfg.kill_file)


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return {"position": None, "risk": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state(path: str, state: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)  # atomic: a crash mid-write can't leave a corrupt file


def close_position(cfg, ex, risk, state, log, reason: str, price_hint: float) -> None:
    pos = state["position"]
    held = ex.base_balance()
    amount = min(pos["size"], held)
    if amount < cfg.min_base_size:
        # sold manually / outside the bot -- nothing left for it to close
        log.warning("position_missing", {"tracked": pos["size"], "held": held})
        state["position"] = None
        save_state(cfg.state_file, state)
        return

    fill = ex.market_sell(amount)
    exit_px = fill["average"] or price_hint
    pnl = (exit_px - pos["entry"]) * fill["filled"] - fill["fee_quote"] - pos["entry_fee"]
    risk.record_pnl(pnl)
    state["position"] = None
    state["risk"] = risk.to_dict()
    save_state(cfg.state_file, state)
    log.info("exit_filled", {"reason": reason, "size": fill["filled"], "price": exit_px,
                             "pnl": round(pnl, 4), "pnl_today": round(risk.realized_pnl_today, 4),
                             "id": fill["id"]})


def step(cfg: Config, ex: OkxExchange, risk: RiskManager, state: dict, log) -> None:
    risk.roll_day(datetime.now(timezone.utc).date())
    pos = state["position"]

    # protective stop: checked every poll, not just on bar close
    if pos is not None:
        last = ex.last_price()
        if last <= pos["stop"]:
            close_position(cfg, ex, risk, state, log, "stop", last)
            return

    closed = ex.fetch_closed_ohlcv()
    sig = generate_signal(closed, cfg.ema_fast, cfg.ema_slow, cfg.atr_period)
    if sig is None:
        return

    if sig.action == "sell" and pos is not None:
        close_position(cfg, ex, risk, state, log, "signal", sig.price)

    elif sig.action == "buy" and pos is None:
        key = f"{sig.time.isoformat()}:buy"
        if risk.is_duplicate(key):
            return
        # remember (and persist) before ordering: if the order call errors after
        # OKX accepted it, a retry must not buy a second time
        risk.remember(key)
        state["risk"] = risk.to_dict()
        save_state(cfg.state_file, state)

        decision = risk.evaluate_entry(sig.price, sig.atr, ex.equity_quote(), kill_engaged(cfg))
        if not decision.allowed:
            log.info("entry_skipped", {"reason": decision.reason, "price": sig.price})
            return

        fill = ex.market_buy(decision.size)
        if fill["filled"] <= 0:
            log.error("entry_unfilled", {"id": fill["id"], "status": fill["status"]})
            return
        entry_px = fill["average"] or sig.price
        state["position"] = {
            "entry": entry_px,
            "size": fill["filled"] - fill["fee_base"],  # OKX takes spot buy fees in base ccy
            "stop": entry_px - decision.stop_distance,
            "entry_fee": fill["fee_quote"],
            "opened": sig.time.isoformat(),
        }
        save_state(cfg.state_file, state)
        log.info("entry_filled", {"size": state["position"]["size"], "price": entry_px,
                                  "stop": state["position"]["stop"], "id": fill["id"]})


def main() -> None:
    cfg = Config()
    log = get_logger(cfg.log_dir)
    ex = OkxExchange(cfg)
    cfg = dataclasses.replace(cfg, min_base_size=ex.min_amount())
    risk = RiskManager(cfg)
    state = load_state(cfg.state_file)
    risk.load_dict(state.get("risk", {}))

    log.info("started", {"symbol": cfg.symbol, "timeframe": cfg.timeframe, "demo": cfg.demo,
                         "position": state["position"]})
    if not cfg.demo:
        log.warning("LIVE MODE -- real money", {})

    try:
        while True:
            try:
                step(cfg, ex, risk, state, log)
            except Exception:  # keep the loop alive; one bad poll shouldn't kill the bot
                log.exception("error", {})
            time.sleep(cfg.poll_seconds)
    except KeyboardInterrupt:
        log.info("stopped", {})


if __name__ == "__main__":
    main()
