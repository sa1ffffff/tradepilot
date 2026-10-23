"""Market-regime filter for SiGen: hold back trend signals when the market is choppy.

    python -m bot.sigen_regime prove      # the evidence, written to reports/ and data/sigen/regime.json

Chop is measured on closed candles only, at the signal candle:
- efficiency ratio (Kaufman): net move over the last n candles / the sum of every candle's move.
  1 = price went straight; near 0 = it went nowhere the long way round.
- choppiness index (14): 100 = range-bound, low = trending (classic lines 61.8 / 38.2).
- ADX (14): trend strength; under ~20 is commonly read as no trend.
Each is measured on the coin itself and on BTC (crypto chop is often market-wide).

The proof uses SiGen's own history: every out-of-sample walk-forward trade of the strategy
SiGen picked for each coin, 3 years, both markets. Trend strategies only; mean-reversion
rules (Bollinger, RSI(2), overreaction fade) want chop and are never filtered.
1. Calibrate on the older 60% of trades (by entry time): for each measure and threshold,
   how much does skipping the choppy entries raise the average result? Keep the best that
   still leaves at least half the trades.
2. Validate that one rule, untouched, on the newer 40%.
3. Luck check: drop the same number of newer trades at random 5,000 times; the filter must
   beat 90% of those draws.
4. Sanity check on the 30-day replay in the journal.
Rule fixed before looking: switch on only if, on the newer trades, the average gain is at
least +0.05R per signal, the total R doesn't fall, and the luck check passes. Otherwise
SiGen keeps the filter off and the report says why.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from bot import indicators as ind
from bot import sigen

TREND = {"ema_cross", "ema_cross_adx", "donchian_breakout", "breakout_htf", "supertrend", "chandelier_trend",
         "donchian_ensemble", "tsmom", "trend_pullback", "pullback_htf"}
FILE = "regime.json"
# Shadow trial. When the pre-set rule fails validation, this candidate tags live signals
# without blocking them, so it can prove itself on data nobody has seen yet. It is the one
# measure whose effect had the right sign before and after the split (first proof run,
# 2026-10-23). It was picked after seeing the validation set, which is exactly why it has to
# earn its place live and not on history.
SHADOW = {"measure": "er_30", "side": "below", "threshold": 0.20,
          "why": "the only measure that helped before and after the split; picked after seeing both, "
                 "so it must prove itself on live signals"}
TRIAL_MIN = 60   # closed live trend signals per side before the trial says anything
CALIBRATE = 0.6
MIN_KEEP = 0.5
MIN_GAIN_R = 0.05
LUCK = 0.9

# measure -> (direction: "below" means choppy when the value is under the threshold, thresholds)
GRID = {
    "er_30": ("below", [0.10, 0.15, 0.20, 0.25, 0.30]),
    "er_60": ("below", [0.08, 0.12, 0.16, 0.20, 0.25]),
    "chop_14": ("above", [50, 55, 58, 61.8, 65]),
    "adx_14": ("below", [15, 18, 20, 22, 25]),
    "btc_er_30": ("below", [0.10, 0.15, 0.20, 0.25]),
    "btc_chop_14": ("above", [55, 58, 61.8, 65]),
}


def efficiency(close: pd.Series, n: int) -> pd.Series:
    net = (close - close.shift(n)).abs()
    path = close.diff().abs().rolling(n).sum()
    return net / path.replace(0, np.nan)


def choppiness(df: pd.DataFrame, n: int = 14) -> pd.Series:
    tr = ind.atr(df, 1)  # true range of each candle
    span = df["high"].rolling(n).max() - df["low"].rolling(n).min()
    return 100 * np.log10(tr.rolling(n).sum() / span.replace(0, np.nan)) / np.log10(n)


def measures(df: pd.DataFrame, btc: pd.DataFrame | None = None) -> pd.DataFrame:
    """Chop measures per candle, indexed by candle time."""
    c = df["close"].astype(float)
    out = pd.DataFrame({"er_30": efficiency(c, 30), "er_60": efficiency(c, 60), "chop_14": choppiness(df),
                        "adx_14": ind.adx(df, 14)})
    out.index = pd.DatetimeIndex(df["time"])
    if btc is not None:
        b = pd.DataFrame({"btc_er_30": efficiency(btc["close"].astype(float), 30), "btc_chop_14": choppiness(btc)})
        b.index = pd.DatetimeIndex(btc["time"])
        out = out.join(b, how="left")
    return out


def active(root: str = ".") -> dict:
    """What SiGen applies now: {"mode": "on"|"shadow"|"none", "rule": {...}} from the last proof."""
    doc = load(root)
    if doc.get("enabled") and doc.get("rule"):
        return {"mode": "on", "rule": {k: doc["rule"][k] for k in ("measure", "side", "threshold")}}
    if doc.get("shadow"):
        return {"mode": "shadow", "rule": doc["shadow"]}
    return {"mode": "none", "rule": None}


def at(df: pd.DataFrame, i: int, strategy: str, filt: dict) -> dict:
    """Regime at candle i of df (closed candles) for one signal."""
    m = measures(df)
    vals = {k: (round(float(v), 3) if np.isfinite(v) else None) for k, v in m.iloc[i].to_dict().items()}
    rule = filt.get("rule")
    trend = strategy in TREND
    choppy = bool(rule) and is_choppy(vals, rule)
    return {**vals, "trend_strategy": trend, "choppy": choppy, "mode": filt["mode"], "rule": rule,
            "held_back": bool(trend and choppy and filt["mode"] == "on"),
            "would_hold": bool(trend and choppy)}


def is_choppy(values: dict, rule: dict) -> bool:
    v = values.get(rule["measure"])
    if v is None or not np.isfinite(v):
        return False  # unknown: don't hold a signal back on missing data
    return v < rule["threshold"] if rule["side"] == "below" else v > rule["threshold"]


# --- the evidence -------------------------------------------------------------------------
def history(root: str = ".") -> pd.DataFrame:
    """Every out-of-sample trade of each coin's chosen SiGen strategy, with chop at entry."""
    from research import MARKETS as RM, walk_forward
    from bot.data import load_history
    doc = sigen.read(root, "scan.json")
    cfgs = sigen.configs()
    btc = load_history(cfgs["spot"], "BTC/USDT", sigen.TIMEFRAME, sigen.DAYS, refresh=False)
    rows = []
    for res in doc["results"]:
        ch = res.get("chosen")
        if not ch:
            continue
        m, cfg = res["market"], cfgs[res["market"]]
        sig_fn, sim_fn, grid_fn = RM[sigen.RESEARCH_MARKET[m]]
        df = load_history(cfg, res["symbol"], sigen.TIMEFRAME, sigen.DAYS, refresh=False)
        cands = [(spec, sim_fn(sig_fn(df, spec), spec, cfg)[0]) for spec in grid_fn(ch["strategy"])]
        trades = walk_forward(df, cands, cfg, sigen.RESEARCH_MARKET[m])["_trades"]
        meas = measures(df, btc)
        for t in trades:
            if t.entry_time not in meas.index:
                continue
            rows.append({"market": m, "coin": res["coin"], "strategy": ch["strategy"], "trend": ch["strategy"] in TREND,
                         "time": t.entry_time, "side": t.side, "R": float(t.R), **meas.loc[t.entry_time].to_dict()})
    return pd.DataFrame(rows).sort_values("time").reset_index(drop=True)


def stats(r: np.ndarray) -> dict:
    if not len(r):
        return {"trades": 0, "avg_r": None, "total_r": 0.0, "win_rate_pct": None, "profit_factor": None, "max_dd_r": 0.0}
    eq = np.cumsum(r)
    dd = float((eq - np.maximum.accumulate(np.r_[0.0, eq])[1:]).min())
    loss = -r[r < 0].sum()
    return {"trades": int(len(r)), "avg_r": round(float(r.mean()), 3), "total_r": round(float(r.sum()), 1),
            "win_rate_pct": round(100 * float((r > 0).mean()), 1),
            "profit_factor": round(float(r[r > 0].sum() / loss), 2) if loss else None, "max_dd_r": round(dd, 1)}


def held(df: pd.DataFrame, rule: dict) -> np.ndarray:
    v = df[rule["measure"]].to_numpy(dtype=float)
    bad = v < rule["threshold"] if rule["side"] == "below" else v > rule["threshold"]
    return np.where(np.isfinite(v), bad, False) & df["trend"].to_numpy()


def calibrate(cal: pd.DataFrame) -> tuple[dict | None, list[dict]]:
    base = cal["R"].mean()
    tried = []
    for measure, (side, thresholds) in GRID.items():
        if measure not in cal:
            continue
        for th in thresholds:
            rule = {"measure": measure, "side": side, "threshold": th}
            drop = held(cal, rule)
            keep = cal["R"].to_numpy()[~drop]
            tried.append({**rule, "kept_pct": round(100 * len(keep) / len(cal), 1),
                          "avg_r": round(float(keep.mean()), 3) if len(keep) else None,
                          "gain_r": round(float(keep.mean() - base), 3) if len(keep) else None,
                          "held_avg_r": round(float(cal["R"].to_numpy()[drop].mean()), 3) if drop.any() else None})
    ok = [t for t in tried if t["kept_pct"] >= 100 * MIN_KEEP and t["gain_r"] is not None]
    best = max(ok, key=lambda t: t["gain_r"], default=None)
    return best, tried


def luck(val: pd.DataFrame, drop: np.ndarray, n: int = 5000, seed: int = 5) -> float:
    """Share of random drops (same count, among trend trades) the filter beats on average R."""
    r = val["R"].to_numpy()
    trend_idx = np.flatnonzero(val["trend"].to_numpy())
    k = int(drop.sum())
    if k == 0 or k >= len(trend_idx):
        return 0.0
    real = r[~drop].mean()
    rng = np.random.default_rng(seed)
    beats = 0
    for _ in range(n):
        mask = np.zeros(len(r), bool)
        mask[rng.choice(trend_idx, k, replace=False)] = True
        beats += real > r[~mask].mean()
    return beats / n


def replay_check(root: str, rule: dict, fetch=None) -> dict:
    """The 30-day replay in the journal, with and without the filter."""
    from bot import sigen_journal as j
    from bot.data import fetch_closed, public_client
    rows = [r for r in j.evaluate(root, fetch) if r["source"] == "replay" and r["outcome"]["status"] in ("won", "lost", "flat")]
    if not rows:
        return {"signals": 0}
    if fetch is None:
        client = public_client(sigen.configs()["spot"].okx_hostname)
        fetch = lambda s, tf, n: fetch_closed(client, s, tf, n)  # noqa: E731
    btc = fetch("BTC/USDT", sigen.TIMEFRAME, 600)
    cache, flags = {}, []
    for r in rows:
        if r["symbol"] not in cache:
            cache[r["symbol"]] = measures(fetch(r["symbol"], sigen.TIMEFRAME, 600), btc)
        m = cache[r["symbol"]]
        t = pd.Timestamp(r["entry_bar"])
        vals = m.loc[t].to_dict() if t in m.index else {}
        flags.append(r["strategy"] in TREND and is_choppy(vals, rule))
    res = np.array([r["outcome"]["result_r"] for r in rows])
    flags = np.array(flags)
    return {"signals": len(rows), "all": stats(res), "kept": stats(res[~flags]), "held_back": stats(res[flags])}


def prove(root: str = ".", fetch=None) -> dict:
    h = history(root)
    cut = h["time"].iloc[int(len(h) * CALIBRATE)]
    cal, val = h[h["time"] < cut], h[h["time"] >= cut]
    best, tried = calibrate(cal)
    out = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "trades": len(h),
           "trend_trades": int(h["trend"].sum()), "calibrate_until": cut.isoformat(),
           "from": h["time"].iloc[0].isoformat(), "to": h["time"].iloc[-1].isoformat(),
           "rule_fixed": {"min_gain_r": MIN_GAIN_R, "luck": LUCK, "min_keep": MIN_KEEP}, "tried": tried,
           "rule": best}
    if best is None:
        out.update(enabled=False, reason="no threshold kept half the trades and raised the average")
        return out
    rule = {k: best[k] for k in ("measure", "side", "threshold")}
    drop_c, drop_v = held(cal, rule), held(val, rule)
    out["calibration"] = {"all": stats(cal["R"].to_numpy()), "kept": stats(cal["R"].to_numpy()[~drop_c]),
                          "held_back": stats(cal["R"].to_numpy()[drop_c])}
    out["validation"] = {"all": stats(val["R"].to_numpy()), "kept": stats(val["R"].to_numpy()[~drop_v]),
                         "held_back": stats(val["R"].to_numpy()[drop_v])}
    v = out["validation"]
    gain = (v["kept"]["avg_r"] or 0) - (v["all"]["avg_r"] or 0)
    out["validation"]["gain_r"] = round(gain, 3)
    out["validation"]["luck_beaten_pct"] = round(100 * luck(val, drop_v), 1)
    by_market = {}
    for m in sigen.MARKETS:
        part = val[val["market"] == m]
        d = held(part, rule)
        by_market[m] = {"all": stats(part["R"].to_numpy()), "kept": stats(part["R"].to_numpy()[~d])}
    out["validation"]["by_market"] = by_market
    try:
        out["replay"] = replay_check(root, rule, fetch)
    except Exception as e:  # the replay is a sanity check, not part of the decision
        out["replay"] = {"error": repr(e)[:200]}
    checks = {"gain": gain >= MIN_GAIN_R, "total": v["kept"]["total_r"] >= v["all"]["total_r"],
              "luck": bool(out["validation"]["luck_beaten_pct"] >= 100 * LUCK)}
    checks = {k: bool(v) for k, v in checks.items()}
    out["checks"] = checks
    out["enabled"] = all(checks.values())
    out["shadow"] = SHADOW if not out["enabled"] else None
    out["reason"] = ("passed every check on trades it was never tuned on" if out["enabled"] else
                     "failed: " + ", ".join(k for k, ok in checks.items() if not ok))
    return out


def load(root: str = ".") -> dict:
    return sigen.read(root, FILE)


def write_report(doc: dict) -> str:
    os.makedirs("reports", exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    p = os.path.join("reports", f"sigen_regime_{stamp}.md")
    r = doc.get("rule") or {}

    def line(name, s):
        return (f"| {name} | {s['trades']} | {s['avg_r']} | {s['total_r']} | {s['win_rate_pct']} | "
                f"{s['profit_factor']} | {s['max_dd_r']} |")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# SiGen regime filter: evidence ({stamp} UTC)\n\n")
        f.write(f"**Verdict: {'ON' if doc['enabled'] else 'OFF'}** ({doc['reason']}).\n\n")
        f.write(f"{doc['trades']} out-of-sample trades of SiGen's chosen strategies, {doc['from'][:10]} to "
                f"{doc['to'][:10]}, {doc['trend_trades']} of them from trend strategies (the only ones the filter "
                f"can hold back). Calibrated on trades before {doc['calibrate_until'][:10]}, validated after.\n\n")
        if r:
            f.write(f"Rule picked on the older trades: hold back a trend signal when **{r['measure']} is "
                    f"{r['side']} {r['threshold']}** at the signal candle.\n\n")
        for part in ("calibration", "validation"):
            if part in doc:
                f.write(f"## {part.capitalize()}\n\n| set | trades | avg R | total R | win % | PF | max DD (R) |\n|---|---|---|---|---|---|---|\n")
                for k, name in (("all", "every signal"), ("kept", "filter on: kept"), ("held_back", "held back")):
                    f.write(line(name, doc[part][k]) + "\n")
                f.write("\n")
        if "validation" in doc:
            v = doc["validation"]
            f.write(f"Gain on the newer trades: {v['gain_r']:+.3f}R per signal. Beats {v['luck_beaten_pct']}% of "
                    f"random drops of the same size.\n\n")
        rep = doc.get("replay") or {}
        if rep.get("signals"):
            f.write("## 30-day replay (sanity check, not part of the decision)\n\n| set | trades | avg R | total R | win % | PF | max DD (R) |\n|---|---|---|---|---|---|---|\n")
            for k, name in (("all", "every signal"), ("kept", "filter on: kept"), ("held_back", "held back")):
                f.write(line(name, rep[k]) + "\n")
            f.write("\n")
        f.write("## Every rule tried on the older trades\n\n| measure | threshold | kept % | avg R kept | gain R | avg R held back |\n|---|---|---|---|---|---|\n")
        for t in doc["tried"]:
            f.write(f"| {t['measure']} ({t['side']}) | {t['threshold']} | {t['kept_pct']} | {t['avg_r']} | {t['gain_r']} | {t['held_avg_r']} |\n")
    return p


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["prove"])
    p.parse_args()
    doc = prove()
    sigen.write(".", FILE, doc)
    print(json.dumps({k: doc.get(k) for k in ("enabled", "reason", "rule", "checks")}, indent=1, default=str))
    if "validation" in doc:
        v = doc["validation"]
        print("validation all ", v["all"])
        print("validation kept", v["kept"])
        print("held back      ", v["held_back"])
        print("gain", v["gain_r"], "luck beaten", v["luck_beaten_pct"], "%")
        print("by market", json.dumps(v["by_market"], default=str))
    print("replay", json.dumps(doc.get("replay"), default=str))
    print("report:", write_report(doc))


if __name__ == "__main__":
    main()
