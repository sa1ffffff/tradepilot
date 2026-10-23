"""How realistic is a daily profit target? An estimate from research evidence.

Each strategy file carries its out-of-sample record: trade count, win rate and
profit factor over the walk-forward test (4 of 5 segments of ~3 years, about
876 days). From those we rebuild a simple trade model per strategy: trades
arrive at the measured rate, a loss costs 1R (the stop), and a win pays the
average R that makes the profit factor come out right. Simulating many days
of that, in random trade order, with the daily loss limit and the target both
cutting the day short, says how often a target would have been reached.

It's a model, not a promise: it ignores how trades cluster in trending
markets, and it assumes the future looks like the test period.
"""
from __future__ import annotations

import numpy as np

OOS_DAYS = 1095 * 4 / 5


def trade_model(evidence: dict) -> dict | None:
    n, wr, pf = evidence.get("trades"), evidence.get("win_rate_pct"), evidence.get("profit_factor")
    if not n or not wr or not pf or wr <= 0 or wr >= 100:
        return None
    p = wr / 100
    return {"per_day": n / OOS_DAYS, "p_win": p, "win_r": pf * (1 - p) / p}


def assess(target_usd: float, funds: float, slots: list[dict], daily_loss_usd: float,
           days: int = 20_000, seed: int = 7) -> dict:
    """slots: [{"label", "evidence", "risk_fraction"}]. Returns the estimate."""
    models = []
    for s in slots:
        m = trade_model(s.get("evidence") or {})
        if m:
            models.append({**m, "risk_usd": funds * s["risk_fraction"], "label": s["label"]})
    if not models or funds <= 0 or target_usd <= 0:
        return {"ok": False, "reason": "no research evidence to estimate from" if not models
                else "funds and target must be positive"}

    rng = np.random.default_rng(seed)
    hit = loss_stop = 0
    totals = np.empty(days)
    trades_per_day = sum(m["per_day"] for m in models)
    for i in range(days):
        pnls = []
        for m in models:
            k = rng.poisson(m["per_day"])
            wins = rng.random(k) < m["p_win"]
            pnls += list(np.where(wins, m["win_r"], -1.0) * m["risk_usd"])
        rng.shuffle(pnls)
        total = 0.0
        for x in pnls:
            total += x
            if total >= target_usd:
                hit += 1
                break
            if total <= -daily_loss_usd:
                loss_stop += 1
                break
        totals[i] = total

    risk_usd = float(np.mean([m["risk_usd"] for m in models]))
    avg_win = float(np.mean([m["win_r"] * m["risk_usd"] for m in models]))
    expected_day = sum(m["per_day"] * (m["p_win"] * m["win_r"] - (1 - m["p_win"])) * m["risk_usd"]
                       for m in models)
    p_hit = hit / days
    pct = target_usd / funds * 100
    if p_hit >= 0.25:
        verdict, summary = "realistic", "Reachable on a fair share of days at the current risk."
    elif p_hit >= 0.08:
        verdict, summary = "stretch", "Reachable on some days, but most days end below it."
    else:
        verdict, summary = "unlikely", "Rarely reached at the current risk; the bots would almost never stop early."
    notes = [
        f"The target is {pct:.1f}% of ${funds:,.0f} in one day.",
        f"The bots average {trades_per_day:.2f} trades a day across {len(models)} strategies, "
        f"so many days have no trade at all.",
        f"Each trade risks about ${risk_usd:,.2f}; an average winner makes about ${avg_win:,.2f}.",
        f"Expected result of an average day: ${expected_day:+,.2f}.",
    ]
    if target_usd > avg_win * 1.5:
        need = target_usd / avg_win * (risk_usd / funds) * 100
        notes.append(f"Hitting it with one average winner would take about {need:.1f}% risk per trade, "
                     f"which would make losing days just as much bigger. The target doesn't change risk.")
    return {
        "ok": True, "target_usd": target_usd, "funds": funds, "target_pct": round(pct, 2),
        "p_hit_day": round(p_hit, 4), "p_loss_limit_day": round(loss_stop / days, 4),
        "p_no_trade_day": round(float(np.exp(-trades_per_day)), 4),
        "expected_day_usd": round(expected_day, 2), "trades_per_day": round(trades_per_day, 3),
        "risk_per_trade_usd": round(risk_usd, 2), "avg_win_usd": round(avg_win, 2),
        "days_to_first_hit": round(1 / p_hit, 1) if p_hit else None,
        "verdict": verdict, "summary": summary, "notes": notes,
        "method": "Simulated from each strategy's out-of-sample research record (trade rate, win rate, "
                  "profit factor). An estimate, not a forecast.",
    }
