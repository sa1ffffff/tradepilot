"""The risk layer. Deterministic, no network, no cleverness.

This is the part that decides whether a trade is allowed and how big it is.
It is intentionally boring and easy to audit, because it is the thing standing
between a bad signal and your balance.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    size: float = 0.0
    stop_distance: float = 0.0   # price distance from entry to the protective stop


class RiskManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self._seen: set[str] = set()
        self._day: date | None = None
        self.realized_pnl_today: float = 0.0

    # --- idempotency: never act on the same bar's signal twice ---------------
    def is_duplicate(self, key: str) -> bool:
        return key in self._seen

    def remember(self, key: str) -> None:
        self._seen.add(key)

    # --- daily loss tracking -------------------------------------------------
    def roll_day(self, day: date) -> None:
        if day != self._day:
            self._day = day
            self.realized_pnl_today = 0.0

    def record_pnl(self, pnl: float) -> None:
        self.realized_pnl_today += pnl

    def daily_loss_hit(self) -> bool:
        return self.realized_pnl_today <= -abs(self.cfg.max_daily_loss_usd)

    # --- persistence, so a restart can't reset the daily loss counter --------
    def to_dict(self) -> dict:
        return {
            "day": self._day.isoformat() if self._day else None,
            "realized_pnl_today": self.realized_pnl_today,
            "seen": sorted(self._seen)[-50:],
        }

    def load_dict(self, data: dict) -> None:
        self._day = date.fromisoformat(data["day"]) if data.get("day") else None
        self.realized_pnl_today = float(data.get("realized_pnl_today", 0.0))
        self._seen = set(data.get("seen", []))

    # --- the gate ------------------------------------------------------------
    def evaluate_entry(self, price: float, stop_distance: float, equity: float,
                       kill: bool) -> Decision:
        if kill:
            return Decision(False, "kill switch engaged")
        if self.daily_loss_hit():
            return Decision(False, f"daily loss limit reached ({self.realized_pnl_today:.2f})")
        if equity <= 0:
            return Decision(False, "no equity")
        if price <= 0:
            return Decision(False, "invalid price")
        if not stop_distance > 0 or stop_distance >= price:
            return Decision(False, "invalid stop distance")

        size = position_size(equity, price, stop_distance, self.cfg.risk_fraction,
                             self.cfg.max_notional_usd, self.cfg.fee_rate)
        if size < self.cfg.min_base_size:
            return Decision(False, "position below minimum size")

        return Decision(True, "ok", size=math.floor(size * 1e8) / 1e8, stop_distance=stop_distance)


def position_size(equity: float, price: float, stop_distance: float, risk_fraction: float,
                  max_notional: float, fee_rate: float = 0.0) -> float:
    """Risk `risk_fraction` of equity if the stop is hit -- but in spot you
    can't spend more than you have, and never more than the hard cap."""
    size = equity * risk_fraction / stop_distance
    return min(size, equity / (price * (1 + fee_rate)), max_notional / price)
