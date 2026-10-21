"""The futures (perpetual swap) demo loop: long and short, isolated margin.

Runs one or more strategies at once -- FUT_STRATEGY_FILE is a comma-separated
list of strategy files (from `research.py --market swap --save-all`), at most
one per symbol, since OKX nets positions per instrument. Each poll, for every
strategy:
1. syncs with OKX: if its position is gone, the exchange stop/take-profit (or a
   liquidation) closed it -- record OKX's realised P&L;
2. makes sure an open position has its stop-loss resting on OKX, re-placing it
   if missing;
3. on a closed bar: exits on the opposite signal (and may reverse), or enters
   if flat and the risk gate allows.

Safety rules:
- every entry is sized by bot.futures.plan: FUT_RISK_FRACTION of equity lost at
  the stop, leverage from volatility (liquidation >= FUT_LIQ_BUFFER x the stop
  distance, at most FUT_MAX_LEVERAGE), and margin across ALL open positions
  <= FUT_MAX_MARGIN_FRACTION of equity;
- a position is never left without its exchange stop: if placing it fails, the
  position is closed at once;
- the bot only manages its own positions; if one it didn't open exists on a
  symbol, that strategy doesn't trade until it is gone;
- KILL file blocks new entries; the shared daily loss limit
  (FUT_MAX_DAILY_LOSS_USD) blocks entries for the rest of the UTC day;
  DEMO=false is refused.

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
from bot.lock import acquire as acquire_lock
from bot.log import get_logger
from bot.risk import RiskManager
from bot.runner import kill_engaged
from bot.strategies import StrategySpec, signals_ls, warmup_bars


class Store:
    """state_futures.json: {"risk": {...}, "slots": {symbol: {"position": ...}}}.
    Written atomically after every change."""

    def __init__(self, path: str):
        self.path = path
        self.data = {"risk": {}, "slots": {}}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.data = json.load(f)
            self.data.setdefault("slots", {})

    def slot(self, symbol: str) -> dict:
        return self.data["slots"].setdefault(symbol, {"position": None})

    def margin_in_use(self, except_symbol: str | None = None) -> float:
        return sum((s.get("position") or {}).get("margin", 0.0)
                   for sym, s in self.data["slots"].items() if sym != except_symbol)

    def save(self, risk: RiskManager | None = None) -> None:
        if risk is not None:
            self.data["risk"] = risk.to_dict()
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        os.replace(tmp, self.path)


def load_futures_strategy(cfg: Config, path: str | None = None) -> tuple[Config, StrategySpec]:
    path = path or cfg.strategy_file
    if not os.path.exists(path):
        raise SystemExit(f"No futures strategy at {path}. Run "
                         "`python research.py --market swap --save-all` or set FUT_STRATEGY_FILE.")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    cfg = dataclasses.replace(cfg, strategy_file=path, symbol=d.get("symbol", cfg.symbol),
                              timeframe=d.get("timeframe", cfg.timeframe),
                              max_cost_per_r=d.get("max_cost_per_r", cfg.max_cost_per_r),
                              # a test slot can risk less than the researched ones
                              fut_risk_fraction=d.get("fut_risk_fraction", cfg.fut_risk_fraction))
    if ":" not in cfg.symbol:
        raise SystemExit(f"{path} is a spot strategy ({cfg.symbol}); "
                         "use one researched with --market swap.")
    return cfg, StrategySpec.from_dict(d)


def load_futures_strategies(cfg: Config) -> list[tuple[Config, StrategySpec]]:
    out = [load_futures_strategy(cfg, p.strip()) for p in cfg.strategy_file.split(",") if p.strip()]
    symbols = [c.symbol for c, _ in out]
    if len(set(symbols)) != len(symbols):
        raise SystemExit("FUT_STRATEGY_FILE has two strategies on the same symbol; OKX nets "
                         "positions per instrument, so use one strategy per symbol.")
    return out


def record_close(ex, risk, store, slot, log, reason: str, fill: dict | None = None) -> None:
    pos = slot["position"]
    res = ex.closed_pnl(pos["opened_ms"])
    if res is not None:
        pnl, px, kind = res["pnl"], res["close_price"], res["kind"]
    else:  # OKX history not available yet: estimate from our own fills
        px = (fill or {}).get("average") or pos["entry"]
        pnl = pos["dir"] * (px - pos["entry"]) * pos["size"] - pos["entry_fee"] - \
            (fill or {}).get("fee_quote", 0.0)
        kind = "estimated"
    risk.record_pnl(pnl)
    slot["position"] = None
    store.save(risk)
    log.info("exit_filled", {"symbol": ex.cfg.symbol, "reason": reason, "result": kind,
                             "side": pos["side"], "entry": pos["entry"], "price": px,
                             "size": pos["size"], "leverage": pos["leverage"], "pnl": round(pnl, 4),
                             "pnl_today": round(risk.realized_pnl_today, 4),
                             "maker_share": round((fill or {}).get("maker_share", 0.0), 3)})


def close_position(ex, risk, store, slot, log, reason: str) -> None:
    ex.cancel_protection()
    live = ex.position()
    fill = ex.close(live["dir"], live["contracts"]) if live is not None else None
    record_close(ex, risk, store, slot, log, reason, fill)


def open_position(cfg, spec, ex, risk, store, slot, log, direction: int, bar) -> None:
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
    p = None
    if not reason:
        p = plan(ex.equity_quote(), price, dist, direction, cfg,
                 margin_in_use=store.margin_in_use(except_symbol=cfg.symbol))
    contracts = ex.to_contracts(p.size) if p else 0.0
    if not reason and (p is None or contracts < ex.min_contracts):
        reason = "no margin room or position below minimum size"
    if reason:
        log.info("entry_skipped", {"symbol": cfg.symbol, "side": side, "reason": reason,
                                   "bar": bar_time, "price": price})
        return

    ex.set_leverage(p.leverage)
    opened_ms = int(time.time() * 1000)
    fill = ex.open(direction, contracts)
    if fill["filled"] <= 0:
        log.error("entry_unfilled", {"symbol": cfg.symbol, "side": side, "id": fill["id"],
                                     "status": fill["status"]})
        return
    entry = fill["average"] or price
    stop = entry - direction * dist
    tp = entry + direction * spec.tp_r * dist if spec.tp_r else None
    slot["position"] = {
        "dir": direction, "side": side, "entry": entry, "size": fill["size"],
        "contracts": fill["filled"], "stop": stop, "tp": tp, "leverage": p.leverage,
        "margin": fill["size"] * entry / p.leverage, "entry_fee": fill["fee_quote"],
        "opened": bar_time, "opened_ms": opened_ms,
    }
    store.save(risk)
    try:
        ex.place_protection(direction, stop, tp)
    except Exception as e:  # never hold a position without its stop
        log.error("stop_failed_closing", {"symbol": cfg.symbol, "side": side, "error": repr(e)})
        close_position(ex, risk, store, slot, log, "stop placement failed")
        return

    live = ex.position() or {}
    if live.get("liq") and direction * (stop - live["liq"]) <= 0:
        log.error("liq_inside_stop_closing", {"symbol": cfg.symbol, "stop": stop,
                                              "liq_price": live["liq"]})
        close_position(ex, risk, store, slot, log, "liquidation price inside stop")
        return
    log.info("entry_filled", {"symbol": cfg.symbol, "side": side, "bar": bar_time,
                              "size": fill["size"], "contracts": fill["filled"], "price": entry,
                              "signal_close": price, "stop": round(stop, 2),
                              "tp": round(tp, 2) if tp else None, "leverage": p.leverage,
                              "margin": round(live.get("margin") or slot["position"]["margin"], 2),
                              "liq_price": live.get("liq") or round(p.liq_price, 2),
                              "risk_usd": round(fill["size"] * dist, 2),
                              "maker_share": round(fill["maker_share"], 3), "id": fill["id"]})


def step(cfg: Config, spec: StrategySpec, ex, risk: RiskManager, store: Store, log) -> None:
    """One poll for one strategy (its symbol's slot)."""
    risk.roll_day(datetime.now(timezone.utc).date())
    slot = store.slot(cfg.symbol)
    pos = slot["position"]
    live = ex.position()

    # 1. sync with the exchange
    if pos is not None and live is None:
        record_close(ex, risk, store, slot, log, "exchange stop/tp")
        pos = None
    elif pos is None and live is not None:
        if not slot.get("foreign_warned"):
            log.warning("foreign_position", {"symbol": cfg.symbol,
                                             "side": "long" if live["dir"] > 0 else "short",
                                             "size": live["size"],
                                             "note": "not opened by the bot; not trading it"})
            slot["foreign_warned"] = True
        return
    slot.pop("foreign_warned", None)

    # 2. the stop must be resting on OKX
    if pos is not None and not ex.pending_protection():
        log.warning("stop_missing_replacing", {"symbol": cfg.symbol, "stop": pos["stop"]})
        try:
            ex.place_protection(pos["dir"], pos["stop"], pos.get("tp"))
        except Exception as e:
            log.error("stop_failed_closing", {"symbol": cfg.symbol, "error": repr(e)})
            close_position(ex, risk, store, slot, log, "stop placement failed")
            return

    # 3. signals on the last closed bar
    sig = signals_ls(ex.fetch_closed_ohlcv(warmup_bars(spec)), spec)
    if len(sig) < 2:
        return
    bar = sig.iloc[-1]
    key = f"{cfg.symbol}:{bar['time'].isoformat()}"
    if risk.is_duplicate(key):
        return

    long_in, short_in = bool(bar["entry"]), bool(bar["short_entry"])
    if pos is not None:
        d = pos["dir"]
        if (d > 0 and (bar["exit"] or short_in)) or (d < 0 and (bar["short_exit"] or long_in)):
            risk.remember(key)
            close_position(ex, risk, store, slot, log, "signal")
            if not (long_in or short_in):
                return
        else:
            return
    if long_in or short_in:
        risk.remember(key)
        store.save(risk)
        open_position(cfg, spec, ex, risk, store, slot, log, 1 if long_in else -1, bar)


def main() -> None:
    import ccxt

    from bot.futures_exchange import OkxFutures

    base = Config()
    if not base.demo and os.getenv("I_UNDERSTAND_THIS_IS_REAL_MONEY") != "yes":
        raise SystemExit("DEMO=false would trade real money. Futures run on demo only.")
    fcfg = futures_cfg(base)
    lock = acquire_lock(fcfg.state_file)  # noqa: F841 -- held until the process exits
    strategies = load_futures_strategies(fcfg)
    log = get_logger(fcfg.log_dir, "futures")
    slots = []
    for cfg, spec in strategies:
        ex = OkxFutures(cfg)
        ok, msg = ex.account_mode_ok()
        if not ok:
            raise SystemExit(msg)
        slots.append((cfg, spec, ex))
    risk = RiskManager(fcfg)
    store = Store(fcfg.state_file)
    risk.load_dict(store.data.get("risk", {}))

    log.info("started", {"demo": fcfg.demo, "risk_per_trade": fcfg.fut_risk_fraction,
                         "max_leverage": fcfg.fut_max_leverage,
                         "max_margin": fcfg.fut_max_margin_fraction,
                         "strategies": [f"{c.symbol} {c.timeframe} {s.label()}" for c, s, _ in slots],
                         "positions": {k: v.get("position") for k, v in store.data["slots"].items()}})
    try:
        while True:
            for cfg, spec, ex in slots:
                try:
                    step(cfg, spec, ex, risk, store, log)
                except ccxt.NetworkError as e:  # internet/OKX blip: one line, retry next poll
                    log.warning("network_error", {"symbol": cfg.symbol, "error": str(e)[:200]})
                except Exception:
                    log.exception("error", {"symbol": cfg.symbol})
            time.sleep(fcfg.poll_seconds)
    except KeyboardInterrupt:
        log.info("stopped", {"positions": {k: v.get("position")
                                           for k, v in store.data["slots"].items()}})


if __name__ == "__main__":
    main()
