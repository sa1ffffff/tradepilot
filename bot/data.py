"""Candle download (paged, OKX returns at most 300 per call) and a CSV cache
under data/cache/ so research doesn't re-download a year of bars every run.
Only public market data -- no API keys involved."""
from __future__ import annotations

import os

import pandas as pd

CACHE_DIR = os.path.join("data", "cache")


def candles_to_df(rows: list[list]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
    df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    return df


def fetch_closed(client, symbol: str, timeframe: str, bars: int | None = None,
                 since_ms: int | None = None) -> pd.DataFrame:
    """Closed candles, oldest first: the last `bars` of them, or all since `since_ms`."""
    tf_ms = client.parse_timeframe(timeframe) * 1000
    now = client.milliseconds()
    since = since_ms if since_ms is not None else now - (bars + 1) * tf_ms
    rows: dict[int, list] = {}
    while since < now:
        batch = client.fetch_ohlcv(symbol, timeframe, since=since, limit=300)
        if not batch:
            break
        for r in batch:
            rows[r[0]] = r
        nxt = batch[-1][0] + tf_ms
        if nxt <= since:
            break
        since = nxt
    closed = [rows[t] for t in sorted(rows) if t + tf_ms <= now]  # drop the forming candle
    if bars is not None:
        closed = closed[-bars:]
    return candles_to_df(closed)


def public_client(hostname: str):
    import ccxt
    return ccxt.okx({"enableRateLimit": True, "hostname": hostname})


def load_history(cfg, symbol: str, timeframe: str, days: int, refresh: bool = True) -> pd.DataFrame:
    """`days` of closed candles from the cache, topped up from OKX."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{symbol.replace('/', '-')}_{timeframe}.csv")
    cached = pd.read_csv(path, parse_dates=["time"]) if os.path.exists(path) else None
    start = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)

    if refresh:
        client = public_client(cfg.okx_hostname)
        if cached is not None and len(cached) and cached["time"].iloc[0] <= start:
            since = int(cached["time"].iloc[-1].value // 1_000_000) + 1
            new = fetch_closed(client, symbol, timeframe, since_ms=since)
            df = pd.concat([cached, new])
        else:
            df = fetch_closed(client, symbol, timeframe, since_ms=int(start.value // 1_000_000))
        df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
        df.to_csv(path, index=False)
    elif cached is None:
        raise SystemExit(f"no cached data at {path}; run without --offline first")
    else:
        df = cached
    return df[df["time"] >= start].reset_index(drop=True)
