"""SiGen: terms gate, the AI model, signal levels and the API lock."""
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import numpy as np
import pandas as pd
import pytest

import dashboard
from bot import sigen
from bot.engine import simulate, simulate_ls
from bot.strategies import STRATEGIES, StrategySpec, signals, signals_ls
from tests.test_console import _frame

ALL = [k for k, _ in sigen.TERMS["statements"]]


def test_terms_need_every_statement_and_a_name(tmp_path):
    root = str(tmp_path)
    assert not sigen.acceptance(root)["accepted"]
    with pytest.raises(ValueError):
        sigen.accept("Alex Morgan", ALL[:-1], sigen.TERMS["version"], root)
    with pytest.raises(ValueError):
        sigen.accept(" ", ALL, sigen.TERMS["version"], root)
    with pytest.raises(ValueError):
        sigen.accept("Alex Morgan", ALL, "an-old-version", root)
    a = sigen.accept("  Alex   Morgan ", ALL, sigen.TERMS["version"], root)
    assert a["accepted"] and a["name"] == "Alex Morgan" and a["accepted_at"]


def test_changed_terms_ask_again(tmp_path, monkeypatch):
    root = str(tmp_path)
    sigen.accept("Alex Morgan", ALL, sigen.TERMS["version"], root)
    changed = json.loads(json.dumps(sigen.TERMS))
    changed["sections"][0][1] += " Something new."
    monkeypatch.setattr(sigen, "TERMS", changed)
    assert not sigen.acceptance(root)["accepted"]   # same version, different text


def _samples(n=3000, seed=1):
    """Synthetic trades where the first feature decides the odds."""
    rng = np.random.default_rng(seed)
    names = list(STRATEGIES)
    out = []
    for k in range(n):
        x = rng.normal(0, 1, len(sigen.FEATURES))
        p = 1 / (1 + np.exp(-1.5 * x[0]))
        out.append({"x": x.tolist(), "win": int(rng.random() < p), "strategy": names[k % 3], "dir": 1 if k % 2 else -1,
                    "time": (pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(hours=4 * k)).isoformat(),
                    "coin": "BTC" if k % 2 else "ETH"})
    return out


def test_model_learns_a_real_pattern_and_flags_strange_markets():
    m = sigen.Model.train(_samples())
    assert m.d["holdout"]["auc"] > 0.7                       # it found the planted signal ...
    good = m.predict(np.r_[2.0, np.zeros(len(sigen.FEATURES) - 1)], list(STRATEGIES)[0], 1)
    bad = m.predict(np.r_[-2.0, np.zeros(len(sigen.FEATURES) - 1)], list(STRATEGIES)[0], 1)
    assert good["p_win"] > 0.7 > 0.3 > bad["p_win"] and not good["unusual"]
    far = m.predict(np.full(len(sigen.FEATURES), 9.0), list(STRATEGIES)[0], 1)
    assert far["unusual"]                                     # ... and knows when it is out of its depth


def test_model_with_no_pattern_gets_no_weight():
    rng = np.random.default_rng(4)
    s = _samples()
    for x in s:
        x["win"] = int(rng.random() < 0.4)
    m = sigen.Model.train(s)
    assert abs(m.d["holdout"]["auc"] - 0.5) < 0.06
    chosen = {"r": [1.0, -1.0] * 20, "folds_positive": 2, "strategy": list(STRATEGIES)[0]}
    c = sigen.confidence(chosen, {"p_win": 0.9, "unusual": False}, {**m.d, "holdout": {**m.d["holdout"], "auc": 0.5}})
    assert c["parts"]["ai_weight"] == 0 and 0 <= c["score"] <= 100


def test_confidence_is_bounded_and_cut_in_unusual_markets():
    model = {"holdout": {"auc": 0.6}, "base_rates": {"supertrend": 0.4}, "base_rate": 0.4}
    chosen = {"r": [2.0, -1.0, 1.5, -1.0, 3.0] * 10, "folds_positive": 4, "strategy": "supertrend"}
    hi = sigen.confidence(chosen, {"p_win": 0.6, "unusual": False}, model)
    odd = sigen.confidence(chosen, {"p_win": 0.6, "unusual": True}, model)
    assert hi["score"] <= 100 and hi["label"] == "High"
    assert odd["score"] == round(hi["score"] * 0.75) or abs(odd["score"] - hi["score"] * 0.75) <= 1


@pytest.mark.parametrize("market", ["spot", "futures"])
def test_open_position_is_reported(market):
    df = _frame(1200)
    spec = StrategySpec("donchian_breakout", dict(STRATEGIES["donchian_breakout"].defaults), 2.0, None,
                        shorts=market == "futures")
    cfg = sigen.configs()[market]
    held = {}
    sig = signals_ls(df, spec) if market == "futures" else signals(df, spec)
    trades, _, _ = (simulate_ls if market == "futures" else simulate)(sig, spec, cfg, open_out=held)
    if trades and trades[-1].reason == "end":
        assert held and held["entry"] == trades[-1].entry and held["init_dist"] > 0
    else:
        assert held == {}


def _scan_result(market):
    spec = StrategySpec("donchian_breakout", dict(STRATEGIES["donchian_breakout"].defaults), 2.0, 3.0,
                        shorts=market == "futures")
    chosen = {"strategy": spec.name, "spec": spec.to_dict(), "r": [1.5, -1.0, 2.0, -1.0] * 10, "trades": 40,
              "wins": 20, "win_rate_pct": 50.0, "profit_factor": 1.75, "avg_win_r": 1.75, "avg_loss_r": 1.0,
              "folds_positive": 3, "total_return_pct": 12.0, "max_drawdown_pct": -8.0}
    return {"coin": "TST", "market": market, "symbol": sigen.pair("TST", market), "chosen": chosen}


@pytest.mark.parametrize("market", ["spot", "futures"])
@pytest.mark.parametrize("cut", [700, 820, 950, 1100, 1199])
def test_signal_levels_are_on_the_right_side(market, cut):
    model = sigen.Model(sigen.Model.train(_samples(1500)).d)
    df = _frame(1200).iloc[:cut + 1].reset_index(drop=True)
    s = sigen.signal_for(_scan_result(market), model, df, sigen.configs()[market])
    assert s["state"] in sigen.ORDER and s["instruction"] and s["action"]
    if s["state"] in ("entry", "armed") or (s["state"] == "holding" and s["entry"]):
        d = 1 if s["direction"] == "long" else -1
        assert d * (s["entry"] - s["stop"]) > 0 if s["state"] != "holding" else True
        if s["target"]:
            assert d * (s["target"] - s["entry"]) > 0
    if market == "spot":
        assert s["direction"] in (None, "long")
    assert 0 <= s["confidence"]["score"] <= 100


def test_signals_api_is_locked_until_terms_are_accepted(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "HERE", str(tmp_path))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), dashboard.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    def call(path, body=None):
        req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(),
                                     headers={"X-Tradepilot": "1", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    try:
        assert call("/api/sigen")[1]["terms"]["accepted"] is False
        assert call("/api/sigen/signals?market=spot")[0] == 403
        assert call("/api/sigen/accept", {"name": "A", "statements": ALL, "version": sigen.TERMS["version"]})[0] == 400
        code, res = call("/api/sigen/accept", {"name": "Alex Morgan", "statements": ALL,
                                               "version": sigen.TERMS["version"]})
        assert code == 200 and res["ok"]
        code, res = call("/api/sigen/signals?market=spot")
        assert code == 200 and res["scanned"] is False
    finally:
        srv.shutdown()
