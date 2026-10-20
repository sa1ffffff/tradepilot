# tradepilot — OKX demo trading bot

A deterministic crypto trading bot that runs on your own PC against **your OKX
demo (simulated) account**: fake money, real API, real orders in the demo book.
Phase 1 is about two things: finding a strategy that holds up on data it was
never tuned on, and proving that the live bot does exactly what the backtest
says it does.

There is no AI in the trading loop. Strategies are plain indicator rules, and
the risk layer is hard-coded, so every decision can be audited.

## How it works

```
OKX candles ─► strategy (strategy.json) ─► risk gate ─► OKX demo order
              closed bars only             size / limits    (simulated)
                                    ▲
           research.py picks it ────┘   stop + take-profit checked every poll
```

| File | What it does |
|---|---|
| `bot/strategies.py` | five strategies (EMA cross, trend pullback, Donchian breakout, Bollinger reversion, Supertrend) |
| `bot/indicators.py` | EMA, RSI, ATR, Bollinger, Supertrend, computed the way TradingView computes them |
| `bot/engine.py` | the simulation used by backtest and research: fees, slippage, ATR stop, take-profit |
| `bot/risk.py` | sizing (1% risk against the stop, capped at cash and `MAX_NOTIONAL_USD`), daily loss limit, kill switch |
| `bot/runner.py` | the live loop; tracks its own position in `state.json` |
| `research.py` | walk-forward test of every strategy; `--save` writes the winner to `strategy.json` |
| `check_connection.py` | read-only check of your OKX demo account (never places orders) |
| `session_report.py` | after a demo run: compares your live demo trades with the backtest over the same hours |

## 1. Install

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # macOS/Linux: cp .env.example .env
python -m pytest -q             # should be all green
```

## 2. Research a strategy (no account needed)

```bash
python research.py                  # BTC + ETH, 15m/1h/4h, last 365 days
python research.py --save           # also write the best passing strategy to strategy.json
```

It downloads public candles (cached in `data/cache/`), then for every
strategy runs a 4-fold **walk-forward** test: choose parameters on the past,
trade the next unseen segment with them, repeat. Only the unseen results are
reported. A strategy is a **CANDIDATE** only with ≥30 out-of-sample trades,
profit factor ≥1.2, a positive return, and at least 3 of 4 segments profitable.
The `auto` rows show what the process gives you when it picks among all
strategies each time; that is the most honest number in the table.

If nothing passes, `--save` refuses to write `strategy.json`. That isn't a bug:
it means no strategy has shown an edge. `--save --force` writes the best one
anyway, for testing the plumbing only.

## 3. Connect your OKX demo account

1. Log in at okx.com, open **Trade → Demo Trading**. The whole UI switches to simulated.
2. Still in demo mode: **Profile → API → Create API key**.
   - Permissions: **Read + Trade**. Never Withdraw.
   - Set a passphrase and write it down; OKX won't show it again.
   - IP allowlist: optional; if you set one, it must be your PC's public IP.
3. Put the three values in `.env`:
   ```
   OKX_API_KEY=...
   OKX_API_SECRET=...
   OKX_API_PASSPHRASE=...
   DEMO=true
   OKX_HOSTNAME=app.okx.com      # www.okx.com is blocked on some networks; EEA accounts: my.okx.com
   ```
4. Check it (read-only, places no orders):
   ```bash
   python check_connection.py
   ```
   It explains common failures (wrong passphrase, live key used in demo, clock
   off, IP allowlist).

`.env` is git-ignored; your keys never leave your PC.

## 4. Run the demo bot

```bash
python -m bot.runner
```

It polls every `POLL_SECONDS`, acts only on closed bars, and places
**simulated** orders in your demo account, at most `MAX_NOTIONAL_USD` per
position. Logs stream as JSON to the console and `logs/bot.log`. Keep the PC
awake while it runs: the stop and take-profit are checked by the bot, so they
only work while it's running. Stop it with Ctrl-C; restarting is safe.

The bot refuses to start with `DEMO=false`.

**Kill switch**: create a file named `KILL` in this folder (PowerShell: `ni KILL`)
to block new entries; delete it to resume. Exits keep working.

**State file**: `state.json` holds the bot's open position and today's realized
P&L, so a restart neither forgets the position nor resets the daily loss limit.
The bot only sells what it bought itself; the BTC a demo account starts with is
left alone. Delete `state.json` only while the bot is stopped and flat.

## 5. Check the run

```bash
python session_report.py
```

Lists your live demo trades next to the backtest's trades for the same
window, with matched entries, slippage and P&L. Phase 1 passes when they line
up. One or two days is far too few trades to show profitability by itself;
the matching proves the backtest is a faithful model of the bot, and the
research results are the evidence on profit.

## Settings (`.env`)

| Setting | Meaning |
|---|---|
| `RISK_FRACTION` | fraction of equity risked per trade, sized against the stop |
| `MAX_NOTIONAL_USD` | hard cap on one position (live only) |
| `MAX_DAILY_LOSS_USD` | once the day is down this much, no new entries (live only) |
| `FEE_RATE`, `SLIPPAGE_BPS` | cost assumptions for backtest and research |
| `OKX_HOSTNAME` | API host |

The strategy, its stop (`stop_atr`) and take-profit (`tp_r`, in multiples of
the stop distance) come from `strategy.json`.

## TradingView

The indicators here use TradingView's formulas (RMA-smoothed RSI/ATR,
`ta.supertrend`), so a chart in TradingView shows the same values the bot
uses. That's handy for eyeballing signals. To test an idea from TradingView,
describe the rules and add it to `bot/strategies.py`, so it goes through the
same walk-forward test.

---

Demo tooling for learning, not financial advice. Real crypto trading can lose
real money.
