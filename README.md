# okx-demo-bot

A deterministic crypto trading bot that runs against **OKX demo (simulated) trading** —
fake money, real API, real plumbing. The point of this stage is to prove the whole
loop works and to measure a strategy honestly before any real capital is involved.

There is no AI in the trading loop here, by design. The signal is a plain EMA
crossover; the risk layer is hard-coded. That keeps every decision auditable while
you validate. Claude's role at this stage is building and reviewing this code — not
placing trades.

## How it works

```
OKX candles ──► strategy (EMA cross + ATR) ──► risk gate ──► OKX demo order
                     closed bars only          size / limits      (simulated)
```

- **strategy.py** — EMA(fast/slow) crossover, read only off closed bars, with ATR for the stop.
- **risk.py** — position sizing (risk a fixed fraction against the ATR stop), per-trade notional cap, daily loss limit, idempotency, kill switch.
- **exchange.py** — ccxt wrapper for OKX, sandbox mode on by default.
- **runner.py** — the live demo loop (long/flat). Tracks its own position and daily P&L in `state.json`, and exits on a sell signal or when price hits the ATR stop (checked every poll).
- **backtest.py** — runs the strategy over history (sample data or real candles) and reports stats.

## Setup

```bash
cd okx-demo-bot
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Get OKX demo keys (free, no real funds)

1. Log in to OKX → **Trade → Demo Trading** (switches the whole UI to simulated).
2. Profile → **API** → create keys **inside Demo Trading**. These are separate from real-account keys.
3. Give the key **Trade** permission and set a passphrase.
4. Put the API key, secret, and passphrase into `.env`. Leave `DEMO=true`.

## Run the backtest first (no keys needed)

```bash
python make_sample_data.py     # writes synthetic candles to data/
python backtest.py             # runs on the sample data
```

Real OKX candles (public data, still no keys needed):

```bash
python backtest.py --live --symbol BTC/USDT --timeframe 1h --limit 1000
```

On the bundled synthetic data this plain EMA cross **loses money** — low win rate,
negative expectancy. That is expected and it is the lesson: the pipeline is correct,
the naive strategy has no edge. Finding an edge is the work you do *after* the plumbing
is trusted, by testing real data and better rules. Do not run anything live until a
strategy shows a positive, stable edge across different market conditions.

## Run the demo bot

With `.env` filled in and `DEMO=true`:

```bash
python -m bot.runner
```

It polls every `POLL_SECONDS`, acts only on closed bars, and places **simulated** orders.
Logs stream as JSON to the console and to `logs/bot.log`.

### Kill switch

```bash
touch KILL      # stops new entries immediately (PowerShell: ni KILL)
rm KILL         # resumes
```

Exits and the stop keep working while KILL is present.

### State file

`state.json` holds the bot's open position (entry, size, stop) and today's realized
P&L, so a restart neither forgets the position nor resets the daily loss limit. The bot
only ever sells what it bought itself: OKX demo accounts start with BTC already in them,
and that balance is left alone. Delete `state.json` only while the bot is stopped and flat.

Stop the process any time with Ctrl-C.

## Risk settings (`.env`)

| Setting | Meaning |
|---|---|
| `RISK_FRACTION` | fraction of equity risked per trade, sized against the ATR stop |
| `MAX_NOTIONAL_USD` | hard cap on how much goes into one position |
| `MAX_DAILY_LOSS_USD` | once the day is down this much, no new entries |
| `ATR_STOP_MULT` | stop distance = this × ATR |

The backtest sizes by `RISK_FRACTION` (capped at available equity, since this is spot)
to show the strategy's edge; the live bot also applies `MAX_NOTIONAL_USD`, so real demo
positions stay small while you watch it. Both honour the ATR stop and charge fees on
entry and exit.

Run the tests with `python -m pytest -q`.

## What to verify before even thinking about live

- Orders appear in your OKX demo account matching the logs.
- The kill switch halts entries.
- The daily loss limit stops trading when breached.
- Backtest on real candles shows a positive, repeatable edge — not one lucky run.

## Not done here (on purpose)

Leverage, shorting, stop orders resting on the exchange (the stop is enforced by the
bot on each poll, so it only works while the bot is running), and any
Claude-in-the-loop decision layer. Those come after this demo is trusted. The gated
Claude decision layer plugs in at the risk gate — it can veto or resize a trade, never
trigger one.

---

This is demo tooling for learning, not financial advice. Trading real crypto can lose
real money, including with leverage very quickly. Keep `DEMO=true` until you have your
own verified results and understand exactly what flipping it changes.
