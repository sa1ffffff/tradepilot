"""Thin ccxt wrapper for OKX, defaulting to demo (simulated) trading.

Everything here talks to the network, so none of it runs in the backtest.
Orders are sized in base currency (BTC). With EXECUTION=maker, buys and
non-urgent sells are first tried as post-only limit orders at the best
bid/ask (maker fee), re-priced a few times, and whatever is left goes as a
market order. Stop-loss exits are always market orders.
"""
from __future__ import annotations

import time

import pandas as pd

from bot.data import fetch_closed


class OkxExchange:
    def __init__(self, cfg):
        import ccxt  # imported here so the backtest never needs ccxt installed

        cfg.require_keys()
        self.cfg = cfg
        self.client = ccxt.okx({
            "apiKey": cfg.api_key,
            "secret": cfg.api_secret,
            "password": cfg.api_passphrase,
            "enableRateLimit": True,
            "hostname": cfg.okx_hostname,
            "options": {"defaultType": "spot"},
        })
        if cfg.demo:
            self.client.set_sandbox_mode(True)
        self.client.load_markets()
        self.market = self.client.market(cfg.symbol)
        if not self.market.get("spot"):
            raise SystemExit(f"{cfg.symbol} is not a spot market; this bot is spot long/flat only.")
        self.base = self.market["base"]
        self.quote = self.market["quote"]

    def min_amount(self) -> float:
        return float(self.market["limits"]["amount"]["min"] or self.cfg.min_base_size)

    def fetch_closed_ohlcv(self, bars: int) -> pd.DataFrame:
        """The last `bars` candles whose period has fully ended (the forming
        candle is dropped by timestamp)."""
        return fetch_closed(self.client, self.cfg.symbol, self.cfg.timeframe, bars)

    def last_price(self) -> float:
        return float(self.client.fetch_ticker(self.cfg.symbol)["last"])

    def _free(self, ccy: str) -> float:
        bal = self.client.fetch_balance()
        return float(bal.get(ccy, {}).get("free", 0.0) or 0.0)

    def equity_quote(self) -> float:
        return self._free(self.quote)

    def base_balance(self) -> float:
        return self._free(self.base)

    # --- execution -----------------------------------------------------------
    def _wait(self, oid: str, seconds: float) -> dict:
        """Poll an order until it is closed/canceled or `seconds` pass."""
        deadline = time.monotonic() + seconds
        while True:
            o = self.client.fetch_order(oid, self.cfg.symbol)
            if o.get("status") in ("closed", "canceled", "expired", "rejected"):
                return o
            if time.monotonic() >= deadline:
                return o
            time.sleep(1.0)

    def _parse_fill(self, o: dict) -> dict:
        filled = float(o.get("filled") or 0.0)
        avg = float(o.get("average") or o.get("price") or 0.0)
        fee_base = fee_quote = 0.0
        for fee in o.get("fees") or ([o["fee"]] if o.get("fee") else []):
            cost = float(fee.get("cost") or 0.0)  # negative for a maker rebate
            if fee.get("currency") == self.base:
                fee_base += cost
            else:
                fee_quote += cost
        return {"id": o["id"], "filled": filled, "average": avg, "fee_base": fee_base,
                "fee_quote": fee_quote, "status": o.get("status")}

    def _maker_attempt(self, side: str, amount: float, params: dict | None = None) -> dict | None:
        """One post-only limit at the best bid (buy) / ask (sell); cancelled if
        still open after maker_wait_seconds. Returns what filled, or None."""
        import ccxt

        book = self.client.fetch_order_book(self.cfg.symbol, 5)
        levels = book["bids"] if side == "buy" else book["asks"]
        if not levels:
            return None
        try:
            o = self.client.create_order(self.cfg.symbol, "limit", side, amount, levels[0][0],
                                         params={"postOnly": True, **(params or {})})
        except ccxt.InvalidOrder:
            return None  # would have crossed the spread; re-price on the next attempt
        o = self._wait(o["id"], self.cfg.maker_wait_seconds)
        if o.get("status") == "open":
            try:
                self.client.cancel_order(o["id"], self.cfg.symbol)
            except ccxt.OrderNotFound:
                pass  # filled or cancelled in the meantime
            o = self._wait(o["id"], 5)  # final state, including any fill that raced the cancel
        return self._parse_fill(o)

    def _execute(self, side: str, amount: float, urgent: bool, params: dict | None = None) -> dict:
        parts: list[tuple[dict, bool]] = []  # (fill, was_maker)
        remaining = amount
        min_amt = self.min_amount()
        if self.cfg.execution == "maker" and not urgent:
            for _ in range(self.cfg.maker_attempts):
                f = self._maker_attempt(side, remaining, params)
                if f and f["filled"] > 0:
                    parts.append((f, True))
                    remaining -= f["filled"]
                if remaining < min_amt:
                    break
        if remaining >= min_amt:
            mparams = dict(params or {})
            if side == "buy" and self.market.get("spot"):
                mparams["tgtCcy"] = "base_ccy"
            o = self.client.create_order(self.cfg.symbol, "market", side, remaining, params=mparams)
            parts.append((self._parse_fill(self._wait(o["id"], 10)), False))

        filled = sum(f["filled"] for f, _ in parts)
        maker = sum(f["filled"] for f, m in parts if m)
        avg = sum(f["filled"] * f["average"] for f, _ in parts) / filled if filled else 0.0
        fee_base = sum(f["fee_base"] for f, _ in parts)
        fee_quote = sum(f["fee_quote"] for f, _ in parts)
        return {
            "id": ",".join(f["id"] for f, _ in parts),
            "status": parts[-1][0]["status"] if parts else "unfilled",
            "filled": filled,
            "average": avg,
            "fee_base": fee_base,
            "fee_quote": fee_quote + fee_base * avg,  # total fee in quote terms
            "maker_share": maker / filled if filled else 0.0,
        }

    def buy(self, amount: float) -> dict:
        return self._execute("buy", amount, urgent=False)

    def sell(self, amount: float, urgent: bool = False) -> dict:
        """urgent=True (stop-loss) goes straight to a market order."""
        return self._execute("sell", amount, urgent)

    def trading_fee(self) -> dict:
        """This account's actual maker/taker rates for the symbol (positive = you pay)."""
        f = self.client.fetch_trading_fee(self.cfg.symbol)
        return {"maker": float(f["maker"]), "taker": float(f["taker"])}
