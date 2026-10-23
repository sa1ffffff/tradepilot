import dashboard
from bot.lock import acquire, is_held


def test_trades_pair_entries_with_exits():
    events = [
        {"ts": "2026-10-21T10:00:00+00:00", "msg": "started", "symbol": "BTC/USDT", "timeframe": "4h",
         "strategy": "chandelier_trend(trend=100,mult=2.5) stop=2.0ATR no tp"},
        {"ts": "2026-10-21T10:01:00+00:00", "msg": "entry_filled", "bar": "2026-10-21T08:00:00+00:00",
         "price": 100.0, "signal_close": 100.0, "stop": 95.0, "size": 2.0},
        {"ts": "2026-10-21T11:00:00+00:00", "msg": "exit_filled", "price": 105, "entry": 100, "pnl": 9.8,
         "reason": "signal"},
        {"ts": "2026-10-22T09:00:00+00:00", "msg": "exit_filled", "symbol": "BTC/USDT:USDT", "side": "short",
         "price": 99, "entry": 100, "pnl": -2.5, "reason": "stop"},
    ]
    t = dashboard.trades(events, "spot", "BTC/USDT", "4h")
    assert [x["pnl"] for x in t] == [9.8, -2.5]          # oldest first
    assert t[0]["r"] == 0.98 and t[0]["timeframe"] == "4h" and t[0]["bar"].startswith("2026-10-21T08")
    assert t[1]["entry_time"] is None and t[1]["side"] == "short"   # exit without a logged entry
    assert dashboard.parse_label(t[0]["strategy"]).params == {"trend": 100, "mult": 2.5}


def test_parse_label_round_trips_every_logged_form():
    from bot.strategies import StrategySpec
    for spec in (StrategySpec("supertrend", {"mult": 3.0, "trend": 200}, 2.0, 3.0, True),
                 StrategySpec("donchian_breakout", {"entry_n": 20, "exit_n": 10, "trend": 0}, 3.0, None)):
        assert dashboard.parse_label(spec.label()) == spec
    assert dashboard.parse_label("nonsense") is None


def test_health_note_reads_last_section(tmp_path):
    p = tmp_path / "health.md"
    p.write_text("## a - OK\n- fine\n\n## b - ATTENTION\n- Start the spot bot\n- more\n", encoding="utf-8")
    h = dashboard.health_note(str(p))
    assert h["status"] == "ATTENTION" and h["lines"] == ["Start the spot bot", "more"]


def test_is_held_reflects_a_running_bot(tmp_path):
    state = str(tmp_path / "state.json")
    assert not is_held(state)
    held = acquire(state)
    try:
        assert is_held(state)
    finally:
        held.close()
    assert not is_held(state)
