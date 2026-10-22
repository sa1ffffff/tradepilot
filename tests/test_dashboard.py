from datetime import datetime, timezone

import dashboard
from bot.lock import acquire, is_held


def test_trades_and_summary():
    events = [
        {"ts": "2026-10-21T10:00:00+00:00", "msg": "started"},
        {"ts": "2026-10-21T11:00:00+00:00", "msg": "exit_filled", "price": 101, "entry": 100, "pnl": 1.0, "reason": "signal"},
        {"ts": "2026-10-22T09:00:00+00:00", "msg": "exit_filled", "symbol": "BTC/USDT:USDT", "side": "short",
         "price": 99, "entry": 100, "pnl": -2.5, "reason": "stop"},
    ]
    t = dashboard.trades(events, "Spot", "BTC/USDT")
    assert [x["pnl"] for x in t] == [-2.5, 1.0]          # newest first
    assert t[1]["symbol"] == "BTC/USDT" and t[0]["side"] == "short"
    day = dashboard.summarise(t, datetime(2026, 10, 22, tzinfo=timezone.utc))
    assert day == {"pnl": -2.5, "trades": 1, "wins": 0}


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
