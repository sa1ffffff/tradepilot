"""The live demo loop.

Long/flat spot model running the strategy in strategy.json: an entry signal
opens a long if flat; an exit signal, the ATR stop or the take-profit closes
it. Every entry passes through the risk gate. A file named KILL in the working
directory stops new entries (create it to halt, delete it to resume); exits,
the stop and the take-profit keep working while it is engaged.

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
from bot.strategies import StrategySpec, default_spec, signals, warmup_bars


def kill_engaged(cfg: Config) -> bool:
    return os.path.exists(cfg.kill_file)


def load_strategy(cfg: Config) -> tuple[Config, StrategySpec]:
    """strategy.json (from research.py --save) if present, else the EMA fallback.
    The symbol and timeframe it was researched on override .env."""
    if not os.path.exists(cfg.strategy_file):
        return cfg, default_spec()
    with open(cfg.strategy_file, encoding="utf-8") as f:
        d = json.load(f)
    cfg = dataclasses.replace(cfg, symbol=d.get("symbol", cfg.symbol),
                              timeframe=d.get("timeframe", cfg.timeframe),
                              max_cost_per_r=d.get("max_cost_per_r", cfg.max_cost_per_r))
    return cfg, StrategySpec.from_dict(d)


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


def close_position(cfg, ex, risk, state, log, reason: str, price_hint: float, bar=None) -> None:
    pos = state["position"]
    held = ex.base_balance()
    amount = min(pos["size"], held)
    if amount < cfg.min_base_size:
        # sold manually / outside the bot -- nothing left for it to close
        log.warning("position_missing", {"tracked": pos["size"], "held": held})
        state["position"] = None
        save_state(cfg.state_file, state)
        return

    fill = ex.sell(amount, urgent=(reason == "stop"))
    exit_px = fill["average"] or price_hint
    pnl = (exit_px - pos["entry"]) * fill["filled"] - fill["fee_quote"] - pos["entry_fee"]
    risk.record_pnl(pnl)
    state["position"] = None
    state["risk"] = risk.to_dict()
    save_state(cfg.state_file, state)
    log.info("exit_filled", {"reason": reason, "bar": bar, "size": fill["filled"],
                             "price": exit_px, "entry": pos["entry"], "pnl": round(pnl, 4),
                             "pnl_today": round(risk.realized_pnl_today, 4),
                             "maker_share": round(fill.get("maker_share", 0.0), 3), "id": fill["id"]})


def step(cfg: Config, spec: StrategySpec, ex: OkxExchange, risk: RiskManager, state: dict,
         log) -> None:
    risk.roll_day(datetime.now(timezone.utc).date())
    pos = state["position"]

    # protective stop / take-profit: checked every poll, not just on bar close
    if pos is not None:
        last = ex.last_price()
        if last <= pos["stop"]:
            close_position(cfg, ex, risk, state, log, "stop", last)
            return
        if pos.get("tp") and last >= pos["tp"]:
            close_position(cfg, ex, risk, state, log, "tp", last)
            return

    sig = signals(ex.fetch_closed_ohlcv(warmup_bars(spec)), spec)
    if len(sig) < 2:
        return
    bar = sig.iloc[-1]
    bar_time = bar["time"].isoformat()

    if pos is not None and bar["exit"]:
        close_position(cfg, ex, risk, state, log, "signal", float(bar["close"]), bar_time)

    elif pos is None and bar["entry"]:
        key = f"{bar_time}:entry"
        if risk.is_duplicate(key):
            return
        # remember (and persist) before ordering: if the order call errors after
        # OKX accepted it, a retry must not buy a second time
        risk.remember(key)
        state["risk"] = risk.to_dict()
        save_state(cfg.state_file, state)

        price, stop_distance = float(bar["close"]), spec.stop_atr * float(bar["atr"])
        decision = risk.evaluate_entry(price, stop_distance, ex.equity_quote(), kill_engaged(cfg))
        if not decision.allowed:
            log.info("entry_skipped", {"reason": decision.reason, "bar": bar_time, "price": price})
            return

        fill = ex.buy(decision.size)
        if fill["filled"] <= 0:
            log.error("entry_unfilled", {"id": fill["id"], "status": fill["status"]})
            return
        entry_px = fill["average"] or price
        state["position"] = {
            "entry": entry_px,
            "size": fill["filled"] - fill["fee_base"],  # OKX takes spot buy fees in base ccy
            "stop": entry_px - stop_distance,
            "tp": entry_px + spec.tp_r * stop_distance if spec.tp_r else None,
            "entry_fee": fill["fee_quote"],
            "opened": bar_time,
        }
        save_state(cfg.state_file, state)
        log.info("entry_filled", {"bar": bar_time, "size": state["position"]["size"],
                                  "price": entry_px, "signal_close": price,
                                  "stop": state["position"]["stop"], "tp": state["position"]["tp"],
                                  "maker_share": round(fill.get("maker_share", 0.0), 3),
                                  "id": fill["id"]})


def main() -> None:
    cfg, spec = load_strategy(Config())
    if not cfg.demo and os.getenv("I_UNDERSTAND_THIS_IS_REAL_MONEY") != "yes":
        raise SystemExit("DEMO=false would trade real money. Phase 1 is demo only; set DEMO=true.")
    log = get_logger(cfg.log_dir)
    ex = OkxExchange(cfg)
    cfg = dataclasses.replace(cfg, min_base_size=ex.min_amount())
    risk = RiskManager(cfg)
    state = load_state(cfg.state_file)
    risk.load_dict(state.get("risk", {}))

    log.info("started", {"symbol": cfg.symbol, "timeframe": cfg.timeframe, "demo": cfg.demo,
                         "strategy": spec.label(), "position": state["position"]})
    if not cfg.demo:
        log.warning("LIVE MODE -- real money", {})

    try:
        while True:
            try:
                step(cfg, spec, ex, risk, state, log)
            except Exception:  # keep the loop alive; one bad poll shouldn't kill the bot
                log.exception("error", {})
            time.sleep(cfg.poll_seconds)
    except KeyboardInterrupt:
        log.info("stopped", {})


if __name__ == "__main__":
    main()
