"""The Time Machine replays: deterministic, bounded, and correct on known inputs."""
from types import SimpleNamespace

import numpy as np
import pandas as pd

from bot.timemachine import month_bootstrap, months_of, summary, trade_bootstrap, trade_odds


def test_all_winners_never_lose():
    rep = trade_bootstrap(np.array([1.0, 2.0]), 10, 0.02, paths=500)
    s = summary(rep)
    assert s["p_loss_pct"] == 0 and s["bad_max_dd_pct"] == 0 and s["bad_losing_streak"] == 0


def test_known_compounding():
    rep = trade_bootstrap(np.array([-1.0]), 3, 0.02, paths=10)
    assert np.allclose(rep.final, 0.98 ** 3)
    assert np.allclose(rep.max_dd, 1 - 0.98 ** 3)
    assert (rep.streak == 3).all()


def test_same_seed_same_answer():
    r = np.random.default_rng(0).normal(0.1, 1.5, 200)
    a = summary(trade_bootstrap(r, 50, 0.02, paths=2000, seed=7))
    b = summary(trade_bootstrap(r, 50, 0.02, paths=2000, seed=7))
    assert a == b


def test_huge_loss_cannot_take_equity_below_zero():
    rep = trade_bootstrap(np.array([-500.0]), 2, 0.02, paths=5)
    assert (rep.final >= 0).all()


def _t(day, R, reason="stop"):
    return SimpleNamespace(exit_time=pd.Timestamp(day, tz="UTC"), R=R, reason=reason)


def test_months_keep_coins_together_and_include_empty_months():
    months = months_of({"A": [_t("2025-01-05", -1), _t("2025-03-02", 2)],
                        "B": [_t("2025-01-20", -1)]})
    assert len(months) == 3                        # Jan, (empty) Feb, Mar
    assert list(months[0]) == [-1, -1] and len(months[1]) == 0 and list(months[2]) == [2]


def test_month_bootstrap_of_a_single_month():
    rep = month_bootstrap([np.array([-1.0, 1.0])], 2, 0.02, paths=3)
    assert (rep.trades == 4).all()


def test_trade_odds():
    o = trade_odds([_t("2025-01-01", -1), _t("2025-01-02", 3, "tp"), _t("2025-01-03", 0.5, "signal")])
    assert o["win_pct"] == 66.7 and o["stop_pct"] == 33.3 and o["tp_pct"] == 33.3
    assert o["avg_win_R"] == 1.75 and o["worst_R"] == -1.0
