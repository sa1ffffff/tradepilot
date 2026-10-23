# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React + Vite (TypeScript), built to `web/dist` and served by `dashboard.py` (Python stdlib HTTP server). Chosen by the user on 2026-10-23.

## Users

One person: the owner of the OKX demo account. They run the bots on their own Windows PC, check the console a few times a day on the desktop browser and on their phone (same local network), and do a 10-minute weekly review during a 6–8 week forward test.

## Product Purpose

Tradepilot runs deterministic, researched indicator strategies against an OKX **demo** account (spot BTC 4h and eight 4h perpetual-swap strategies). The console is where the owner sees everything the bots did and are about to do, and controls them: start/stop each bot, pause new entries, close a position, and set a daily profit target. Success: the owner never has to open a log file or a terminal to know what is happening or why.

## Positioning

Every decision is explainable: the bot's rules are plain indicator conditions, so the console can show, for any trade or for right now, exactly which conditions were met on which candle. No AI in the trading loop.

## Operating Context

- Bots: `python -m bot.runner` (spot) and `python -m bot.futures_runner` (futures); each holds an OS lock so only one copy runs.
- Logs are JSON lines in `logs/bot.log` and `logs/futures.log`; state in `state.json` and `state_futures.json`.
- Weekly tools: `demo_report.py`, `session_report.py`, `futures_session_report.py`; 2-hourly health check writes `logs/health.md`.
- Futures stops rest on OKX; spot stop is checked by the bot itself.

## Capabilities and Constraints

- Demo only. The bots refuse DEMO=false; the console must never suggest real-money trading.
- The console never reads or displays API keys. Actions that need the exchange are performed by the bots themselves through request files.
- Phone access goes over the local network and must be protected by a token.
- Candle and price data come from OKX public endpoints (demo prices).
- A daily profit target blocks new entries for the rest of the UTC day once realized P&L (both bots) reaches it; the risk assessment is a statistical estimate from research evidence, labelled as such.

## Evidence on Hand

Real trade history in the logs (13 closed trades so far), research evidence per strategy in `strategies/*.json`, reports in `reports/`. No invented performance claims.

## Product Principles

1. Show the reason, not just the result: every trade and every waiting state names its rule and the numbers.
2. Safety is visible: demo status, kill switch, stops and limits are always on screen.
3. Controls confirm before acting and say exactly what will happen.
4. Honest numbers: estimates are labelled as estimates; missing data says it is missing.

## Accessibility & Inclusion

Works at phone width; P&L direction is never shown by colour alone (sign and arrow too).
