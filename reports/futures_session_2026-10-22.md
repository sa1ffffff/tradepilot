# Futures session report

Window: 2026-10-21 07:38 → 2026-10-22 17:55 UTC (bot stopped; window ends at its last log line). Replayed on OKX demo candles.

## BTC/USDT 5m: ema_cross(fast=15,slow=40) stop=2.0ATR no tp +shorts

| Signal bar (UTC) | Side | Status | Live entry → exit | Backtest entry → exit | Entry diff | Live P&L |
|---|---|---|---|---|---|---|
| 2026-10-21 19:10 | short | matched | 84,302.3 → 84,489.1 (signal) | 84,306.3 → 84,557.2 (signal) | -0.5 bps | -8.43 |
| 2026-10-21 20:00 | long | matched | 84,516.1 → 84,480.3 (signal) | 84,557.2 → 84,480.1 (signal) | -4.9 bps | -3.04 |
| 2026-10-21 22:50 | short | matched | 84,485.8 → 81,329.8 (trailing stop) | 84,480.1 → 84,290.0 (stop) | +0.7 bps | +158.26 |

## ADA/USDT 4h: supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts

| Signal bar (UTC) | Side | Status | Live entry → exit | Backtest entry → exit | Entry diff | Live P&L |
|---|---|---|---|---|---|---|
| 2026-10-22 12:00 | short | only backtest | – | 0.2136 → 0.2136 (end) | – | – |

## AVAX/USDT 4h: supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts

No signals in this window (live or backtest).

## BNB/USDT 4h: donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=3.0ATR tp=3.0R

No signals in this window (live or backtest).

## DOGE/USDT 4h: supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R

No signals in this window (live or backtest).

## ETH/USDT 4h: trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=3.0ATR no tp +shorts

No signals in this window (live or backtest).

## LTC/USDT 4h: bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp

No signals in this window (live or backtest).

## SOL/USDT 4h: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R

| Signal bar (UTC) | Side | Status | Live entry → exit | Backtest entry → exit | Entry diff | Live P&L |
|---|---|---|---|---|---|---|
| 2026-10-21 12:00 | long | explained: strategy wasn't running then | – | 108.4300 → 104.5700 (end) | – | – |

## XRP/USDT 4h: donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=2.0ATR tp=3.0R

No signals in this window (live or backtest).

## Summary

- Entries matched: **3**; explained by downtime or a deliberate skip: 1; only live: **0**; only backtest: **1**.
- Unexplained mismatches mean the bot and the backtest disagree: investigate them before trusting research results for that strategy.
- Exits can differ a little: live stops trigger on the traded price between bars, and a strategy's settings (trailing stop, size) may have changed during the window.
