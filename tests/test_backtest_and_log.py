import json
import logging

import numpy as np
import pandas as pd

from config import Config
from backtest import run
from bot.log import JsonFormatter


def _record(msg, args):
    return logging.LogRecord("bot", logging.INFO, __file__, 1, msg, args, None)


def test_log_empty_dict_does_not_error():
    out = json.loads(JsonFormatter().format(_record("stopped", ({},))))
    assert out["msg"] == "stopped"


def test_log_fields_are_merged_and_percent_is_safe():
    out = json.loads(JsonFormatter().format(_record("100% done", ({"a": 1},))))
    assert out["msg"] == "100% done" and out["a"] == 1


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="15min", tz="UTC"),
        "open": closes, "high": closes * 1.001, "low": closes * 0.999,
        "close": closes, "volume": np.ones(n),
    })


def test_fees_are_in_trade_pnl_and_equity_matches():
    # up-cross then down-cross at an unchanged price: the trade loses exactly the fees
    closes = [100.0] * 60 + [101.0] + [100.0] * 30
    cfg = Config(fee_rate=0.001, backtest_start_equity=1000.0, atr_stop_mult=50.0)
    m = run(_frame(closes), cfg)
    assert m["trades"] >= 1
    assert m["final_equity"] < 1000.0
    assert m["total_return_pct"] < 0


def test_stop_is_honoured():
    closes = [100.0] * 60 + [105.0] + [60.0] * 5
    cfg = Config(fee_rate=0.0, backtest_start_equity=1000.0, atr_stop_mult=2.0)
    m = run(_frame(closes), cfg)
    assert m["stopped_out"] == 1


def test_never_spends_more_than_equity():
    closes = [100.0] * 60 + [100.5] + [100.6] * 3
    cfg = Config(fee_rate=0.001, backtest_start_equity=1000.0, risk_fraction=0.5,
                 atr_stop_mult=0.1)
    m = run(_frame(closes), cfg)
    assert m["max_drawdown_pct"] > -100


def test_live_loader_pages_past_okx_300_bar_cap(monkeypatch):
    import ccxt
    import backtest

    tf = 3_600_000
    now = 1_000 * 2_000 * tf  # fixed clock, aligned to the hour

    class FakeOkx:
        def __init__(self, *_):
            pass

        def parse_timeframe(self, _):
            return tf // 1000

        def milliseconds(self):
            return now + tf // 2  # half-way through the forming candle

        def fetch_ohlcv(self, symbol, timeframe, since, limit):
            start = since - since % tf
            return [[t, 1, 1, 1, 1, 1] for t in range(start, min(start + limit * tf, now + 1), tf)]

    monkeypatch.setattr(ccxt, "okx", FakeOkx)
    df = backtest.load_live(Config(timeframe="1h"), 1000)
    assert len(df) == 1000
    assert df["time"].is_monotonic_increasing
    assert int(df["time"].iloc[-1].value // 1_000_000) + tf <= now + tf // 2
