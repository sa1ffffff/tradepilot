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
| `bot/strategies.py` | nine strategies: five classics (EMA cross, trend pullback, Donchian breakout, Bollinger reversion, Supertrend) and four cost-aware variants for 1h/4h with slow trend filters, an ADX trend-strength gate and trailing exits |
| `bot/indicators.py` | EMA, RSI, ATR, Bollinger, Supertrend, computed the way TradingView computes them |
| `bot/engine.py` | the simulation used by backtest and research: maker/taker costs, ATR stop, take-profit |
| `bot/costs.py` | the cost model shared by engine, risk gate and live bot |
| `bot/risk.py` | sizing (1% risk against the stop, capped at cash and `MAX_NOTIONAL_USD`), daily loss limit, kill switch |
| `bot/runner.py` | the live loop; tracks its own position in `state.json` |
| `research.py` | walk-forward test of every strategy; `--save` writes the winner to `strategy.json` |
| `check_connection.py` | read-only check of your OKX demo account (never places orders) |
| `session_report.py` | after a demo run: compares your live demo trades with the backtest over the same hours |
| `dashboard.py` + `web/` | the console: status, P&L, trades, live strategy analysis and controls |

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
python research.py                  # BTC + ETH, 1h/4h, last 3 years, maker execution
python research.py --execution taker   # same with market orders, for comparison
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

### Strategy files

The bot trades whatever `STRATEGY_FILE` in `.env` points to (default
`strategy.json`). `research.py --save-all` writes every passing strategy to
`strategies/`, so you can switch between them:

| File | Use |
|---|---|
| `strategies/plumbing_test_5m.json` | **Setup test only.** EMA 9/21 on 5m, several trades a day, so a 1–2 day demo run has enough orders to compare with the backtest. No edge; it loses money after costs |
| `strategies/chandelier_trend_btc_4h.json` | research candidate, BTC 4h, ~2 trades a month |
| `strategies/ema_cross_adx_eth_1h.json` | research candidate, ETH 1h, ~4 trades a month |

The candidates trade too rarely to show anything in a day or two; they need a
forward demo run of several weeks.

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

For futures, the same check strategy by strategy:

```bash
python futures_session_report.py
```

It replays every strategy in `FUT_STRATEGY_FILE` (or `--files ...`) over the hours the bot
ran, on the demo candles, and matches each live trade to the backtest by signal bar and
side. A backtest entry the bot didn't take is marked "explained" when the log shows the
strategy wasn't running then, or that the bot skipped it on purpose; anything else is a
mismatch to investigate. Writes `reports/futures_session_<date>.md`.

### Full run report

```bash
python demo_report.py
```

Writes `reports/demo_run_<date>.md` covering both bots: every trade, P&L per market,
exit reasons, the real limit-order fill share and entry slippage, and every error type.
It also writes `reports/measured_costs.json`; put its maker fill share into
`MAKER_FILL_RATE` in `.env` (or pass `--maker-fill-rate` to `research.py`) so the next
research round uses what actually happened instead of assumptions.

### The console

Double-click `start_dashboard.bat` (or run `python dashboard.py`) and it opens
http://127.0.0.1:8765. It shows:

- **Overview**: today's and all-time P&L, open positions at the live demo price, both bots' status,
  and, for every strategy, what it sees on its latest closed candle and how far price is from the
  trigger.
- **Strategies**: one chart per strategy with its indicators, past signals, the trigger price as a
  dashed line, and a checklist of each entry condition (met or not), plus its research evidence.
- **Trades**: every closed trade. Open one for the candles around it, why it entered (the
  conditions on the signal candle), how it ended, slippage and limit-fill share.
- **Activity**: every fill, skipped signal, stop move, start, stop and error.
- **Controls**: start / stop each bot, pause new entries (the KILL file), close a position, and a
  **daily profit target**. Enter a target and your funds, press *Assess the risk*: it estimates from
  each strategy's research record how often a day would reach it, then asks you to confirm. Once
  both bots' realized P&L for the UTC day reaches it, they take no new trades until midnight UTC
  (optionally closing open positions too).

The console never reads your API keys. Stop and Close leave a request in `control/` that the bot
itself carries out on its next check (within a second or two), so its state and stops stay
consistent; closing therefore needs the bot running. Starting a bot runs the same
`python -m bot.runner` / `python -m bot.futures_runner`, with output in `logs/spot.out` /
`logs/futures.out`.

**On your phone**: run `start_dashboard_lan.bat` (or `python dashboard.py --lan`). The window prints
a link with a private token; open it on a phone on the same Wi-Fi. Anyone with that link can start
and stop the bots, so keep it to yourself. Windows may ask to let Python through the firewall:
allow it on private networks only.

The UI source is in `web/` (React + Vite). After changing it: `cd web`, `npm install` once, then
`npm run build`.

## Settings (`.env`)

| Setting | Meaning |
|---|---|
| `RISK_FRACTION` | fraction of equity risked per trade, sized against the stop |
| `MAX_NOTIONAL_USD` | hard cap on one position (live only) |
| `MAX_DAILY_LOSS_USD` | once the day is down this much, no new entries (live only) |
| `EXECUTION` | `maker` (default): post-only limit at the best bid/ask, re-priced `MAKER_ATTEMPTS` times, `MAKER_WAIT_SECONDS` each, then a market order for the rest. Stop exits are always market. `taker`: market orders only |
| `MAKER_FEE`, `TAKER_FEE` | your fee rates; defaults are OKX's regular spot tier (0.08% / 0.10%). `check_connection.py` prints your account's real rates |
| `SLIPPAGE_BPS` | assumed slippage on market orders |
| `MAKER_FILL_RATE` | share of maker attempts research assumes will fill (default 70%); `session_report.py` measures the real share |
| `MAX_COST_PER_R` | skip entries whose round-trip costs exceed this share of the amount risked (default 20%) |
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

## Futures (perpetual swaps, demo)

A second bot trades USDT-margined perpetual swaps, long and short:

```bash
python research.py --market swap --save   # research long/short; writes strategies/futures.json
python check_futures.py                   # read-only pre-flight
python -m bot.futures_runner              # trade on the demo account
```

- **Shorts** come from the same rules applied to the chart upside down, so a breakout
  becomes a breakdown without a second set of parameters. Research tests every strategy
  long-only and long+short.
- **Size and leverage:** each trade loses `FUT_RISK_FRACTION` of equity at the stop.
  Leverage is set from volatility: the highest that keeps the liquidation price at least
  `FUT_LIQ_BUFFER`× further away than the stop, capped at `FUT_MAX_LEVERAGE`. Margin
  never exceeds `FUT_MAX_MARGIN_FRACTION` of equity. Margin is **isolated**.
- **The stop-loss lives on OKX** (an algo order closing the whole position), so it works
  even if the bot or PC is down. A position without its stop is closed immediately;
  a missing stop is re-placed on the next poll.
- **OKX errors mid-order:** a signal is marked as handled before the order goes out, so a
  lost reply can't cause a second entry. If the entry errors, the next poll checks OKX: no
  position and no resting order means nothing went through, and the signal is retried
  (`entry_retry` in the log). A failed exit is retried straight away (exits are reduce-only).
- **Trailing stop:** once a trade is `FUT_TRAIL_START_R`× its risk in profit, the OKX
  stop follows the best price at `FUT_TRAIL_MULT`× the strategy's stop distance and only
  ever tightens (the new stop is placed before the old one is cancelled). Defaults 2R / 2×
  leave the researched results almost unchanged while capping big give-backs; the BTC
  5m test slot uses a tight 1R / 1× (`trail_start_r`, `trail_mult` in its strategy file).
  The backtest engine applies the same rule.
- State: `state_futures.json`; log: `logs/futures.log`. The `KILL` file blocks entries
  for both bots.

## Time Machine (read-only)

```bash
python timemachine.py                 # next 12 months for the strategies in FUT_STRATEGY_FILE
python timemachine.py --risk 0.01     # same at 1% risk per trade
```

Replays each strategy's out-of-sample trades 10,000 times to show the range of outcomes:
typical and 1-in-20 bad returns, the odds of a losing year, drawdowns and losing streaks.
The portfolio row resamples whole historical months for all coins together, so coins that
fell together still fall together. It also shows how each strategy's trades have ended
(stop, target, exit signal). It only reads cached candles; it never touches the account,
and the bots don't import it. It doesn't model the margin cap or daily loss limit, and the
strategies were picked on this same data, so treat the numbers as optimistic.
