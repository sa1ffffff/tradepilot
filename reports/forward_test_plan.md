# Forward test plan (demo), prepared 2026-10-22

**Goal:** check, on OKX demo with real fills, that the researched strategies behave the way
research says, before anyone thinks about real money. The goal is to learn whether research
can be trusted, not to make money in a few weeks.

**Duration:** at least **6 weeks**, ideally 8. About 40 futures trades in 2 months is the
minimum to compare against expectations. Fewer trades than that say very little.

## What runs

Settings are in `.env`; nothing starts until you start the bots.

**Futures bot** (`python -m bot.futures_runner`): 8 strategies, all 4h candles, each risking
2% of equity (~$102 now), leverage set from volatility (3–5×), margin at most 50% of equity
across all positions, stop resting on OKX, trailing stop from 2R at 2× the stop distance.

| Market | Strategy | Out-of-sample evidence (3 yrs, measured costs) |
|---|---|---|
| ADA | 4h supertrend, long+short | +88%, PF 2.04, 4 of 4 folds |
| AVAX | 4h supertrend, long+short | +40%, PF 1.41 |
| BNB | 4h donchian_breakout | +31%, PF 1.45, 4 of 4 folds |
| DOGE | 4h supertrend | +82%, PF 2.10 |
| ETH | 4h trend_pullback, long+short (**new**) | +13%, PF 1.33 |
| LTC | 4h bollinger_reversion | +15%, PF 1.42 |
| SOL | 4h donchian_breakout (**new**) | +29%, PF 1.52 |
| XRP | 4h donchian_breakout | +76%, PF 1.49, 4 of 4 folds |

**Spot bot** (`python -m bot.runner`): BTC/USDT 4h chandelier_trend (+22.9% out of sample,
PF 1.81, 3 of 4 folds), long only, up to $1,000 a position, $100 daily loss limit.
About 2 trades a month, so spot will produce only a handful of trades in this test.

Removed: the BTC 5m test slots (spot and futures). They existed to exercise the plumbing,
and they did.

## What "as expected" looks like after 2 months

From `timemachine.py --months 2` (10,000 replays of the strategies' out-of-sample trades,
`timemachine_20261022_183010.md`):

| | Futures portfolio |
|---|---|
| Trades | ~38 |
| Typical result | **+16.6%** |
| Bad 1-in-20 result | **−18.5%** |
| Chance of being down | 24% |
| Typical / bad worst drop from a peak | 14% / 24% |
| Losing streak to expect (1-in-20) | 13 trades in a row |

A result anywhere in that range is consistent with the research. Being down after two
months is not, by itself, evidence of a problem; a 1-in-4 chance is common.

## Weekly check (10 minutes)

1. Dashboard (`start_dashboard.bat`): both bots running, no red banner.
2. `python demo_report.py`: trades, P&L, limit-fill share, errors.
3. `python session_report.py`: spot trades vs backtest. Expect every entry to match.
4. Note anything unexpected in a new `reports/lessons_<date>.md`.

The 2-hourly health check is paused: resume it under **Scheduled** in the Claude app when the
bots start.

## Stop and investigate if

- A live trade has no matching backtest trade, or the backtest shows one the bot missed.
- A position is ever open without its OKX stop (the log would show `stop_missing_replacing`
  or `stop_failed_closing`).
- Drawdown passes **25%** (worse than the 1-in-20 case), or a losing streak passes 13.
- Limit fills drop well below 54% or entry slippage averages worse than +5 bps.
- Either bot repeatedly stops on its own.

## At the end

1. `demo_report.py`, then put the measured fill share into `MAKER_FILL_RATE`.
2. Re-run research and the time machine with the new costs and the extra months of data.
3. Compare each strategy's live trades with its research: same exit mix (stop / target /
   signal), win rate and average R in the same ballpark.
4. Write the lessons file and decide what goes into the next round.

Known gap: there's no futures equivalent of `session_report.py` yet (futures trades are in
`demo_report.py`, but not replayed against the backtest trade by trade). Worth building
before the end of the test.
