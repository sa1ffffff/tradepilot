"""Configuration loaded from environment / .env.

Nothing secret is hard-coded here; keys come from the environment so the
same code runs in demo and (later) live without edits.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

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
    # repr=False: credentials never show up in printed configs, tracebacks or test output
    api_key: str = field(default=os.getenv("OKX_API_KEY", ""), repr=False)
    api_secret: str = field(default=os.getenv("OKX_API_SECRET", ""), repr=False)
    api_passphrase: str = field(default=os.getenv("OKX_API_PASSPHRASE", ""), repr=False)
    demo: bool = _b("DEMO", True)
    # www.okx.com is unreachable from some networks; app.okx.com / my.okx.com (EEA) are alternatives
    okx_hostname: str = os.getenv("OKX_HOSTNAME", "www.okx.com")

    symbol: str = os.getenv("SYMBOL", "BTC/USDT")
    timeframe: str = os.getenv("TIMEFRAME", "15m")
    poll_seconds: int = int(_f("POLL_SECONDS", 60))

    # which strategy to trade comes from strategy.json (written by research.py)
    strategy_file: str = os.getenv("STRATEGY_FILE", "strategy.json")

    risk_fraction: float = _f("RISK_FRACTION", 0.01)
    max_notional_usd: float = _f("MAX_NOTIONAL_USD", 50.0)
    max_daily_loss_usd: float = _f("MAX_DAILY_LOSS_USD", 20.0)
    min_base_size: float = 1e-5

    # Execution and costs. Defaults are OKX's regular (Lv1) spot tier; check_connection.py
    # prints your account's actual rates.
    execution: str = os.getenv("EXECUTION", "maker")        # maker: post-only limit, then market
    maker_fee: float = _f("MAKER_FEE", 0.0008)
    taker_fee: float = _f("TAKER_FEE", 0.0010)
    slippage_bps: float = _f("SLIPPAGE_BPS", 2.0)          # market orders only
    maker_wait_seconds: int = int(_f("MAKER_WAIT_SECONDS", 20))
    maker_attempts: int = int(_f("MAKER_ATTEMPTS", 3))
    maker_fill_rate: float = _f("MAKER_FILL_RATE", 0.7)    # research assumption; measure it live
    max_cost_per_r: float = _f("MAX_COST_PER_R", 0.2)      # skip trades whose costs eat >20% of the risk
    backtest_start_equity: float = _f("BACKTEST_START_EQUITY", 1000.0)

    # Futures (USDT-margined perpetual swaps), run by bot.futures_runner. Defaults are sized
    # for the demo account: 2% risk per trade, isolated margin, leverage set from volatility.
    fut_symbol: str = os.getenv("FUT_SYMBOL", "BTC/USDT:USDT")
    fut_strategy_file: str = os.getenv("FUT_STRATEGY_FILE", "strategies/futures.json")
    fut_risk_fraction: float = _f("FUT_RISK_FRACTION", 0.02)
    fut_max_margin_fraction: float = _f("FUT_MAX_MARGIN_FRACTION", 0.5)  # of equity, all positions
    fut_max_leverage: int = int(_f("FUT_MAX_LEVERAGE", 5))
    fut_liq_buffer: float = _f("FUT_LIQ_BUFFER", 3.0)      # liquidation >= 3x further than the stop
    fut_maint_margin: float = _f("FUT_MAINT_MARGIN", 0.004)
    fut_maker_fee: float = _f("FUT_MAKER_FEE", 0.0002)
    fut_taker_fee: float = _f("FUT_TAKER_FEE", 0.0005)
    fut_funding_8h: float = _f("FUT_FUNDING_8H", 0.0001)   # research charges it to both sides
    fut_max_daily_loss_usd: float = _f("FUT_MAX_DAILY_LOSS_USD", 250.0)
    fut_state_file: str = "state_futures.json"
    # Trailing stop: once a trade is FUT_TRAIL_START_R x its initial risk in profit, the stop
    # follows the best price at FUT_TRAIL_MULT x the strategy's stop distance (stop_atr x ATR).
    # The defaults (2R, 2x) leave the researched results almost unchanged while capping big
    # give-backs. FUT_TRAIL_START_R=0 turns it off. Strategy files can override both
    # ("trail_start_r", "trail_mult").
    fut_trail_start_r: float = _f("FUT_TRAIL_START_R", 2.0)
    fut_trail_mult: float = _f("FUT_TRAIL_MULT", 2.0)

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
