"""Thin ccxt wrapper for OKX, defaulting to demo (simulated) trading.

Everything here talks to the network, so none of it runs in the backtest.
Spot market buys are sent with tgtCcy=base_ccy so the amount is in base
currency (BTC), matching how the risk layer sizes positions.
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

    def _fill(self, order: dict) -> dict:
        """Look the order up until it reports a fill; market orders on OKX
        return only an id from the create call."""
        oid = order["id"]
        for _ in range(10):
            o = self.client.fetch_order(oid, self.cfg.symbol)
            if o.get("status") in ("closed", "canceled") and o.get("filled"):
                break
            time.sleep(0.5)
        filled = float(o.get("filled") or 0.0)
        avg = float(o.get("average") or o.get("price") or 0.0)
        fee_base = fee_quote = 0.0
        for fee in o.get("fees") or ([o["fee"]] if o.get("fee") else []):
            cost = abs(float(fee.get("cost") or 0.0))
            if fee.get("currency") == self.base:
                fee_base += cost
            else:
                fee_quote += cost
        return {
            "id": oid,
            "status": o.get("status"),
            "filled": filled,
            "average": avg,
            "fee_base": fee_base,
            "fee_quote": fee_quote + fee_base * avg,  # total fee in quote terms
        }

    def market_buy(self, amount: float) -> dict:
        order = self.client.create_order(
            self.cfg.symbol, "market", "buy", amount, params={"tgtCcy": "base_ccy"}
        )
        return self._fill(order)

    def market_sell(self, amount: float) -> dict:
        order = self.client.create_order(self.cfg.symbol, "market", "sell", amount)
        return self._fill(order)
