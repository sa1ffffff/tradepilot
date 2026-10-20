"""Configuration loaded from environment / .env.

Nothing secret is hard-coded here; keys come from the environment so the
same code runs in demo and (later) live without edits.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _f(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _b(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes")


@dataclass(frozen=True)
class Config:
    api_key: str = os.getenv("OKX_API_KEY", "")
    api_secret: str = os.getenv("OKX_API_SECRET", "")
    api_passphrase: str = os.getenv("OKX_API_PASSPHRASE", "")
    demo: bool = _b("DEMO", True)
    # www.okx.com is unreachable from some networks; app.okx.com / my.okx.com (EEA) are alternatives
    okx_hostname: str = os.getenv("OKX_HOSTNAME", "www.okx.com")

    symbol: str = os.getenv("SYMBOL", "BTC/USDT")
    timeframe: str = os.getenv("TIMEFRAME", "15m")
    poll_seconds: int = int(_f("POLL_SECONDS", 60))

    # which strategy to trade comes from strategy.json (written by research.py)
    strategy_file: str = "strategy.json"

    risk_fraction: float = _f("RISK_FRACTION", 0.01)
    max_notional_usd: float = _f("MAX_NOTIONAL_USD", 50.0)
    max_daily_loss_usd: float = _f("MAX_DAILY_LOSS_USD", 20.0)
    min_base_size: float = 1e-5

    fee_rate: float = _f("FEE_RATE", 0.001)
    slippage_bps: float = _f("SLIPPAGE_BPS", 2.0)
    backtest_start_equity: float = _f("BACKTEST_START_EQUITY", 1000.0)

    kill_file: str = "KILL"
    state_file: str = "state.json"
    log_dir: str = "logs"

    def require_keys(self) -> None:
        missing = [n for n, v in (
            ("OKX_API_KEY", self.api_key),
            ("OKX_API_SECRET", self.api_secret),
            ("OKX_API_PASSPHRASE", self.api_passphrase),
        ) if not v]
        if missing:
            raise SystemExit(
                "Missing credentials: " + ", ".join(missing) +
                "\nCopy .env.example to .env and fill in your OKX demo keys."
            )
