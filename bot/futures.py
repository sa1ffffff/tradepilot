"""Futures (perpetual swap) sizing, shared by the long/short engine and the live
futures runner so research and trading size positions identically.

Size comes from risk, leverage from volatility:
- size: lose fut_risk_fraction of equity if the stop is hit;
- leverage: the highest whole number (up to fut_max_leverage) that keeps the
  liquidation price at least fut_liq_buffer times further away than the stop,
  so the stop always triggers first -- wide stops get low leverage;
- margin: never more than fut_max_margin_fraction of equity; if the
  risk-based size would need more, the position is made smaller.
Margin is isolated: a position can lose its own margin, never the account.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass


def futures_cfg(cfg):
    """The config the shared cost model and risk gate should see for futures."""
    return dataclasses.replace(
        cfg, maker_fee=cfg.fut_maker_fee, taker_fee=cfg.fut_taker_fee,
        risk_fraction=cfg.fut_risk_fraction, max_daily_loss_usd=cfg.fut_max_daily_loss_usd,
        state_file=cfg.fut_state_file, strategy_file=cfg.fut_strategy_file,
        symbol=cfg.fut_symbol, max_notional_usd=float("inf"))


@dataclass(frozen=True)
class FuturesPlan:
    direction: int        # +1 long, -1 short
    size: float           # base currency (BTC)
    leverage: int
    margin: float         # quote (USDT) locked in the isolated position
    notional: float
    stop_price: float
    liq_price: float      # estimate; OKX's own figure is shown once the position opens


def leverage_for(stop_pct: float, cfg) -> int:
    """Volatility-based leverage: liquidation distance (~1/lev) must be at least
    fut_liq_buffer x the stop distance."""
    raw = 1 / (stop_pct * cfg.fut_liq_buffer + cfg.fut_maint_margin)
    return int(max(1, min(cfg.fut_max_leverage, math.floor(raw))))


def liq_price(price: float, direction: int, leverage: int, cfg) -> float:
    return price * (1 - direction * (1 / leverage - cfg.fut_maint_margin))


def plan(equity: float, price: float, stop_distance: float, direction: int, cfg,
         margin_in_use: float = 0.0) -> FuturesPlan | None:
    if equity <= 0 or price <= 0 or not stop_distance > 0 or stop_distance >= price:
        return None
    lev = leverage_for(stop_distance / price, cfg)
    size = equity * cfg.fut_risk_fraction / stop_distance
    margin_room = equity * cfg.fut_max_margin_fraction - margin_in_use
    if margin_room <= 0:
        return None
    size = min(size, margin_room * lev / price)
    notional = size * price
    return FuturesPlan(direction, size, lev, notional / lev, notional,
                       price - direction * stop_distance, liq_price(price, direction, lev, cfg))


def trail_stop(direction: int, entry: float, init_dist: float, stop: float, extreme: float,
               atr: float, start_r: float, trail_atr: float) -> float:
    """The trailing stop, shared by the engine and the live runner.

    Once the best price since entry (`extreme`: highest high for a long, lowest
    low for a short) is start_r x the initial risk in profit, the stop sits
    trail_atr x ATR behind that best price. It only ever tightens. With
    start_r = 1 and trail_atr equal to the strategy's stop_atr it lands near
    breakeven when it first activates. start_r <= 0 disables it.
    """
    if start_r <= 0 or not init_dist > 0 or not atr > 0:
        return stop
    if direction * (extreme - entry) < start_r * init_dist:
        return stop
    candidate = extreme - direction * trail_atr * atr
    return max(stop, candidate) if direction > 0 else min(stop, candidate)


def trail_params(spec, cfg) -> tuple[float, float]:
    """(start_r, trail_atr) for a strategy: the trail distance is fut_trail_mult x
    the strategy's own stop distance, in ATRs."""
    start_r = getattr(cfg, "fut_trail_start_r", 0.0)
    return float(start_r), float(getattr(cfg, "fut_trail_mult", 1.0)) * spec.stop_atr
