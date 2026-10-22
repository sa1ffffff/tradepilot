"""OKX USDT-margined perpetual swaps, isolated margin, net position mode.

Orders reuse OkxExchange's maker-first execution (post-only limit, re-priced,
then market). Amounts on swaps are in contracts (BTC-USDT-SWAP: 0.01 BTC each);
this class converts to and from base currency so the rest of the bot can think
in BTC.

The stop-loss (and take-profit, if any) lives on OKX as an algo order with
closeFraction=1: it closes the whole position at market when triggered, even if
the bot or the PC is down.
"""
from __future__ import annotations

import math
import time

from bot.exchange import OkxExchange


class OkxFutures(OkxExchange):
    def __init__(self, cfg):
        import ccxt

        cfg.require_keys()
        self.cfg = cfg
        self.client = ccxt.okx({
            "apiKey": cfg.api_key,
            "secret": cfg.api_secret,
            "password": cfg.api_passphrase,
            "enableRateLimit": True,
            "hostname": cfg.okx_hostname,
            "options": {"defaultType": "swap"},
        })
        if cfg.demo:
            self.client.set_sandbox_mode(True)
        self.client.load_markets()
        self.market = self.client.market(cfg.symbol)
        if not self.market.get("swap") or not self.market.get("linear"):
            raise SystemExit(f"{cfg.symbol} is not a USDT-margined perpetual swap.")
        self.inst_id = self.market["id"]
        self.base, self.quote = self.market["base"], self.market["quote"]
        self.contract_size = float(self.market["contractSize"])
        self.min_contracts = float(self.market["limits"]["amount"]["min"])
        self.contract_step = float(self.market["precision"]["amount"])
        self.trade_params = {"tdMode": "isolated"}

    # --- account ---------------------------------------------------------------
    def account_mode_ok(self) -> tuple[bool, str]:
        acct = self.client.privateGetAccountConfig()["data"][0]
        if acct.get("acctLv") == "1":
            return False, ("account is in Spot mode; switch to 'Spot and futures' mode in OKX "
                           "(Demo Trading > profile > Settings > Account mode)")
        if acct.get("posMode") != "net_mode":
            return False, "position mode must be one-way (net); set it in OKX settings"
        return True, f"account level {acct.get('acctLv')}, one-way positions"

    def equity_quote(self) -> float:
        bal = self.client.fetch_balance()
        return float(bal.get(self.quote, {}).get("total") or 0.0)

    def min_amount(self) -> float:
        return self.min_contracts  # _execute works in contracts on swaps

    # --- sizing ----------------------------------------------------------------
    def to_contracts(self, base_size: float) -> float:
        steps = math.floor(base_size / self.contract_size / self.contract_step + 1e-9)
        return round(steps * self.contract_step, 8)

    def to_base(self, contracts: float) -> float:
        return contracts * self.contract_size

    def set_leverage(self, leverage: int) -> None:
        self.client.set_leverage(leverage, self.cfg.symbol, {"marginMode": "isolated"})

    # --- position --------------------------------------------------------------
    def position(self) -> dict | None:
        """The open position on this symbol, or None. Size in base currency."""
        for p in self.client.fetch_positions([self.cfg.symbol]):
            contracts = float(p.get("contracts") or 0.0)
            if contracts:
                info = p.get("info", {})
                signed = float(info.get("pos") or contracts)
                return {
                    "dir": 1 if signed > 0 else -1,
                    "contracts": abs(signed),
                    "size": self.to_base(abs(signed)),
                    "entry": float(p.get("entryPrice") or 0.0),
                    "liq": float(p.get("liquidationPrice") or 0.0),
                    "leverage": float(p.get("leverage") or 0.0),
                    "margin_mode": p.get("marginMode"),
                    "margin": float(info.get("margin") or p.get("initialMargin") or 0.0),
                    "upl": float(p.get("unrealizedPnl") or 0.0),
                }
        return None

    def open(self, direction: int, contracts: float) -> dict:
        side = "buy" if direction > 0 else "sell"
        fill = self._execute(side, contracts, urgent=False, params=self.trade_params)
        fill["size"] = self.to_base(fill["filled"])
        return fill

    def close(self, direction: int, contracts: float, urgent: bool = False) -> dict:
        side = "sell" if direction > 0 else "buy"
        fill = self._execute(side, contracts, urgent,
                             params={**self.trade_params, "reduceOnly": True})
        fill["size"] = self.to_base(fill["filled"])
        return fill

    # --- exchange-side stop-loss / take-profit -----------------------------------
    def place_protection(self, direction: int, stop: float, tp: float | None = None) -> str:
        """Algo order that closes the whole position at market when the stop (or
        take-profit) price trades. Returns its algoId."""
        req = {
            "instId": self.inst_id, "tdMode": "isolated",
            "side": "sell" if direction > 0 else "buy",
            "ordType": "oco" if tp else "conditional",
            "closeFraction": "1", "reduceOnly": "true",
            "slTriggerPx": self.client.price_to_precision(self.cfg.symbol, stop),
            "slOrdPx": "-1", "slTriggerPxType": "last",
        }
        if tp:
            req.update({"tpTriggerPx": self.client.price_to_precision(self.cfg.symbol, tp),
                        "tpOrdPx": "-1", "tpTriggerPxType": "last"})
        data = self.client.privatePostTradeOrderAlgo(req)["data"][0]
        if data.get("sCode") not in (None, "0"):
            raise RuntimeError(f"stop-loss rejected: {data.get('sCode')} {data.get('sMsg')}")
        return data["algoId"]

    def move_protection(self, direction: int, stop: float, tp: float | None = None) -> str:
        """Replace the resting stop: place the new one first, then cancel the old
        ones, so the position is never without a stop. (Both are reduce-only
        close-all orders, so even if both fired only one could close anything.)"""
        old = self.pending_protection()
        new_id = self.place_protection(direction, stop, tp)
        stale = [i for i in old if i != new_id]
        if stale:
            self.client.privatePostTradeCancelAlgos([{"algoId": i, "instId": self.inst_id}
                                                     for i in stale])
        return new_id

    def last_price(self) -> float:
        return float(self.client.fetch_ticker(self.cfg.symbol)["last"])

    def pending_protection(self) -> list[str]:
        ids = []
        for ord_type in ("conditional", "oco"):
            rows = self.client.privateGetTradeOrdersAlgoPending(
                {"instType": "SWAP", "instId": self.inst_id, "ordType": ord_type})["data"]
            ids += [r["algoId"] for r in rows]
        return ids

    def cancel_protection(self) -> None:
        ids = self.pending_protection()
        if ids:
            self.client.privatePostTradeCancelAlgos([{"algoId": i, "instId": self.inst_id}
                                                     for i in ids])

    # --- results -----------------------------------------------------------------
    def closed_pnl(self, opened_ms: int, tries: int = 5) -> dict | None:
        """OKX's own record of the position closed after opened_ms: realised P&L
        including fees and funding, close price, and how it closed."""
        for _ in range(tries):
            rows = self.client.privateGetAccountPositionsHistory(
                {"instType": "SWAP", "instId": self.inst_id, "limit": "10"})["data"]
            rows = [r for r in rows if int(r.get("cTime") or 0) >= opened_ms - 60_000
                    and r.get("type") in ("2", "3", "4", "5")]
            if rows:
                r = max(rows, key=lambda x: int(x.get("uTime") or 0))
                kind = {"2": "closed", "3": "liquidated", "4": "partly liquidated",
                        "5": "auto-deleveraged"}[r["type"]]
                return {"pnl": float(r.get("realizedPnl") or 0.0),
                        "close_price": float(r.get("closeAvgPx") or 0.0),
                        "fee": float(r.get("fee") or 0.0),
                        "funding": float(r.get("fundingFee") or 0.0), "kind": kind}
            time.sleep(1.0)
        return None
