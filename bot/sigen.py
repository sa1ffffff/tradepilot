"""SiGen: trading signals for the 25 largest coins, each from a strategy that
passed out-of-sample testing on that coin, with an AI read of how much to trust it.

    python -m bot.sigen scan          # research + AI model, a few minutes; writes data/sigen/
    python -m bot.sigen signals       # print the current signals (both markets)
    python -m bot.sigen record        # log this candle's new signals to the journal (bot/sigen_journal.py)
    python -m bot.sigen backfill      # replay the last 30 days into the journal, marked as replays
    python -m bot.sigen report        # how logged signals turned out

How a signal is made
1. Universe: the 25 largest coins by market cap (CoinGecko) that OKX lists both
   as spot BASE/USDT and as a USDT perpetual. Stablecoins and metal tokens are
   left out. If CoinGecko can't be reached, OKX's 24h futures volume ranks them.
2. Testing: for every coin and market (spot: long only; futures: long and
   short), every strategy in bot/strategies.py goes through research.py's
   anchored walk-forward on 3 years of 4h candles with measured costs. A coin
   gets a strategy only if one passes the same gate the bots use (CANDIDATE);
   of those, the most consistent (highest out-of-sample t-stat) is used.
3. AI layer, after FreqAI's ideas (no FreqAI code): a logistic model learns
   from every out-of-sample trade of every strategy on every coin which market
   conditions at entry came before winners. It is retrained on every scan and
   scored on the most recent 30% of trades it never saw, and its weight in
   the confidence score follows that score. A dissimilarity index (distance
   from today's conditions to the nearest training example, over the typical
   distance between examples) flags markets the model hasn't seen.
4. Live: on each closed 4h candle the chosen strategy is replayed to the last
   bar. That gives the action (buy now, hold, exit, or the close that would
   trigger an entry), the stop-loss, the target and the exit rule.

Confidence (0-100) weighs edge certainty (bootstrap of the out-of-sample
trades) 50%, consistency across the 4 test folds 20% and the AI's read of the
setup 30%, cut by a quarter when the market is unlike anything in training.
It measures evidence, not a promise. Picking the best of 13 strategies per
coin flatters the historical numbers a little; win rates are shrunk toward
each strategy's average across all coins to offset some of that.

Public market data only; SiGen never reads API keys and never places orders.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from bot import indicators as ind

TIMEFRAME = "4h"
DAYS = 1095
UNIVERSE = 25
MIN_BARS = 1500                 # ~250 days of 4h candles before a coin can be tested
MARKETS = ("spot", "futures")
RESEARCH_MARKET = {"spot": "spot", "futures": "swap"}
DIR = os.path.join("data", "sigen")
SHRINK_TRADES = 30              # win-rate shrinkage toward the strategy's all-coin average
HOLDOUT = 0.3
CHASE_R = 0.3                   # don't enter once price is this many R past the signal's entry
NOT_COINS = {"USDT", "USDC", "DAI", "USDS", "USDE", "FDUSD", "TUSD", "PYUSD", "USD1", "RLUSD", "USDG",
             "USDD", "USDF", "USDY", "USYC", "BUIDL", "EURC", "XAUT", "PAXG", "WBTC", "WETH", "STETH",
             "WSTETH", "WEETH", "CBBTC", "LEO"}

FEATURES = ["mom_6", "mom_42", "mom_180", "ema50_atr", "ema200_atr", "rsi14", "atr_pct",
            "vol_regime", "volume_z", "channel_pos"]
FEATURE_TEXT = {
    "mom_6": "move over the last day", "mom_42": "move over the last week", "mom_180": "move over the last month",
    "ema50_atr": "price vs its 50-candle average", "ema200_atr": "price vs its 200-candle average",
    "rsi14": "overbought or oversold (RSI)", "atr_pct": "how jumpy the price is", "vol_regime": "jumpiness vs normal",
    "volume_z": "trading volume vs normal", "channel_pos": "where price sits in its recent range",
}


def path(root: str, name: str) -> str:
    return os.path.join(root, DIR, name)


def configs():
    from config import Config
    from bot.futures import futures_cfg
    base = dataclasses.replace(Config(), maker_fill_rate=0.54)  # measured on the demo account
    return {"spot": base, "futures": dataclasses.replace(futures_cfg(Config()), maker_fill_rate=0.54)}


def pair(coin: str, market: str) -> str:
    return f"{coin}/USDT" + (":USDT" if market == "futures" else "")


# --- universe ---------------------------------------------------------------------
def universe(client, n: int = UNIVERSE) -> tuple[list[str], str]:
    """The n largest coins OKX lists as both spot and USDT perpetual."""
    client.load_markets()
    listed = {m.split("/")[0] for m in client.markets if m.endswith("/USDT") and client.markets[m]["spot"]}
    listed &= {m.split("/")[0] for m in client.markets if m.endswith("/USDT:USDT")}
    listed -= NOT_COINS
    try:
        import urllib.request
        url = ("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc"
               "&per_page=150&page=1")
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "tradepilot-sigen"})
        with urllib.request.urlopen(req, timeout=15) as r:
            ranked = [c["symbol"].upper() for c in json.load(r)]
        coins = list(dict.fromkeys(c for c in ranked if c in listed))[:n]
        if len(coins) >= n * 0.8:
            return coins, "CoinGecko market cap"
    except Exception:
        pass
    tickers = client.fetch_tickers(params={"instType": "SWAP"})
    vol = []
    for s, t in tickers.items():
        base = s.split("/")[0]
        if s.endswith("/USDT:USDT") and base in listed:
            size = client.markets[s].get("contractSize") or 1
            vol.append(((t.get("baseVolume") or 0) * size * (t.get("last") or 0), base))
    return [b for _, b in sorted(vol, reverse=True)[:n]], "OKX 24h futures volume"


# --- features (direction-aligned: shorts are measured on the mirrored chart) -------
def features(df: pd.DataFrame) -> np.ndarray:
    c = df["close"].astype(float)
    r = np.log(c).diff()
    vol = r.rolling(100, min_periods=50).std()
    a = ind.atr(df, 14)
    out = {f"mom_{n}": np.log(c / c.shift(n)) / (vol * np.sqrt(n)) for n in (6, 42, 180)}
    out["ema50_atr"] = (c - ind.ema(c, 50)) / a
    out["ema200_atr"] = (c - ind.ema(c, 200)) / a
    out["rsi14"] = (ind.rsi(c, 14) - 50) / 50
    out["atr_pct"] = np.log(a / c)
    out["vol_regime"] = np.log(r.rolling(20).std() / r.rolling(200).std())
    v = np.log(df["volume"].astype(float).replace(0, np.nan))
    out["volume_z"] = (v - v.rolling(50).mean()) / v.rolling(50).std()
    hi, lo = c.rolling(55).max(), c.rolling(55).min()
    out["channel_pos"] = (c - lo) / (hi - lo) - 0.5
    x = pd.DataFrame(out)[FEATURES].replace([np.inf, -np.inf], np.nan)
    return x.clip(-10, 10).to_numpy(dtype=float)


# --- the scan: one coin, one market ------------------------------------------------
def scan_one(job: tuple[str, str]) -> dict:
    """Walk-forward every strategy on one coin and market. Runs in a worker process."""
    from research import MARKETS as RM, pick, walk_forward
    from bot.data import load_history
    from bot.strategies import STRATEGIES, invert
    coin, market = job
    cfg = configs()[market]
    rmarket = RESEARCH_MARKET[market]
    sig_fn, sim_fn, grid_fn = RM[rmarket]
    symbol = pair(coin, market)
    out = {"coin": coin, "market": market, "symbol": symbol}
    try:
        df = load_history(cfg, symbol, TIMEFRAME, DAYS, refresh=False)
    except BaseException as e:  # load_history raises SystemExit when nothing is cached
        return {**out, "error": f"no price history ({e})"[:200]}
    out["bars"] = len(df)
    if len(df) < MIN_BARS:
        return {**out, "error": f"only {len(df) // 6} days of price history; SiGen needs {MIN_BARS // 6}"}

    fx = {1: features(df), -1: features(invert(df))}
    index = pd.Index(df["time"])
    rows, samples = [], []
    for name in STRATEGIES:
        cands = [(spec, sim_fn(sig_fn(df, spec), spec, cfg)[0]) for spec in grid_fn(name)]
        m = walk_forward(df, cands, cfg, rmarket)
        trades = m.pop("_trades")
        row = {"strategy": name, **{k: m[k] for k in ("trades", "win_rate_pct", "profit_factor", "avg_R",
                                                       "t_stat", "total_return_pct", "max_drawdown_pct",
                                                       "folds_positive", "verdict")}}
        idx = index.get_indexer([t.entry_time for t in trades])
        for t, i in zip(trades, idx):
            if i < 0:
                continue
            d = 1 if t.side == "long" else -1
            samples.append({"x": fx[d][i].tolist(), "win": int(t.R > 0), "strategy": name, "dir": d,
                            "time": t.entry_time.isoformat(), "coin": coin})
        if m["verdict"] == "CANDIDATE":
            spec = pick(cands, df["time"].iloc[-1] + pd.Timedelta(days=1))
            row["spec"] = spec.to_dict()
            row["label"] = spec.label()
            r = np.array([t.R for t in trades])
            row["r"] = [round(float(v), 3) for v in r]
            row["avg_win_r"] = round(float(r[r > 0].mean()), 2) if (r > 0).any() else 0.0
            row["avg_loss_r"] = round(float(-r[r <= 0].mean()), 2) if (r <= 0).any() else 0.0
            row["wins"] = int((r > 0).sum())
        rows.append(row)
    passing = [r for r in rows if r["verdict"] == "CANDIDATE"]
    out["rows"] = rows
    out["chosen"] = max(passing, key=lambda r: r["t_stat"]) if passing else None
    out["samples"] = samples
    return out


# --- the AI model -------------------------------------------------------------------
def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def fit_logit(x: np.ndarray, y: np.ndarray, l2: float = 5.0, iters: int = 50) -> np.ndarray:
    """L2-regularised logistic regression by Newton steps; returns [bias, weights...]."""
    xb = np.c_[np.ones(len(x)), x]
    w = np.zeros(xb.shape[1])
    reg = l2 * np.r_[0.0, np.ones(xb.shape[1] - 1)]
    for _ in range(iters):
        p = sigmoid(xb @ w)
        g = xb.T @ (p - y) + reg * w
        h = (xb.T * (p * (1 - p))) @ xb + np.diag(reg)
        step = np.linalg.solve(h, g)
        w -= step
        if np.abs(step).max() < 1e-7:
            break
    return w


def auc(y: np.ndarray, p: np.ndarray) -> float:
    """Probability a random winner scored above a random loser (0.5 = no skill)."""
    pos, neg = p[y == 1], p[y == 0]
    if not len(pos) or not len(neg):
        return 0.5
    ranks = pd.Series(np.r_[pos, neg]).rank().to_numpy()
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


class Model:
    """Standardise -> logistic regression on features + strategy + side; plus the dissimilarity index."""

    def __init__(self, d: dict):
        self.d = d

    @staticmethod
    def design(xs: np.ndarray, strategies: list[str], dirs: np.ndarray, names: list[str]) -> np.ndarray:
        onehot = np.array([[s == n for n in names] for s in strategies], dtype=float)
        return np.c_[xs, onehot, (dirs > 0).astype(float)]

    @classmethod
    def train(cls, samples: list[dict], seed: int = 11) -> "Model":
        from bot.strategies import STRATEGIES
        names = list(STRATEGIES)
        samples = sorted(samples, key=lambda s: s["time"])
        x = np.array([s["x"] for s in samples], dtype=float)
        y = np.array([s["win"] for s in samples], dtype=float)
        strat = [s["strategy"] for s in samples]
        dirs = np.array([s["dir"] for s in samples])
        ok = np.isfinite(x).all(axis=1)
        x, y, dirs = x[ok], y[ok], dirs[ok]
        strat = [s for s, k in zip(strat, ok) if k]
        times = [s["time"] for s, k in zip(samples, ok) if k]

        def standardise(train):
            mu, sd = train.mean(0), train.std(0)
            return mu, np.where(sd > 0, sd, 1.0)

        # honest check first: train on the older 70%, score the newest 30%
        cut = int(len(x) * (1 - HOLDOUT))
        mu, sd = standardise(x[:cut])
        xtr = cls.design((x[:cut] - mu) / sd, strat[:cut], dirs[:cut], names)
        xte = cls.design((x[cut:] - mu) / sd, strat[cut:], dirs[cut:], names)
        w = fit_logit(xtr, y[:cut])
        p = sigmoid(np.c_[np.ones(len(xte)), xte] @ w)
        base = y[:cut].mean()
        brier, brier0 = float(np.mean((p - y[cut:]) ** 2)), float(np.mean((base - y[cut:]) ** 2))
        q = pd.qcut(p, 5, labels=False, duplicates="drop")
        calib = [{"predicted": round(float(p[q == k].mean()), 3), "actual": round(float(y[cut:][q == k].mean()), 3),
                  "trades": int((q == k).sum())} for k in sorted(set(q))]
        # strategy identity alone separates 60%-win reversion from 35%-win trend rules, so skill
        # is judged within each strategy: can it tell this strategy's good setups from its bad ones?
        st_te = np.array(strat[cut:])
        per = [(auc(y[cut:][st_te == n], p[st_te == n]), int((st_te == n).sum())) for n in set(strat[cut:])]
        per = [(a_, k) for a_, k in per if k >= 30]
        within = sum(a_ * k for a_, k in per) / sum(k for _, k in per) if per else 0.5
        holdout = {"trades": int(len(xte)), "auc": round(within, 3), "auc_pooled": round(auc(y[cut:], p), 3),
                   "brier_skill": round(1 - brier / brier0, 4) if brier0 else 0.0,
                   "from": times[cut], "to": times[-1], "calibration": calib}

        # then the live model on everything
        mu, sd = standardise(x)
        xs = (x - mu) / sd
        w = fit_logit(cls.design(xs, strat, dirs, names), y)
        # dissimilarity index: nearest reference example / mean distance between examples; the
        # threshold is what 99% of held-back training examples stay under
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(xs))
        n_ref = min(4000, int(len(xs) * 0.8))
        ref, probe = xs[perm[:n_ref]], xs[perm[n_ref:n_ref + 1000]]
        i, j = rng.integers(0, len(ref), 3000), rng.integers(0, len(ref), 3000)
        dbar = float(np.linalg.norm(ref[i] - ref[j], axis=1).mean())
        nn = np.array([np.linalg.norm(ref - v, axis=1).min() for v in probe])
        base_rates = {n: round(float(y[np.array(strat) == n].mean()), 4) for n in names if n in strat}
        importance = {f: round(float(w[1 + k]), 3) for k, f in enumerate(FEATURES)}
        return cls({"w": w.tolist(), "mu": mu.tolist(), "sd": sd.tolist(), "names": names,
                    "ref": ref.round(3).tolist(), "dbar": dbar,
                    "di_threshold": round(float(np.quantile(nn / dbar, 0.99)), 3),
                    "base_rate": round(float(y.mean()), 4), "base_rates": base_rates,
                    "trained_on": int(len(x)), "coins": len({s["coin"] for s in samples}),
                    "holdout": holdout, "importance": importance,
                    "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})

    def predict(self, x: np.ndarray, strategy: str, direction: int) -> dict:
        d = self.d
        if not np.isfinite(x).all():
            return {"p_win": None, "di": None, "unusual": False}
        xs = (x - np.array(d["mu"])) / np.array(d["sd"])
        row = self.design(xs[None, :], [strategy], np.array([direction]), d["names"])
        p = float(sigmoid(np.r_[1.0, row[0]] @ np.array(d["w"])))
        di = float(np.linalg.norm(np.array(d["ref"]) - xs, axis=1).min() / d["dbar"])
        # the three conditions pulling the estimate most, for the explanation
        contrib = sorted(((float(xs[k] * d["w"][1 + k]), f) for k, f in enumerate(FEATURES)),
                         key=lambda c: -abs(c[0]))[:3]
        return {"p_win": round(p, 4), "di": round(di, 3), "unusual": di > d["di_threshold"],
                "drivers": [{"feature": FEATURE_TEXT[f], "effect": "for" if v > 0 else "against",
                             "weight": round(abs(v), 3)} for v, f in contrib]}


# --- scoring ------------------------------------------------------------------------
def edge_certainty(r: list[float], n: int = 2000, seed: int = 3) -> float:
    """Share of bootstrap resamples of the out-of-sample trades whose average R is positive."""
    a = np.array(r, dtype=float)
    if len(a) < 2:
        return 0.5
    rng = np.random.default_rng(seed)
    return float((a[rng.integers(0, len(a), (n, len(a)))].mean(axis=1) > 0).mean())


def clip01(v: float) -> float:
    return float(min(1.0, max(0.0, v)))


def confidence(chosen: dict, ai: dict, model: dict) -> dict:
    edge = edge_certainty(chosen["r"])
    edge_s = clip01((edge - 0.5) / 0.5)
    folds = clip01(chosen["folds_positive"] / 4)
    skill = clip01((model["holdout"]["auc"] - 0.5) / 0.1)   # no weight at AUC 0.50, full weight at 0.60
    base = model["base_rates"].get(chosen["strategy"], model["base_rate"]) or model["base_rate"]
    ai_s = 0.5 if ai.get("p_win") is None else clip01(0.5 + (ai["p_win"] / base - 1) * 1.5)
    ai_part = skill * ai_s + (1 - skill) * 0.5
    score = 100 * (0.5 * edge_s + 0.2 * folds + 0.3 * ai_part)
    if ai.get("unusual"):
        score *= 0.75
    score = int(round(score))
    return {"score": score, "label": "High" if score >= 80 else "Medium" if score >= 60 else "Low",
            "parts": {"edge_certainty": round(edge, 3), "folds_positive": chosen["folds_positive"],
                      "ai_setup": round(ai_s, 3), "ai_weight": round(skill, 3),
                      "unusual_market": bool(ai.get("unusual"))}}


def accuracy(chosen: dict, model: dict) -> dict:
    base = model["base_rates"].get(chosen["strategy"], model["base_rate"])
    n = chosen["trades"]
    shrunk = (chosen["wins"] + base * SHRINK_TRADES) / (n + SHRINK_TRADES)
    return {"win_rate_pct": chosen["win_rate_pct"], "expected_win_rate_pct": round(100 * shrunk, 1),
            "trades": n, "profit_factor": chosen["profit_factor"], "avg_win_r": chosen["avg_win_r"],
            "avg_loss_r": chosen["avg_loss_r"], "folds_positive": chosen["folds_positive"],
            "return_pct": chosen["total_return_pct"], "max_drawdown_pct": chosen["max_drawdown_pct"]}


# --- scan driver ----------------------------------------------------------------------
def write(root: str, name: str, doc) -> None:
    p = path(root, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    os.replace(tmp, p)


def read(root: str, name: str) -> dict:
    try:
        with open(path(root, name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def scan(root: str = ".", coins: list[str] | None = None, workers: int | None = None,
         refresh: bool = True) -> dict:
    from bot.data import load_history, public_client
    from bot.lock import acquire
    os.makedirs(path(root, ""), exist_ok=True)
    lock = acquire(path(root, "scan"))  # noqa: F841 -- held until the process exits
    cfgs = configs()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def progress(step: str, done: int, total: int, **kw):
        write(root, "progress.json", {"state": "running", "step": step, "done": done, "total": total,
                                      "started_at": started, "pid": os.getpid(), **kw})

    try:
        progress("Picking the 25 largest coins", 0, 1)
        source = "given"
        if coins is None:
            coins, source = universe(public_client(cfgs["spot"].okx_hostname))
        jobs = [(c, m) for c in coins for m in MARKETS]
        failed = {}
        for k, (c, m) in enumerate(jobs):  # downloads one at a time: OKX rate-limits candles
            progress("Downloading price history", k, len(jobs), coin=c)
            try:
                load_history(cfgs[m], pair(c, m), TIMEFRAME, DAYS, refresh=refresh)
            except BaseException as e:
                failed[(c, m)] = str(e)[:200]
        results = []
        workers = workers or max(1, min(6, (os.cpu_count() or 2) - 1))
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for k, res in enumerate(pool.map(scan_one, jobs)):
                if (res["coin"], res["market"]) in failed and "error" in res:
                    res["error"] = "couldn't download price history"
                results.append(res)
                progress("Testing strategies on every coin", k + 1, len(jobs), coin=res["coin"])

        progress("Training the AI model", 0, len(MARKETS))
        models = {}
        for k, m in enumerate(MARKETS):
            samples = [s for r in results if r["market"] == m for s in r.get("samples", [])]
            if len(samples) < 500:
                raise RuntimeError(f"only {len(samples)} {m} trades to learn from")
            models[m] = Model.train(samples).d
            progress("Training the AI model", k + 1, len(MARKETS))
        for m in MARKETS:
            write(root, f"model_{m}.json", models[m])
        doc = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "started_at": started, "timeframe": TIMEFRAME, "days": DAYS, "coins": coins,
               "universe_source": source,
               "results": [{k: v for k, v in r.items() if k != "samples"} for r in results]}
        write(root, "scan.json", doc)
        write(root, "progress.json", {"state": "done", "started_at": started, "finished_at": doc["generated_at"],
                                      "done": len(jobs), "total": len(jobs)})
        return doc
    except BaseException as e:
        write(root, "progress.json", {"state": "error", "started_at": started, "error": repr(e)[:300],
                                      "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        raise


# --- live signals ---------------------------------------------------------------------
EXIT_WHY = {"signal": "the strategy's exit condition was met on the latest 4-hour candle",
            "stop": "the price reached the stop-loss", "tp": "the price reached the take-profit",
            "liquidated": "the position was liquidated"}


def side_word(market: str, d: int) -> str:
    """LONG / SHORT on futures; spot can only buy."""
    return "BUY" if market == "spot" else ("LONG" if d > 0 else "SHORT")


def pct(level: float, base: float) -> str:
    v = (level / base - 1) * 100
    return f"{'+' if v > 0 else '-' if v < 0 else ''}{abs(v):.1f}%"


def plain(text):
    """Strategy wording for everyone: candles, not bars."""
    if not isinstance(text, str):
        return text
    import re
    text = re.sub(r"\b(\d+)-bar\b", r"\1-candle", text)
    text = re.sub(r"\bbars\b", "candles", text)
    text = re.sub(r"\bbar\b", "candle", text)
    text = re.sub(r"\bStop ([\d.]+)× ATR\b", r"Stop-loss \1× the average candle size away", text)
    text = re.sub(r"\btarget ([\d.]+)R\b", r"take-profit at \1× the risk", text)
    text = re.sub(r"\bno target\b", "no fixed take-profit", text)
    return re.sub(r"\bEMA (\d+)\b", r"the \1-candle average", text)


def _fmt(v):
    from bot.explain import fmt
    return fmt(v)


def signal_for(res: dict, model: Model, df: pd.DataFrame, cfg, filt: dict | None = None) -> dict:
    """One coin's signal on its latest closed candle."""
    from bot.engine import simulate, simulate_ls
    from bot.explain import analyse, rule_text
    from bot.futures import trail_params
    from bot.strategies import StrategySpec, invert, signals, signals_ls

    market, coin, chosen = res["market"], res["coin"], res["chosen"]
    spec = StrategySpec.from_dict(chosen["spec"])
    fut = market == "futures"
    a = analyse(df, spec, TIMEFRAME, bars=160)
    sig = signals_ls(df, spec) if fut else signals(df, spec)
    held: dict = {}
    trades, _, _ = (simulate_ls if fut else simulate)(sig, spec, cfg, open_out=held)
    last_t = df["time"].iloc[-1]
    close, atr = a["close"], a["atr"]
    fx = {1: features(df), -1: features(invert(df))}
    times = pd.Index(df["time"])
    bar = pd.Timedelta(minutes=240)
    out = {"id": f"{market}:{coin}", "coin": coin, "symbol": res["symbol"], "market": market,
           "timeframe": TIMEFRAME, "strategy": spec.name, "label": spec.label(), "rule": rule_text(spec),
           "price": close, "bar_time": a["bar_time"], "next_decision": a["next_decision"],
           "headline": a["headline"], "entry": None, "stop": None, "target": None, "trail": None,
           "direction": None, "signal_time": None, "spec": spec.to_dict(), "entry_bar": None}
    if fut and trail_params(spec, cfg)[0] > 0:
        start_r, trail_atr = trail_params(spec, cfg)
        out["trail"] = (f"Once the trade is up {start_r:g} times what you risked, SiGen moves the stop-loss "
                        f"up behind the price to lock in profit, and shows the new level here.")

    def levels(d: int, entry: float, dist: float):
        out.update(direction="long" if d > 0 else "short", entry=entry, stop=entry - d * dist,
                   target=entry + d * spec.tp_r * dist if spec.tp_r else None)

    if held:
        d = held["dir"]
        i = times.get_indexer([pd.Timestamp(held["time"])])[0]
        levels(d, held["entry"], held["init_dist"])
        out["stop"] = held["stop"]
        out["initial_stop"] = held["entry"] - d * held["init_dist"]
        out["signal_time"] = (pd.Timestamp(held["time"]) + bar).isoformat()  # filled at that candle's close
        out["entry_bar"] = pd.Timestamp(held["time"]).isoformat()
        out["r_now"] = round(d * (close - held["entry"]) / held["init_dist"], 2)
        new = pd.Timestamp(held["time"]) == last_t
        out["state"] = "entry" if new else "holding"
        ai = model.predict(fx[d][i], spec.name, d)
    elif trades and trades[-1].exit_time == last_t and trades[-1].reason != "end":
        t = trades[-1]
        d = 1 if t.side == "long" else -1
        out.update(state="exit", direction=t.side, entry=t.entry, exit_price=t.exit, exit_reason=t.reason,
                   result_r=round(t.R, 2), signal_time=(t.entry_time + bar).isoformat(),
                   entry_bar=t.entry_time.isoformat())
        i = times.get_indexer([t.entry_time])[0]
        ai = model.predict(fx[d][i], spec.name, d)
    else:
        options = []
        for key, d in (("long", 1), ("short", -1)):
            s = a["sides"].get(key)
            if s and s["trigger_level"]:
                options.append((abs(s["trigger_level"] / close - 1), d, s))
        if options:
            _, d, s = min(options, key=lambda o: o[0])
            levels(d, s["trigger_level"], spec.stop_atr * atr)
            out["state"] = "armed"
        else:
            d = 1
            out["state"] = "watching"
        ai = model.predict(fx[d][-1], spec.name, d)
    side = a["sides"].get(out["direction"] or "long") or {}
    out["checks"] = side.get("checks", [])
    out["checks_at"] = "now"
    if out["state"] in ("holding", "exit"):  # why it entered: the checks on the entry candle
        then = analyse(df.iloc[:i + 1], spec, TIMEFRAME, bars=5)["sides"].get(out["direction"]) or {}
        if then.get("checks"):
            out["checks"], out["checks_at"] = then["checks"], "entry"
    out["exit_rule"] = side.get("exit")
    out["trigger"] = {k: v["trigger"] for k, v in a["sides"].items()}
    out["ai"] = {**ai, "base_rate": model.d["base_rates"].get(spec.name, model.d["base_rate"]),
                 "holdout_auc": model.d["holdout"]["auc"]}
    out["confidence"] = confidence(chosen, ai, model.d)
    from bot.sigen_regime import at as regime_at
    out["regime"] = regime_at(df, i if out["state"] in ("entry", "holding", "exit") else len(df) - 1, spec.name,
                              filt or {"mode": "none", "rule": None})
    out["accuracy"] = accuracy(chosen, model.d)
    out["accuracy"]["history_days"] = int(res.get("bars", 0) // 6)

    # validity: an entry is good for one candle, and only while price hasn't run past the chase limit
    out["valid_from"], out["valid_until"] = a["bar_close_time"], a["next_decision"]
    if out["state"] in ("entry", "holding", "armed") and out["entry"] and out["stop"] is not None:
        dn_ = 1 if out["direction"] != "short" else -1
        risk = abs(out["entry"] - (out.get("initial_stop") or out["stop"]))
        out["chase_limit"] = out["entry"] + dn_ * CHASE_R * risk
        if out["state"] == "holding":
            out["late_entry_ok"] = bool(dn_ * (close - out["chase_limit"]) <= 0 and dn_ * (close - out["stop"]) > 0)

    # the instruction, in plain words: same shape for every signal
    st, dn = out["state"], (1 if out["direction"] != "short" else -1)
    side = side_word(market, dn)
    for k in ("exit_rule", "headline", "rule"):
        out[k] = plain(out.get(k))
    out["trigger"] = {k: plain(v) for k, v in out["trigger"].items()}
    out["checks"] = [{**c, "label": plain(c["label"]), "detail": plain(c["detail"])} for c in out["checks"]]

    def stop_part(entry):
        return f"Set the stop-loss at {_fmt(out['stop'])} ({pct(out['stop'], entry)} from entry)"

    def target_part(entry):
        if out["target"]:
            return f" and the take-profit at {_fmt(out['target'])} ({pct(out['target'], entry)})."
        return ". There is no fixed take-profit: keep the trade until SiGen says to close it."

    if st == "entry":
        out["action"] = "Buy now" if market == "spot" else f"Open a {side} now"
        lead = f"Buy {coin} now" if market == "spot" else f"Open a {side} on {coin} now"
        out["instruction"] = f"{lead}, at about {_fmt(out['entry'])}. {stop_part(out['entry'])}{target_part(out['entry'])}"
    elif st == "holding":
        out["action"] = "Keep holding" if market == "spot" else f"Keep the {side} open"
        what = f"This {coin} buy" if market == "spot" else f"This {side} on {coin}"
        out["instruction"] = (f"{what} is already open, entered at {_fmt(out['entry'])}. Keep the stop-loss at "
                              f"{_fmt(out['stop'])}. SiGen will tell you when to close.")
    elif st == "exit":
        out["action"] = "Sell now" if market == "spot" else f"Close the {side} now"
        what = f"Sell your {coin}" if market == "spot" else f"Close your {side} on {coin}"
        out["instruction"] = f"{what} now: {EXIT_WHY.get(out['exit_reason'], EXIT_WHY['signal'])}."
    elif st == "armed":
        word = "above" if out["entry"] > close else "below"  # reversion rules wait for a move against the side
        out["action"] = f"Wait: {'buy' if market == 'spot' else side} if it closes {word} {_fmt(out['entry'])}"
        lead = f"buy {coin}" if market == "spot" else f"open a {side} on {coin}"
        out["instruction"] = (f"No trade yet. Only {lead} if a 4-hour candle closes {word} {_fmt(out['entry'])} "
                              f"({pct(out['entry'], close)} from now). Then s{stop_part(out['entry'])[1:]}"
                              f"{target_part(out['entry'])}")
    else:
        out["action"] = "No trade yet"
        out["instruction"] = (f"No trade yet: there is no setup on {coin} right now. SiGen checks again at every "
                              f"4-hour close.")
    rg = out["regime"]
    if rg["held_back"] and st in ("entry", "armed"):
        out["state"], out["action"] = "held", "Skip: too choppy"
        out["instruction"] = (f"Skip this one. {coin}'s price has been going back and forth without a clear "
                              f"direction, and signals like this one tend to lose in that kind of market.")
    return out


ORDER = {"entry": 0, "exit": 1, "holding": 2, "armed": 3, "held": 4, "watching": 5}


def live(market: str, root: str = ".", fetch=None, workers: int = 4) -> dict:
    """Signals for every tested coin in one market, on the latest closed 4h candle."""
    from bot.strategies import StrategySpec, warmup_bars
    doc = read(root, "scan.json")
    mdoc = read(root, f"model_{market}.json")
    if not doc or not mdoc:
        return {"market": market, "signals": [], "untested": [], "scanned": False}
    model = Model(mdoc)
    from bot.sigen_regime import active
    filt = active(root)
    cfg = configs()[market]
    if fetch is None:
        from bot.data import fetch_closed, public_client
        client = public_client(cfg.okx_hostname)
        fetch = lambda s, tf, n: fetch_closed(client, s, tf, n)  # noqa: E731
    rows = [r for r in doc["results"] if r["market"] == market]

    def one(r):
        try:
            spec = StrategySpec.from_dict(r["chosen"]["spec"])
            df = fetch(r["symbol"], TIMEFRAME, warmup_bars(spec) + 300)
            return signal_for(r, model, df, cfg, filt)
        except Exception as e:
            return {"coin": r["coin"], "error": repr(e)[:200]}

    tested = [r for r in rows if r.get("chosen")]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        sigs = list(pool.map(one, tested))
    good = [s for s in sigs if "error" not in s]
    good.sort(key=lambda s: (ORDER[s["state"]], -s["confidence"]["score"]))
    untested = []
    for r in rows:
        if r.get("chosen"):
            continue
        best = max((x for x in r.get("rows", []) if x["trades"] >= 30), key=lambda x: x["profit_factor"],
                   default=None)
        untested.append({"coin": r["coin"], "reason": r.get("error") or "no strategy passed testing",
                         "closest": best and {"strategy": best["strategy"], "profit_factor": best["profit_factor"],
                                              "trades": best["trades"], "folds_positive": best["folds_positive"]}})
    errors = [s for s in sigs if "error" in s]
    hold = mdoc["holdout"]
    return {"market": market, "scanned": True, "generated_at": doc["generated_at"], "coins": doc["coins"],
            "regime_filter": filt,
            "universe_source": doc.get("universe_source"), "signals": good, "untested": untested, "errors": errors,
            "model": {k: mdoc[k] for k in ("trained_on", "coins", "base_rate", "di_threshold", "trained_at",
                                           "importance")} | {"holdout": hold}}


# --- terms ----------------------------------------------------------------------------
TERMS = {
    "version": "2026-10-23",
    "title": "SiGen terms and risk declaration",
    "sections": [
        ["What SiGen is",
         "SiGen is software from TradePilot LLC that generates trading signals automatically, using rule-based "
         "strategies and a machine-learning (AI) model applied to public market data. Signals are general "
         "information produced by software. They are not financial, investment, tax or legal advice, not a "
         "recommendation to buy or sell any asset, and not tailored to your circumstances."],
        ["AI can be wrong",
         "Signals come from automated models that can and do make mistakes. Accuracy and confidence figures "
         "describe how similar signals performed in historical testing; past results do not guarantee future "
         "results. Prices can move against any signal, quickly and by large amounts. Crypto assets are highly "
         "volatile, and leveraged futures can lose your whole margin."],
        ["Your decisions",
         "You alone decide whether to act on a signal, how much to trade and whether to use leverage. You are "
         "solely responsible for your trades and their results. Only trade money you can afford to lose, and "
         "consider independent professional advice."],
        ["No responsibility for losses",
         "To the fullest extent permitted by law, TradePilot LLC and its owners, employees and affiliates accept "
         "no responsibility or liability for any loss or damage, including trading losses, lost profits or missed "
         "opportunities, arising from your use of or reliance on SiGen signals, including signals that are wrong, "
         "late, incomplete or unavailable. SiGen is provided \"as is\", without warranties of any kind."],
        ["Data and availability",
         "Signals depend on third-party market data and exchanges, which can be delayed, wrong or unavailable. "
         "SiGen does not place orders for you."],
        ["Changes",
         "TradePilot LLC may update these terms. When they change, you will be asked to accept them again before "
         "seeing signals."],
    ],
    "statements": [
        ["ai", "I understand SiGen signals are generated by AI and automated rules, and can be wrong."],
        ["advice", "I understand signals are not financial advice and that I am solely responsible for any trade I make."],
        ["liability", "I accept that TradePilot LLC takes no responsibility for any loss resulting from SiGen signals."],
    ],
}


def terms_hash() -> str:
    return hashlib.sha256(json.dumps(TERMS, sort_keys=True).encode()).hexdigest()


def acceptance(root: str = ".") -> dict:
    a = read(root, "terms_acceptance.json")
    ok = bool(a) and a.get("version") == TERMS["version"] and a.get("sha256") == terms_hash()
    return {"accepted": ok, "version": TERMS["version"], "accepted_at": a.get("accepted_at") if ok else None,
            "name": a.get("name") if ok else None}


def accept(name: str, statements: list[str], version: str, root: str = ".") -> dict:
    name = " ".join(str(name).split())[:120]
    if version != TERMS["version"]:
        raise ValueError("these terms have changed; reload the page and read them again")
    if len(name) < 2:
        raise ValueError("type your full name to sign")
    missing = [k for k, _ in TERMS["statements"] if k not in set(statements)]
    if missing:
        raise ValueError("every statement must be ticked")
    rec = {"version": TERMS["version"], "sha256": terms_hash(), "name": name, "statements": [k for k, _ in TERMS["statements"]],
           "accepted_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    write(root, "terms_acceptance.json", rec)
    return acceptance(root)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["scan", "signals", "record", "backfill", "report"])
    p.add_argument("--days", type=int, default=30, help="backfill: how far back")
    p.add_argument("--coins", help="comma-separated, instead of the top 25 (e.g. BTC,ETH)")
    p.add_argument("--offline", action="store_true", help="use cached candles only")
    p.add_argument("--workers", type=int)
    args = p.parse_args()
    if args.command == "scan":
        t = time.time()
        doc = scan(coins=args.coins.split(",") if args.coins else None, workers=args.workers,
                   refresh=not args.offline)
        found = sum(bool(r.get("chosen")) for r in doc["results"])
        print(f"SiGen scan: {len(doc['coins'])} coins ({doc['universe_source']}), {found} coin/market pairs "
              f"passed, {time.time() - t:.0f}s")
        for m in MARKETS:
            h = read(".", f"model_{m}.json")["holdout"]
            print(f"  {m} AI holdout: AUC {h['auc']}, Brier skill {h['brier_skill']}, {h['trades']} trades")
    elif args.command in ("record", "backfill", "report"):
        from bot import sigen_journal as j
        if args.command == "record":
            for m in MARKETS:
                res = live(m)
                print(f"{m}: logged {len(j.record(res['signals'], scan_at=res.get('generated_at')))} new signals")
        elif args.command == "backfill":
            print(f"replayed {j.backfill(days=args.days)} signals from the last {args.days} days")
        else:
            rep = j.report()
            for src, b in rep["summary"].items():
                print(f"{src}: {b}")
            for r in rep["signals"][:40]:
                o = r["outcome"]
                print(f"  {r['entry_bar'][:16]} {r['market']:7} {r['coin']:6} {r['direction']:5} {o['verdict']:11} "
                      f"{o.get('result_r', o.get('r_now'))}R  {o.get('exit_reason', '')}  [{r['source']}]")
    else:
        for m in MARKETS:
            res = live(m)
            print(f"\n{m}: {len(res['signals'])} signals")
            for s in res["signals"]:
                print(f"  {s['coin']:6} {s['state']:8} {s['confidence']['score']:3d}  {s['instruction']}")


if __name__ == "__main__":
    sys.exit(main())
