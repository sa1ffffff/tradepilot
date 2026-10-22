import pandas as pd

from bot.engine import Trade
from futures_session_report import active_spans, live_trades, match

TS = lambda s: pd.Timestamp(s, tz="UTC")
STRAT = "BTC/USDT:USDT 5m ema_cross(fast=15,slow=40) stop=2.0ATR no tp +shorts"


def ev(ts, msg, **kw):
    return {"ts": f"2026-10-21T{ts}:00+00:00", "msg": msg, **kw}


EVENTS = [
    ev("07:00", "started", strategies=["ETH/USDT:USDT 1h x"]),             # BTC not running yet
    ev("09:00", "started", strategies=["ETH/USDT:USDT 1h x", STRAT]),
    ev("10:00", "entry_filled", symbol="BTC/USDT:USDT", bar="2026-10-21T09:55:00+00:00",
       side="short", price=100.0, signal_close=100.0),
    ev("10:30", "exit_filled", symbol="BTC/USDT:USDT", side="short", price=99.0, pnl=5.0, reason="signal"),
    ev("11:00", "network_error", symbol="BTC/USDT:USDT"),                    # process killed after this
    ev("12:00", "started", strategies=[STRAT]),
    ev("13:00", "stopped"),
]


def trade(bar, side):
    t = TS(f"2026-10-21T{bar}")
    return Trade(t, t, 100.0, 99.0, 1.0, 1.0, 0.1, 0.1, "signal", side)


def test_spans_follow_the_exact_strategy_and_kills():
    spans = active_spans(EVENTS, STRAT, TS("2026-10-21T14:00"))
    assert spans == [(TS("2026-10-21T09:00"), TS("2026-10-21T11:00")),   # killed: last line 11:00
                     (TS("2026-10-21T12:00"), TS("2026-10-21T13:00"))]
    assert active_spans(EVENTS, "SOL/USDT:USDT 4h other", TS("2026-10-21T14:00")) == []


def test_match_pairs_and_explains():
    live = live_trades(EVENTS, "BTC/USDT:USDT", TS("2026-10-21T00:00"))
    assert live[0]["reason"] == "signal" and live[0]["pnl"] == 5.0
    spans = active_spans(EVENTS, STRAT, TS("2026-10-21T14:00"))
    bt = [trade("09:55", "short"),      # matches the live trade
          trade("08:00", "long"),       # strategy not running yet -> explained
          trade("11:30", "long"),       # between kill and restart -> explained
          trade("12:30", "short"),      # running, not traded, not skipped -> only backtest
          trade("12:40", "long")]       # running, but the bot logged a skip -> explained
    m = match(live, bt, pd.Timedelta(minutes=5), spans, {"2026-10-21T12:40:00+00:00": "no margin room"})
    assert (m["matched"], m["explained"], m["only_bt"], m["only_live"]) == (1, 3, 1, 0)
    reasons = {r["bar"][11:16]: r["why"] for r in m["rows"]}
    assert reasons["12:40"].startswith("bot skipped it") and "wasn't running" in reasons["08:00"]
