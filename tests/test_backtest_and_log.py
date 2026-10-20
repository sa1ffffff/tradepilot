import json
import logging

import numpy as np
import pandas as pd

from config import Config
from bot.data import fetch_closed
from bot.engine import metrics, run
from bot.log import JsonFormatter
from bot.strategies import StrategySpec, default_spec


def _record(msg, args):
    return logging.LogRecord("bot", logging.INFO, __file__, 1, msg, args, None)


def test_log_empty_dict_does_not_error():
    out = json.loads(JsonFormatter().format(_record("stopped", ({},))))
    assert out["msg"] == "stopped"


def test_log_fields_are_merged_and_percent_is_safe():
    out = json.loads(JsonFormatter().format(_record("100% done", ({"a": 1},))))
    assert out["msg"] == "100% done" and out["a"] == 1


def _frame(closes, lows=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    lows = closes * 0.999 if lows is None else np.array(lows, dtype=float)
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC"),
        "open": closes, "high": closes * 1.001, "low": lows,
        "close": closes, "volume": np.ones(n),
    })


CFG = Config(execution="taker", taker_fee=0.001, slippage_bps=0.0, backtest_start_equity=1000.0,
             risk_fraction=0.01, max_cost_per_r=0)


def test_round_trip_at_same_price_loses_exactly_the_fees():
    closes = [100.0] * 80 + [101.0] + [101.0] * 3 + [90.0] * 3
    wide = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=50.0)
    trades, _, equity = run(_frame(closes), wide, CFG)
    t = trades[0]
    expected = -(t.size * t.entry * 0.001 + t.size * t.exit * 0.001) + t.size * (t.exit - t.entry)
    assert abs(t.pnl - expected) < 1e-9
    assert abs(equity - (1000 + sum(x.pnl for x in trades))) < 1e-9


def test_stop_fills_at_stop_or_gap_open():
    closes = [100.0] * 80 + [105.0] + [60.0]
    trades, _, _ = run(_frame(closes), default_spec(), CFG)
    assert trades[0].reason == "stop"
    assert trades[0].exit == 60.0  # bar opened below the stop -> filled at the open


def test_take_profit():
    closes = [100.0] * 80 + [101.0] + [101.2] * 3 + [130.0]
    spec = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=1.0, tp_r=1.0)
    trades, _, _ = run(_frame(closes), spec, CFG)
    assert trades[0].reason == "tp"


def test_never_spends_more_than_equity():
    closes = [100.0] * 80 + [100.5] + [100.6] * 3
    cfg = Config(taker_fee=0.001, backtest_start_equity=1000.0, risk_fraction=0.5, max_cost_per_r=0)
    spec = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=0.1)
    trades, curve, _ = run(_frame(closes), spec, cfg)
    assert trades[0].size * trades[0].entry * 1.001 <= 1000 + 1e-6
    assert min(curve) > 0


def test_metrics_basic():
    trades, curve, eq = run(_frame([100.0] * 80 + [101.0] + [90.0] * 3), default_spec(), CFG)
    m = metrics(trades, curve, 1000, eq, 100, 90)
    assert m["trades"] == 1 and m["buy_hold_pct"] == -10.0


def test_fetch_closed_pages_past_okx_300_bar_cap():
    tf = 3_600_000
    now = 1_000 * 2_000 * tf  # fixed clock, aligned to the hour

    class FakeOkx:
        def parse_timeframe(self, _):
            return tf // 1000

        def milliseconds(self):
            return now + tf // 2  # half-way through the forming candle

        def fetch_ohlcv(self, symbol, timeframe, since, limit):
            start = since - since % tf + (tf if since % tf else 0)
            return [[t, 1, 1, 1, 1, 1] for t in range(start, min(start + limit * tf, now + 1), tf)]

    df = fetch_closed(FakeOkx(), "BTC/USDT", "1h", bars=1000)
    assert len(df) == 1000
    assert df["time"].is_monotonic_increasing
    assert int(df["time"].iloc[-1].value // 1_000_000) == now - tf  # forming candle dropped
