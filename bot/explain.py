"""What a strategy sees on the latest closed bar, in words and numbers.

The dashboard uses this to show, for every strategy, the conditions it checks,
which of them hold right now, how far price is from the next trigger, and the
indicator lines to draw on the chart. It reads candles only; it never decides
anything for the bots. Short-side checks run on the mirrored chart (the same
trick signals_ls uses), and their price levels are mapped back to real prices.
"""
from __future__ import annotations

import pandas as pd

from bot import indicators as ind
from bot.strategies import StrategySpec, invert, signals_ls

TF_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120, "4h": 240, "1d": 1440}


def fmt(v: float) -> str:
    a = abs(v)
    return f"{v:,.2f}" if a >= 100 else f"{v:.4f}" if a >= 1 else f"{v:.5f}"


class Side:
    """Wording and price mapping for one direction."""

    def __init__(self, df: pd.DataFrame, direction: int):
        self.dir = direction
        self.d = df if direction > 0 else invert(df)   # frame the rule is evaluated on
        self.real_close = float(df["close"].iloc[-1])
        self.above = "above" if direction > 0 else "below"
        self.below = "below" if direction > 0 else "above"
        self.rises = "rises" if direction > 0 else "falls"

    def px(self, v: float) -> float:
        return float(v) if self.dir > 0 else 1.0 / float(v)

    def dist(self, level_real: float) -> str:
        return f"{(level_real / self.real_close - 1) * 100:+.2f}%"

    def level_check(self, label: str, name: str, level_d: float, cmp: str = "above") -> dict:
        """close vs a level on the rule's frame, worded in real prices."""
        close_d = float(self.d["close"].iloc[-1])
        ok = close_d > level_d if cmp == "above" else close_d < level_d
        lvl = self.px(level_d)
        word = self.above if cmp == "above" else self.below
        state = "is" if ok else "is not"
        return {"label": label, "ok": bool(ok), "level": lvl,
                "detail": f"Close {fmt(self.real_close)} {state} {word} {name} {fmt(lvl)} ({self.dist(lvl)})"}


def _last(s: pd.Series, i: int = -1) -> float:
    return float(s.iloc[i])


# --- per-strategy explainers --------------------------------------------------
# Each returns (checks, trigger, exit_text) for one side, on that side's frame.

def _trend_check(sd: Side, trend: int) -> list[dict]:
    if not trend:
        return []
    return [sd.level_check("Trend filter", f"EMA {trend}", _last(ind.ema(sd.d["close"], trend)))]


def _x_supertrend(sd: Side, p: dict):
    up, line = ind.supertrend(sd.d, 10, p["mult"])
    now, prev, lvl = bool(up.iloc[-1]), bool(up.iloc[-2]), sd.px(_last(line))
    flip = now and not prev
    checks = [{"label": "Fresh Supertrend flip", "ok": flip, **({} if now else {"level": lvl}),
               "detail": ("Supertrend flipped on this bar" if flip else
                          f"Supertrend already {'up' if sd.dir > 0 else 'down'}; entries only on a fresh flip"
                          if now else f"Supertrend is against this side; line at {fmt(lvl)} ({sd.dist(lvl)})")}]
    checks += _trend_check(sd, p.get("trend", 0))
    if not now:
        trigger = f"a close {sd.above} {fmt(lvl)} ({sd.dist(lvl)}) flips Supertrend"
    elif not flip:
        trigger = f"Supertrend to turn {'down' if sd.dir > 0 else 'up'} and flip back"
    else:
        trigger = "conditions met on this bar"
    exit_text = f"a close {sd.below} the Supertrend line {fmt(lvl)} ({sd.dist(lvl)})"
    return checks, trigger, exit_text


def _x_donchian(sd: Side, p: dict):
    hi = sd.d["high"].rolling(p["entry_n"]).max().shift(1)
    lo = sd.d["low"].rolling(p["exit_n"]).min().shift(1)
    checks = [sd.level_check("Breakout", f"the prior {p['entry_n']}-bar {'high' if sd.dir > 0 else 'low'}",
                             _last(hi))]
    checks += _trend_check(sd, p.get("trend", 0))
    lvl = sd.px(_last(hi))
    trigger = f"a close {sd.above} {fmt(lvl)} ({sd.dist(lvl)})"
    ex = sd.px(_last(lo))
    return checks, trigger, f"a close {sd.below} the {p['exit_n']}-bar channel {fmt(ex)} ({sd.dist(ex)})"


def _x_breakout_htf(sd: Side, p: dict):
    hi = sd.d["high"].rolling(p["entry_n"]).max().shift(1)
    lo = sd.d["low"].rolling(20).min().shift(1)
    adx = _last(ind.adx(sd.d))
    checks = [sd.level_check("Breakout", f"the prior {p['entry_n']}-bar extreme", _last(hi)),
              *_trend_check(sd, p["trend"]),
              {"label": "Trend strength", "ok": adx > 20, "detail": f"ADX {adx:.1f} (needs > 20)"}]
    lvl = sd.px(_last(hi))
    ex = sd.px(_last(lo))
    return checks, f"a close {sd.above} {fmt(lvl)} ({sd.dist(lvl)})", \
        f"a close {sd.below} the 20-bar channel {fmt(ex)} ({sd.dist(ex)})"


def _rsi_cross(sd: Side, level: float) -> tuple[dict, str]:
    r = ind.rsi(sd.d["close"], 14)
    now, prev = _last(r), _last(r, -2)
    crossed = prev <= level < now
    name = "RSI" if sd.dir > 0 else "RSI of the mirrored chart"
    if crossed:
        detail, trig = f"{name} crossed up through {level:g} ({prev:.1f} → {now:.1f})", "conditions met on this bar"
    elif now <= level:
        detail = f"{name} {now:.1f} is under {level:g}: a close back above {level:g} triggers"
        trig = f"{name} recovering above {level:g} (now {now:.1f})"
    else:
        detail = f"{name} {now:.1f}; needs a dip under {level:g} and a recovery"
        trig = f"a pullback: {name} under {level:g}, then back above it (now {now:.1f})"
    return {"label": "Pullback (RSI)", "ok": crossed, "detail": detail}, trig


def _x_trend_pullback(sd: Side, p: dict):
    rc, trig = _rsi_cross(sd, p["rsi_entry"])
    checks = [*_trend_check(sd, p["trend"]), rc]
    t = sd.px(_last(ind.ema(sd.d["close"], p["trend"])))
    return checks, trig, f"RSI above {p['rsi_exit']} or a close {sd.below} EMA {p['trend']} {fmt(t)}"


def _x_pullback_htf(sd: Side, p: dict):
    rc, trig = _rsi_cross(sd, p["rsi_entry"])
    checks = [*_trend_check(sd, p["trend"]),
              sd.level_check("Mid-term trend", "EMA 50", _last(ind.ema(sd.d["close"], 50))), rc]
    t = sd.px(_last(ind.ema(sd.d["close"], p["trend"])))
    return checks, trig, f"RSI above 75 or a close {sd.below} EMA {p['trend']} {fmt(t)}"


def _x_bollinger(sd: Side, p: dict):
    lower, mid, _ = ind.bollinger(sd.d["close"], 20, p["k"])
    c, pc = _last(sd.d["close"]), _last(sd.d["close"], -2)
    lo_now, lo_prev = _last(lower), _last(lower, -2)
    back_in = pc < lo_prev and c > lo_now
    band = "lower" if sd.dir > 0 else "upper"
    lvl = sd.px(lo_now)
    if back_in:
        detail = f"Closed back inside the {band} band {fmt(lvl)} after a close outside it"
    elif c < lo_now:
        detail = f"Close is outside the {band} band {fmt(lvl)}: a close back inside triggers"
    else:
        detail = f"Close is inside the bands; needs a close beyond the {band} band {fmt(lvl)} ({sd.dist(lvl)}) first"
    checks = [{"label": "Band re-entry", "ok": back_in, "level": lvl, "detail": detail},
              *_trend_check(sd, p.get("trend", 0))]
    m = sd.px(_last(mid))
    return checks, ("conditions met on this bar" if back_in else
                    f"a close beyond {fmt(lvl)} ({sd.dist(lvl)}), then back inside"), \
        f"a close at the middle band {fmt(m)} ({sd.dist(m)})"


def _cross_check(sd: Side, fast: int, slow: int) -> tuple[dict, str, str]:
    f, s = ind.ema(sd.d["close"], fast), ind.ema(sd.d["close"], slow)
    crossed = _last(f, -2) <= _last(s, -2) and _last(f) > _last(s)
    gap = (_last(f) / _last(s) - 1) * 100
    if crossed:
        detail = f"EMA {fast} crossed {sd.above} EMA {slow} on this bar"
    elif _last(f) > _last(s):
        detail = f"EMA {fast} already {sd.above} EMA {slow}; entries only on the cross"
    else:
        detail = f"EMA {fast} is {abs(gap):.2f}% {sd.below} EMA {slow}"
    trig = "conditions met on this bar" if crossed else f"EMA {fast} crossing {sd.above} EMA {slow}"
    return {"label": "EMA cross", "ok": crossed, "detail": detail}, trig, \
        f"EMA {fast} crossing back {sd.below} EMA {slow}"


def _x_ema_cross(sd: Side, p: dict):
    c, trig, ex = _cross_check(sd, p["fast"], p["slow"])
    return [c], trig, ex


def _x_ema_cross_adx(sd: Side, p: dict):
    c, trig, ex = _cross_check(sd, p["fast"], p["slow"])
    adx = _last(ind.adx(sd.d))
    return [c, {"label": "Trend strength", "ok": adx > p["adx_min"],
                "detail": f"ADX {adx:.1f} (needs > {p['adx_min']})"}], trig, ex


def _x_chandelier(sd: Side, p: dict):
    t = ind.ema(sd.d["close"], p["trend"])
    c, pc = _last(sd.d["close"]), _last(sd.d["close"], -2)
    crossed = pc <= _last(t, -2) and c > _last(t)
    adx = _last(ind.adx(sd.d))
    lvl = sd.px(_last(t))
    if crossed:
        detail = f"Close reclaimed EMA {p['trend']} {fmt(lvl)} on this bar"
    elif c > _last(t):
        detail = f"Close already {sd.above} EMA {p['trend']} {fmt(lvl)}; entries only on the reclaim"
    else:
        detail = f"Close is {sd.below} EMA {p['trend']} {fmt(lvl)} ({sd.dist(lvl)})"
    ch = sd.px(_last(ind.chandelier_long(sd.d, 22, p["mult"])))
    checks = [{"label": "Trend reclaim", "ok": crossed, **({"level": lvl} if c <= _last(t) else {}), "detail": detail},
              {"label": "Trend strength", "ok": adx > 20, "detail": f"ADX {adx:.1f} (needs > 20)"}]
    trig = "conditions met on this bar" if crossed else (
        f"a close {sd.above} EMA {p['trend']} {fmt(lvl)} ({sd.dist(lvl)})" if c <= _last(t)
        else f"price to cross back {sd.below} EMA {p['trend']} and reclaim it")
    return checks, trig, f"a close {sd.below} the chandelier stop {fmt(ch)} ({sd.dist(ch)})"


EXPLAINERS = {
    "supertrend": _x_supertrend, "donchian_breakout": _x_donchian, "breakout_htf": _x_breakout_htf,
    "trend_pullback": _x_trend_pullback, "pullback_htf": _x_pullback_htf,
    "bollinger_reversion": _x_bollinger, "ema_cross": _x_ema_cross, "ema_cross_adx": _x_ema_cross_adx,
    "chandelier_trend": _x_chandelier,
}

RULES = {
    "supertrend": "Enter when Supertrend (10, {mult}) flips in the trade's direction{trend}. Exit when it flips back.",
    "donchian_breakout": "Enter on a close beyond the prior {entry_n}-bar high (low for shorts){trend}. "
                         "Exit on a close beyond the prior {exit_n}-bar low (high).",
    "breakout_htf": "Enter on a close beyond the prior {entry_n}-bar extreme with EMA {trend} and ADX > 20 agreeing. "
                    "Exit on a 20-bar channel break.",
    "trend_pullback": "In a trend (EMA {trend}), enter when RSI dips under {rsi_entry} and closes back above it. "
                      "Exit when RSI passes {rsi_exit} or the trend breaks.",
    "pullback_htf": "Above EMA {trend} and EMA 50, enter when RSI recovers through {rsi_entry}. "
                    "Exit on RSI > 75 or a close through EMA {trend}.",
    "bollinger_reversion": "Enter when price closes outside the {k}σ Bollinger band and then back inside it{trend}. "
                           "Exit at the middle band.",
    "ema_cross": "Enter when EMA {fast} crosses EMA {slow}. Exit on the cross back.",
    "ema_cross_adx": "Enter when EMA {fast} crosses EMA {slow} with ADX > {adx_min}. Exit on the cross back.",
    "chandelier_trend": "Enter when price reclaims EMA {trend} with ADX > 20. Exit on the chandelier stop (22, {mult} ATR).",
}


def rule_text(spec: StrategySpec) -> str:
    p = dict(spec.params)
    trend = p.get("trend", 0)
    p["trend"] = trend
    text = RULES[spec.name]
    if "{trend}" in text and spec.name in ("supertrend", "donchian_breakout", "bollinger_reversion"):
        text = text.replace("{trend}", f", with price on the right side of EMA {trend}" if trend else "")
    risk = f" Stop {spec.stop_atr:g}× ATR" + (f", target {spec.tp_r:g}R." if spec.tp_r else ", no fixed target.")
    return text.format(**p) + risk + (" Trades long and short." if spec.shorts else " Long only.")


def overlays(df: pd.DataFrame, spec: StrategySpec) -> tuple[list[dict], list[dict]]:
    """Indicator lines on the price chart, and lower panes (RSI / ADX)."""
    p, n = spec.params, spec.name
    lines, panes = [], []

    def add(name, s, role):
        lines.append({"name": name, "role": role, "values": s})

    if p.get("trend"):
        add(f"EMA {p['trend']}", ind.ema(df["close"], p["trend"]), "trend")
    if n == "supertrend":
        up, line = ind.supertrend(df, 10, p["mult"])
        add("Supertrend", line.where(up), "bull")
        add("Supertrend ", line.where(~up), "bear")
    elif n in ("donchian_breakout", "breakout_htf"):
        en = p["entry_n"]
        add(f"{en}-bar high", df["high"].rolling(en).max().shift(1), "band")
        add(f"{en}-bar low", df["low"].rolling(en).min().shift(1), "band")
    elif n == "bollinger_reversion":
        lo, mid, hi = ind.bollinger(df["close"], 20, p["k"])
        add("Upper band", hi, "band"), add("Middle band", mid, "mid"), add("Lower band", lo, "band")
    elif n in ("ema_cross", "ema_cross_adx"):
        add(f"EMA {p['fast']}", ind.ema(df["close"], p["fast"]), "fast")
        add(f"EMA {p['slow']}", ind.ema(df["close"], p["slow"]), "slow")
    elif n == "chandelier_trend":
        add("Chandelier stop", ind.chandelier_long(df, 22, p["mult"]), "band")
    elif n == "pullback_htf":
        add("EMA 50", ind.ema(df["close"], 50), "fast")
    if n in ("trend_pullback", "pullback_htf"):
        levels = [p["rsi_entry"], p.get("rsi_exit", 75)]
        panes.append({"name": "RSI 14", "levels": levels, "values": ind.rsi(df["close"], 14)})
    if n in ("ema_cross_adx", "breakout_htf", "chandelier_trend"):
        panes.append({"name": "ADX 14", "levels": [p.get("adx_min", 20)], "values": ind.adx(df)})
    return lines, panes


def _series(times: pd.Series, s: pd.Series, bars: int) -> list[list]:
    out = []
    for t, v in zip(times.iloc[-bars:], s.iloc[-bars:]):
        if pd.notna(v):
            out.append([int(t.timestamp()), round(float(v), 8)])
    return out


def analyse(df: pd.DataFrame, spec: StrategySpec, timeframe: str, position: dict | None = None,
            bars: int = 300, trail_start_r: float = 2.0) -> dict:
    """The latest closed bar through the strategy's eyes. df: closed candles only."""
    sig = signals_ls(df, spec)
    last = sig.iloc[-1]
    t = last["time"]
    tf = pd.Timedelta(minutes=TF_MINUTES.get(timeframe, 60))
    sides = {}
    for direction, key in ((1, "long"), (-1, "short")):
        if direction < 0 and not spec.shorts:
            continue
        sd = Side(df, direction)
        checks, trigger, exit_text = EXPLAINERS[spec.name](sd, spec.params)
        fired = bool(last["entry"] if direction > 0 else last["short_entry"])
        blocked = [c["label"].lower() for c in checks if not c["ok"]]
        # unmet price conditions all clear at once beyond the furthest of them
        prices = [(c["level"], c["label"].lower()) for c in checks if not c["ok"] and "level" in c]
        level = None
        if prices:
            level, _ = (max if direction > 0 else min)(prices)
            if len(prices) > 1:
                trigger = (f"a close {sd.above} {fmt(level)} ({sd.dist(level)}), "
                           f"which clears the {' and the '.join(n for _, n in prices)}")
        if trigger.startswith("conditions met") and not fired:
            trigger = "the trigger fired, but the " + " and ".join(blocked or ["warm-up"]) + " blocked it"
        sides[key] = {"checks": checks, "ready": fired, "trigger": trigger, "exit": exit_text, "trigger_level": level,
                      "met": sum(c["ok"] for c in checks), "total": len(checks)}

    close = float(last["close"])
    atr = float(last["atr"])
    if position:
        d = position["dir"]
        side = "long" if d > 0 else "short"
        init = position.get("init_dist") or abs(position["entry"] - position["stop"])
        trail_at = position["entry"] + d * trail_start_r * init
        headline = (f"Holding a {side} from {fmt(position['entry'])}. Stop {fmt(position['stop'])} "
                    f"({(position['stop'] / close - 1) * 100:+.2f}% from the last close). "
                    f"The stop starts trailing at {fmt(trail_at)}. "
                    f"It exits on {sides[side]['exit'] if side in sides else 'the stop'}.")
        mood = "holding"
    elif any(s["ready"] for s in sides.values()):
        which = [k for k, s in sides.items() if s["ready"]][0]
        headline = f"Entry signal: every {which} condition held on the {t:%H:%M} bar."
        mood = "signal"
    else:
        parts = [f"{k.capitalize()}: {s['trigger']}" if s["trigger"].startswith("the trigger")
                 else f"{k.capitalize()} needs {s['trigger']}" for k, s in sides.items()]
        headline = ". ".join(parts) + "."
        mood = "waiting"

    lines, panes = overlays(df, spec)
    view = sig.iloc[-bars:]
    markers = []
    for _, row in view.iterrows():
        ts = int(row["time"].timestamp())
        for col, kind in (("entry", "long_entry"), ("short_entry", "short_entry")):
            if row[col]:
                markers.append({"time": ts, "kind": kind})
    return {
        "bar_time": t.isoformat(), "bar_close_time": (t + tf).isoformat(),
        "next_decision": (t + 2 * tf).isoformat(), "close": close, "atr": atr,
        "rule": rule_text(spec), "sides": sides, "headline": headline, "mood": mood,
        "candles": [[int(r.time.timestamp()), float(r.open), float(r.high), float(r.low), float(r.close),
                     float(r.volume)] for r in view.itertuples()],
        "lines": [{"name": l["name"], "role": l["role"], "points": _series(sig["time"], l["values"], bars)}
                  for l in lines],
        "panes": [{"name": p["name"], "levels": p["levels"], "points": _series(sig["time"], p["values"], bars)}
                  for p in panes],
        "signals": markers,
    }
