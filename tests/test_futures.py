"""Futures sizing, short signals, long/short engine and the futures runner -- no network."""
import dataclasses

import numpy as np
import pandas as pd
import pytest

from config import Config
from bot import futures_runner as fr
from bot.engine import simulate_ls
from bot.futures import futures_cfg, leverage_for, plan
from bot.risk import RiskManager
from bot.strategies import StrategySpec, invert, signals, signals_ls

CFG = futures_cfg(dataclasses.replace(Config(), max_cost_per_r=0))


def frame(closes, spread=0.001):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    return pd.DataFrame({
        "time": pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC"),
        "open": closes, "high": closes * (1 + spread), "low": closes * (1 - spread),
        "close": closes, "volume": np.ones(n),
    })


# --- sizing --------------------------------------------------------------------
def test_leverage_falls_as_stops_widen_and_respects_cap():
    assert leverage_for(0.005, CFG) == CFG.fut_max_leverage
    assert leverage_for(0.08, CFG) < leverage_for(0.03, CFG) <= CFG.fut_max_leverage
    assert leverage_for(0.5, CFG) == 1


@pytest.mark.parametrize("stop_pct", [0.005, 0.01, 0.03, 0.08])
@pytest.mark.parametrize("direction", [1, -1])
def test_plan_keeps_liquidation_beyond_stop_and_margin_under_cap(stop_pct, direction):
    p = plan(5000, 80000, 80000 * stop_pct, direction, CFG)
    liq_dist = abs(80000 - p.liq_price)
    assert liq_dist >= CFG.fut_liq_buffer * 80000 * stop_pct * 0.99
    assert direction * (p.stop_price - p.liq_price) > 0          # stop comes first
    assert p.margin <= 5000 * CFG.fut_max_margin_fraction + 1e-6
    assert p.size * 80000 * stop_pct <= 5000 * CFG.fut_risk_fraction + 1e-6


def test_tight_stop_is_capped_by_margin():
    p = plan(5000, 80000, 80, 1, CFG)  # 0.1% stop would want a $100k position
    assert p.margin == pytest.approx(5000 * CFG.fut_max_margin_fraction)


# --- short signals ---------------------------------------------------------------
def test_inverted_chart_mirrors_signals():
    up = [100.0] * 80 + [130.0]
    spec = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, shorts=True)
    s = signals_ls(frame(up), spec)
    assert s["entry"].iloc[-1] and s["short_exit"].iloc[-1] and not s["short_entry"].iloc[-1]
    down = [100.0] * 80 + [70.0]
    s = signals_ls(frame(down), spec)
    assert s["short_entry"].iloc[-1] and not s["entry"].iloc[-1]
    inv = invert(frame(down))
    assert (inv["high"] >= inv["low"]).all()


def test_long_only_spec_has_no_short_signals():
    s = signals_ls(frame([100.0] * 80 + [70.0]), StrategySpec("ema_cross", {"fast": 9, "slow": 21}))
    assert not s["short_entry"].any()


# --- engine ------------------------------------------------------------------------
def test_short_profits_when_price_falls():
    closes = [100.0] * 80 + [99.0] + list(np.linspace(98, 80, 10))
    spec = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=5.0, shorts=True)
    trades, _, eq = simulate_ls(signals_ls(frame(closes), spec), spec, CFG)
    assert trades[0].side == "short" and trades[0].pnl > 0 and eq > CFG.backtest_start_equity


def test_short_stop_and_fees():
    closes = [100.0] * 80 + [99.0] + [104.0]  # through the stop, well short of liquidation
    spec = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=2.0, shorts=True)
    trades, _, _ = simulate_ls(signals_ls(frame(closes), spec), spec, CFG)
    t = trades[0]
    assert t.side == "short" and t.reason == "stop" and t.pnl < 0
    assert t.R < -1  # a full risk unit plus the gap through the stop and costs


def test_gap_beyond_liquidation_loses_only_the_margin():
    closes = [100.0] * 80 + [99.0] + [130.0]
    spec = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=2.0, shorts=True)
    trades, _, eq = simulate_ls(signals_ls(frame(closes), spec), spec, CFG)
    assert trades[0].reason == "liquidated"
    assert eq > CFG.backtest_start_equity * (1 - CFG.fut_max_margin_fraction) - 5  # isolated


# --- runner ----------------------------------------------------------------------------
class FakeFutures:
    min_contracts, contract_size = 0.01, 0.01

    def __init__(self, closes, symbol="BTC/USDT:USDT"):
        self.cfg = dataclasses.replace(CFG, symbol=symbol)
        self.df = frame(closes)
        self.pos = None
        self.algos = []
        self.calls = []
        self.fail_protection = False

    def fetch_closed_ohlcv(self, bars):
        return self.df

    def equity_quote(self):
        return 5000.0

    def to_contracts(self, base):
        return round(np.floor(base / 0.01 / 0.01 + 1e-9) * 0.01, 8)

    def set_leverage(self, lev):
        self.calls.append(("lev", lev))

    def position(self):
        return dict(self.pos) if self.pos else None

    def open(self, d, contracts):
        self.calls.append(("open", d, contracts))
        px = float(self.df["close"].iloc[-1])
        self.pos = {"dir": d, "contracts": contracts, "size": contracts * 0.01, "entry": px,
                    "liq": px * (1 - d * 0.19), "margin": 100.0}
        return {"id": "o1", "status": "closed", "filled": contracts, "size": contracts * 0.01,
                "average": px, "fee_quote": 0.1, "fee_base": 0.0, "maker_share": 1.0}

    def close(self, d, contracts, urgent=False):
        self.calls.append(("close", d, contracts))
        self.pos = None
        return {"id": "c1", "status": "closed", "filled": contracts, "average": 101.0,
                "fee_quote": 0.1, "maker_share": 1.0}

    def place_protection(self, d, stop, tp=None):
        if self.fail_protection:
            raise RuntimeError("rejected")
        self.algos = [("sl", d, stop, tp)]
        return "a1"

    def pending_protection(self):
        return ["a1"] if self.algos else []

    def cancel_protection(self):
        self.algos = []

    def closed_pnl(self, opened_ms, tries=5):
        return {"pnl": -12.5, "close_price": 99.0, "fee": -0.2, "funding": 0.0, "kind": "closed"}


class Log:
    def __init__(self):
        self.events = []

    def _r(self, msg, fields=None):
        self.events.append((msg, fields))

    info = warning = error = exception = _r


@pytest.fixture
def fcfg(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return dataclasses.replace(CFG, state_file="state_futures.json", symbol="BTC/USDT:USDT")


SPEC = StrategySpec("ema_cross", {"fast": 9, "slow": 21}, stop_atr=2.0, shorts=True)


def new_state(cfg):
    return fr.Store(cfg.state_file)


def test_short_entry_places_exchange_stop(fcfg):
    ex = FakeFutures([100.0] * 80 + [70.0])
    state, log = new_state(fcfg), Log()
    fr.step(fcfg, SPEC, ex, RiskManager(fcfg), state, log)
    assert state.slot(fcfg.symbol)["position"]["side"] == "short"
    assert ex.algos and ex.algos[0][2] > 70.0          # short stop above entry
    assert ex.calls[0][0] == "lev" and 1 <= ex.calls[0][1] <= fcfg.fut_max_leverage


def test_stop_failure_closes_position_immediately(fcfg):
    ex = FakeFutures([100.0] * 80 + [130.0])
    ex.fail_protection = True
    state, log = new_state(fcfg), Log()
    fr.step(fcfg, SPEC, ex, RiskManager(fcfg), state, log)
    assert state.slot(fcfg.symbol)["position"] is None and ex.pos is None
    assert any(m == "stop_failed_closing" for m, _ in log.events)


def test_exchange_stop_close_is_recorded(fcfg):
    ex = FakeFutures([100.0] * 80 + [130.0])
    risk, state, log = RiskManager(fcfg), new_state(fcfg), Log()
    fr.step(fcfg, SPEC, ex, risk, state, log)
    ex.pos = None                                      # OKX's stop closed it
    fr.step(fcfg, SPEC, ex, risk, state, log)
    assert state.slot(fcfg.symbol)["position"] is None and risk.realized_pnl_today == -12.5


def test_missing_stop_is_replaced(fcfg):
    ex = FakeFutures([100.0] * 80 + [130.0])
    risk, state, log = RiskManager(fcfg), new_state(fcfg), Log()
    fr.step(fcfg, SPEC, ex, risk, state, log)
    ex.algos = []
    fr.step(fcfg, SPEC, ex, risk, state, log)
    assert ex.algos and any(m == "stop_missing_replacing" for m, _ in log.events)


def test_reversal_on_opposite_signal(fcfg):
    ex = FakeFutures([100.0] * 80 + [130.0])
    risk, state = RiskManager(fcfg), new_state(fcfg)
    fr.step(fcfg, SPEC, ex, risk, state, Log())
    ex.df = frame([130.0] * 81 + [90.0])  # one bar later
    fr.step(fcfg, SPEC, ex, risk, state, Log())
    assert [c[0] for c in ex.calls if c[0] != "lev"] == ["open", "close", "open"]
    assert state.slot(fcfg.symbol)["position"]["side"] == "short"


def test_foreign_position_blocks_trading(fcfg):
    ex = FakeFutures([100.0] * 80 + [130.0])
    ex.pos = {"dir": 1, "contracts": 1.0, "size": 0.01, "entry": 100.0, "liq": 50.0, "margin": 10}
    state, log = new_state(fcfg), Log()
    fr.step(fcfg, SPEC, ex, RiskManager(fcfg), state, log)
    assert not any(c[0] == "open" for c in ex.calls)
    assert any(m == "foreign_position" for m, _ in log.events)


def test_kill_switch_blocks_futures_entry(fcfg):
    open(fcfg.kill_file, "w").close()
    ex = FakeFutures([100.0] * 80 + [130.0])
    fr.step(fcfg, SPEC, ex, RiskManager(fcfg), new_state(fcfg), Log())
    assert not any(c[0] == "open" for c in ex.calls)


def test_margin_cap_is_shared_across_strategies(fcfg):
    risk, store = RiskManager(fcfg), new_state(fcfg)
    store.slot("ETH/USDT:USDT")["position"] = {"margin": 5000 * fcfg.fut_max_margin_fraction}
    ex = FakeFutures([100.0] * 80 + [130.0])
    log = Log()
    fr.step(fcfg, SPEC, ex, risk, store, log)  # BTC: no margin room left
    assert not any(c[0] == "open" for c in ex.calls)
    assert any(m == "entry_skipped" for m, _ in log.events)


def test_state_survives_restart(fcfg):
    ex = FakeFutures([100.0] * 80 + [130.0])
    store = new_state(fcfg)
    fr.step(fcfg, SPEC, ex, RiskManager(fcfg), store, Log())
    again = fr.Store(fcfg.state_file)
    assert again.slot(fcfg.symbol)["position"]["side"] == "long"


def test_two_strategies_on_one_symbol_are_refused(tmp_path):
    import json
    for name in ("a.json", "b.json"):
        (tmp_path / name).write_text(json.dumps({"symbol": "BTC/USDT:USDT", "timeframe": "1h",
                                                 "name": "ema_cross", "params": {"fast": 9, "slow": 21}}))
    cfg = dataclasses.replace(CFG, strategy_file=f"{tmp_path / 'a.json'},{tmp_path / 'b.json'}")
    with pytest.raises(SystemExit):
        fr.load_futures_strategies(cfg)


def test_strategy_file_can_lower_risk_for_a_test_slot():
    from bot.futures_runner import load_futures_strategy
    cfg, spec = load_futures_strategy(futures_cfg(Config()), "strategies/futures_test_btc_5m_swap.json")
    assert (cfg.symbol, cfg.timeframe, cfg.fut_risk_fraction) == ("BTC/USDT:USDT", "5m", 0.003)
    assert spec.shorts
