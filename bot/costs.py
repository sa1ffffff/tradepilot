"""Trading-cost model shared by the engine (backtest/research) and the live bot.

Rates are fractions of notional per fill, slippage included."""
from __future__ import annotations


def taker_cost(cfg) -> float:
    """A market order: taker fee plus slippage."""
    return cfg.taker_fee + cfg.slippage_bps / 10_000


def passive_cost(cfg) -> float:
    """Expected cost of a fill attempted as maker: the post-only limit fills
    maker_fill_rate of the time, otherwise the fallback market order pays taker."""
    if cfg.execution != "maker":
        return taker_cost(cfg)
    r = cfg.maker_fill_rate
    return r * cfg.maker_fee + (1 - r) * taker_cost(cfg)


def round_trip(cfg) -> float:
    """Entry plus a normal (non-stop) exit."""
    return 2 * passive_cost(cfg)


def too_costly(cfg, price: float, stop_distance: float) -> bool:
    """True when round-trip costs would exceed max_cost_per_r of the amount risked.
    With a tight stop the fees alone can be a large share of every loss."""
    return bool(cfg.max_cost_per_r) and round_trip(cfg) * price > cfg.max_cost_per_r * stop_distance
