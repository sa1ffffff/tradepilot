"""The futures (perpetual swap) demo loop: long and short, isolated margin.

Runs the strategy in FUT_STRATEGY_FILE (written by `research.py --market swap
--save`). Each poll:
1. syncs with OKX: if the position is gone, the exchange stop/take-profit (or a
   liquidation) closed it -- record OKX's realised P&L;
2. makes sure an open position has its stop-loss resting on OKX, re-placing it
   if missing;
3. on a closed bar: exits on the opposite signal (and may reverse), or enters
   if flat and the risk gate allows.

Safety rules:
- every entry is sized by bot.futures.plan: FUT_RISK_FRACTION of equity lost at
  the stop, leverage from volatility (liquidation >= FUT_LIQ_BUFFER x the stop
  distance, at most FUT_MAX_LEVERAGE), margin <= FUT_MAX_MARGIN_FRACTION of equity;
- a position is never left without its exchange stop: if placing it fails, the
  position is closed at once;
- the bot only manages its own position; if one it didn't open exists on the
  symbol, it doesn't trade until that is gone;
- KILL file blocks new entries; the daily loss limit (FUT_MAX_DAILY_LOSS_USD)
  blocks entries for the rest of the UTC day; DEMO=false is refused.

Run:  python -m bot.futures_runner
"""
from __future__ import annotations

import dataclasses
import json
import os
import time
from datetime import datetime, timezone

from config import Config
from bot.costs import too_costly
from bot.futures import futures_cfg, plan
from bot.futures_exchange import OkxFutures
from bot.log import get_logger
from bot.risk import RiskManager
from bot.runner import kill_engaged, load_state, save_state
from bot.strategies import StrategySpec, signals_ls, warmup_bars


def load_futures_strategy(cfg: Config) -> tuple[Config, StrategySpec]:
    if not os.path.exists(cfg.strategy_file):
        raise SystemExit(f"No futures strategy at {cfg.strategy_file}. Run "
                         "`python research.py --market swap --save` or set FUT_STRATEGY_FILE.")
    with open(cfg.strategy_file, encoding="utf-8") as f:
        d = json.load(f)
    cfg = dataclasses.replace(cfg, symbol=d.get("symbol", cfg.symbol),
                              timeframe=d.get("timeframe", cfg.timeframe),
                              max_cost_per_r=d.get("max_cost_per_r", cfg.max_cost_per_r))
    if ":" not in cfg.symbol:
        raise SystemExit(f"{cfg.strategy_file} is a spot strategy ({cfg.symbol}); "
                         "use one researched with --market swap.")
    return cfg, StrategySpec.from_dict(d)


def record_close(ex, risk, state, log, reason: str, fill: dict | None = None) -> None:
    pos = state["position"]
    res = ex.closed_pnl(pos["opened_ms"])
    if res is not None:
        pnl, px, kind = res["pnl"], res["close_price"], res["kind"]
    else:  # OKX history not available yet: estimate from our own fills
        px = (fill or {}).get("average") or pos["entry"]
        pnl = pos["dir"] * (px - pos["entry"]) * pos["size"] - pos["entry_fee"] - \
            (fill or {}).get("fee_quote", 0.0)
        kind = "estimated"
    risk.record_pnl(pnl)
    state["position"] = None
    state["risk"] = risk.to_dict()
    save_state(state["_path"], state)
    log.info("exit_filled", {"reason": reason, "result": kind, "side": pos["side"],
                             "entry": pos["entry"], "price": px, "size": pos["size"],
                             "leverage": pos["leverage"], "pnl": round(pnl, 4),
                             "pnl_today": round(risk.realized_pnl_today, 4),
                             "maker_share": round((fill or {}).get("maker_share", 0.0), 3)})


def close_position(ex, risk, state, log, reason: str) -> None:
    pos = state["position"]
    ex.cancel_protection()
    live = ex.position()
    fill = None
    if live is not None:
        fill = ex.close(live["dir"], live["contracts"])
    record_close(ex, risk, state, log, reason, fill)


def open_position(cfg, spec, ex, risk, state, log, direction: int, bar) -> None:
    side = "long" if direction > 0 else "short"
    bar_time = bar["time"].isoformat()
    price, dist = float(bar["close"]), spec.stop_atr * float(bar["atr"])
    reason = None
    if kill_engaged(cfg):
        reason = "kill switch engaged"
    elif risk.daily_loss_hit():
        reason = f"daily loss limit reached ({risk.realized_pnl_today:.2f})"
    elif not dist > 0 or too_costly(cfg, price, dist):
        reason = "stop too tight for trading costs"
    p = None if reason else plan(ex.equity_quote(), price, dist, direction, cfg)
    contracts = ex.to_contracts(p.size) if p else 0.0
    if not reason and (p is None or contracts < ex.min_contracts):
        reason = "position below minimum size"
    if reason:
        log.info("entry_skipped", {"side": side, "reason": reason, "bar": bar_time, "price": price})
        return

    ex.set_leverage(p.leverage)
    opened_ms = int(time.time() * 1000)
    fill = ex.open(direction, contracts)
    if fill["filled"] <= 0:
        log.error("entry_unfilled", {"side": side, "id": fill["id"], "status": fill["status"]})
        return
    entry = fill["average"] or price
    stop = entry - direction * dist
    tp = entry + direction * spec.tp_r * dist if spec.tp_r else None
    state["position"] = {
        "dir": direction, "side": side, "entry": entry, "size": fill["size"],
        "contracts": fill["filled"], "stop": stop, "tp": tp, "leverage": p.leverage,
        "entry_fee": fill["fee_quote"], "opened": bar_time, "opened_ms": opened_ms,
    }
    save_state(state["_path"], state)
    try:
        ex.place_protection(direction, stop, tp)
    except Exception as e:  # never hold a position without its stop
        log.error("stop_failed_closing", {"side": side, "error": repr(e)})
        close_position(ex, risk, state, log, "stop placement failed")
        return

    live = ex.position() or {}
    if live.get("liq") and direction * (stop - live["liq"]) <= 0:
        log.error("liq_inside_stop_closing", {"stop": stop, "liq_price": live["liq"]})
        close_position(ex, risk, state, log, "liquidation price inside stop")
        return
    log.info("entry_filled", {"side": side, "bar": bar_time, "size": fill["size"],
                              "contracts": fill["filled"], "price": entry, "signal_close": price,
                              "stop": round(stop, 2), "tp": round(tp, 2) if tp else None,
                              "leverage": p.leverage, "margin": round(live.get("margin") or p.margin, 2),
                              "liq_price": live.get("liq") or round(p.liq_price, 2),
                              "risk_usd": round(fill["size"] * dist, 2),
                              "maker_share": round(fill["maker_share"], 3), "id": fill["id"]})


def step(cfg: Config, spec: StrategySpec, ex: OkxFutures, risk: RiskManager, state: dict,
         log) -> None:
    risk.roll_day(datetime.now(timezone.utc).date())
    pos = state["position"]
    live = ex.position()

    # 1. sync with the exchange
    if pos is not None and live is None:
        record_close(ex, risk, state, log, "exchange stop/tp")
        pos = None
    elif pos is None and live is not None:
        if not state.get("foreign_warned"):
            log.warning("foreign_position", {"side": "long" if live["dir"] > 0 else "short",
                                             "size": live["size"],
                                             "note": "not opened by the bot; not trading until it's closed"})
            state["foreign_warned"] = True
        return
    state.pop("foreign_warned", None)

    # 2. the stop must be resting on OKX
    if pos is not None and not ex.pending_protection():
        log.warning("stop_missing_replacing", {"stop": pos["stop"]})
        try:
            ex.place_protection(pos["dir"], pos["stop"], pos.get("tp"))
        except Exception as e:
            log.error("stop_failed_closing", {"error": repr(e)})
            close_position(ex, risk, state, log, "stop placement failed")
            return

    # 3. signals on the last closed bar
    sig = signals_ls(ex.fetch_closed_ohlcv(warmup_bars(spec)), spec)
    if len(sig) < 2:
        return
    bar = sig.iloc[-1]
    key = f"{bar['time'].isoformat()}"
    if risk.is_duplicate(key):
        return

    long_in, short_in = bool(bar["entry"]), bool(bar["short_entry"])
    if pos is not None:
        d = pos["dir"]
        if (d > 0 and (bar["exit"] or short_in)) or (d < 0 and (bar["short_exit"] or long_in)):
            risk.remember(key)
            close_position(ex, risk, state, log, "signal")
            pos = None
            if not (long_in or short_in):
                return
        else:
            return
    if pos is None and (long_in or short_in):
        risk.remember(key)
        state["risk"] = risk.to_dict()
        save_state(state["_path"], state)
        open_position(cfg, spec, ex, risk, state, log, 1 if long_in else -1, bar)


def main() -> None:
    import ccxt

    base = Config()
    if not base.demo and os.getenv("I_UNDERSTAND_THIS_IS_REAL_MONEY") != "yes":
        raise SystemExit("DEMO=false would trade real money. Futures run on demo only.")
    cfg, spec = load_futures_strategy(futures_cfg(base))
    log = get_logger(cfg.log_dir, "futures")
    ex = OkxFutures(cfg)
    ok, msg = ex.account_mode_ok()
    if not ok:
        raise SystemExit(msg)
    risk = RiskManager(cfg)
    state = load_state(cfg.state_file)
    state["_path"] = cfg.state_file
    risk.load_dict(state.get("risk", {}))

    log.info("started", {"symbol": cfg.symbol, "timeframe": cfg.timeframe, "demo": cfg.demo,
                         "strategy": spec.label(), "risk_per_trade": cfg.fut_risk_fraction,
                         "max_leverage": cfg.fut_max_leverage,
                         "max_margin": cfg.fut_max_margin_fraction, "position": state["position"]})
    try:
        while True:
            try:
                step(cfg, spec, ex, risk, state, log)
            except ccxt.NetworkError as e:  # internet/OKX blip: one line, try again next poll
                log.warning("network_error", {"error": str(e)[:200]})
            except Exception:
                log.exception("error", {})
            time.sleep(cfg.poll_seconds)
    except KeyboardInterrupt:
        log.info("stopped", {"position": state["position"]})


if __name__ == "__main__":
    main()
