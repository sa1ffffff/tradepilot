# Strategy research, 2026-10-23

**Question:** which published, well-tested rule-based strategies should the bot add to its
deterministic decision making, and do they beat what it trades now?

**Short answer:** two published trend-following rules (a Donchian trend ensemble and
time-series momentum) are now the most consistent strategies in the library. They made money
out of sample on 14 of 18 coin and timeframe pairs. Two published mean-reversion rules did not
carry over to crypto. None of the four beat the strategy already trading on its coin by enough
to justify the extra risk, so **the futures lineup stays at the same 8 slots**. All four strategies are in the
library, screened by `research.py` and explained in the console.

These are research estimates on demo data, not investment advice.

## What the evidence says (sources)

| Idea | Source | What it claims | Verdict before testing |
|---|---|---|---|
| Donchian trend ensemble | Zarattini, Pagani & Barbon (2025), *Catching Crypto Trends*, SSRN 5209907 | An average of Donchian breakouts over 5–360 day lookbacks with a midpoint trailing stop. Net Sharpe above 1.5 on a rotating top-20 crypto basket. | Strong. Recent, crypto-specific, simple. |
| Time-series momentum | Liu & Tsyvinski (2021), *Risks and Returns of Cryptocurrency*, RFS. Liu, Tsyvinski & Wu (2022), *Common Risk Factors in Cryptocurrency*, JF | Past 1–8 week returns predict the next weeks. This is the most replicated crypto return predictor. | Strong, though later work (Arefev, SSRN) finds the effect weaker since 2021 and dependent on the market regime. |
| RSI(2) pullback | Connors & Alvarez, *Short Term Trading Strategies That Work* | Buy a 2-period RSI dip in an uptrend. | Weak for crypto. It was built on equity indices, which mean-revert. Crypto trends. |
| Overreaction fade | De Nicola, intraday Bitcoin autocorrelation studies | Hourly to 4-hour Bitcoin returns are slightly negatively autocorrelated, and large moves reverse more often. | Mixed. The effect is small next to costs. |
| Funding-rate signals | Several working papers | Extreme funding predicts reversals. | Not testable here: OKX only serves about 3 months of funding history. |
| AdaptiveTrend | arXiv 2602.11708 | A regime-adaptive trend filter. | A preprint with no public code. Skipped. |

The literature mostly agrees on one thing. In crypto, trend following and momentum have held
up out of sample, and short-term mean reversion mostly has not.

## How they were tested

All four were added to `bot/strategies.py`. Each uses a small parameter grid, so there is
little room to overfit. They went through the same anchored 4-fold walk-forward as every other
strategy: 3 years of OKX perpetual candles, 9 coins, 1h, 4h and 1d candles, measured
maker/taker costs and a 54% maker fill rate. The gate is unchanged: at least 30 out-of-sample
trades, PF ≥ 1.2, a positive return and at least 3 of 4 folds positive. Tests in
`tests/test_strategy.py` check that each signal gives the same answer on the live window and on
the full history. Tests in `tests/test_console.py` check that the console's explanation agrees
with the signal.

The full table is in `research_20261023_112206_maker_swap.md`. The 1d rows are left out below
because almost none reach 30 trades.

## Results: how often each strategy made money out of sample (1h and 4h, 9 coins)

| Strategy | PF > 1 | Passed the gate | Out-of-sample trades |
|---|---|---|---|
| **Time-series momentum (new)** | **14 / 18** | **8** | 2,243 |
| **Trend ensemble (new)** | **14 / 18** | 3 | 2,828 |
| Donchian breakout | 12 / 18 | 6 | 3,395 |
| HTF breakout | 12 / 18 | 2 | 2,374 |
| EMA cross + ADX | 10 / 18 | 0 | 1,267 |
| Supertrend | 9 / 18 | 4 | 3,371 |
| EMA cross | 9 / 18 | 4 | 3,762 |
| Chandelier trend | 8 / 18 | 4 | 3,099 |
| Trend pullback | 7 / 18 | 1 | 1,236 |
| Overreaction fade (new) | 5 / 18 | 2 (AVAX, LTC 4h, small gains) | 2,124 |
| HTF pullback | 4 / 18 | 0 | 1,350 |
| Bollinger reversion | 4 / 18 | 1 | 1,887 |
| RSI(2) pullback (new) | 2 / 18 | 0 | 4,223 |

The test agreed with the papers. The two trend strategies made money on more coins than anything
the bot had. RSI(2) is the worst strategy in the library: it wins 60% of its trades, and the
losses still outweigh the wins once costs are counted.

## Does anything replace the current lineup?

There is one strategy per coin, because OKX nets positions per instrument. I decided the rule
before looking at the results: a new strategy replaces the incumbent only if it beats it on PF
**and** has at least as many out-of-sample trades. Choosing the highest number in the table
would be selection bias.

| Coin (4h) | Incumbent | Best new challenger | Rule says |
|---|---|---|---|
| ADA | Supertrend: PF 2.15, 73 trades | — | keep |
| AVAX | Supertrend: PF 1.38, 83 trades | TS momentum: PF 1.33, 80 trades | keep |
| BNB | Donchian breakout: PF 1.38, 61 trades | — | keep |
| DOGE | Supertrend: PF 2.17, 45 trades | TS momentum: PF 1.44, 60 trades | keep |
| ETH | Trend pullback: PF 1.36, 41 trades | Trend ensemble: PF 1.43, 104 trades | **test the swap** |
| LTC | Bollinger reversion: PF 1.42, 72 trades | TS momentum: PF 1.44, 61 trades | keep (fewer trades) |
| SOL | Donchian breakout: PF 1.55, 75 trades | TS momentum: PF 1.79, 63 trades | keep (fewer trades) |
| XRP | Donchian breakout: PF 1.49, 94 trades | Trend ensemble: PF 2.20, 42 trades | keep (fewer trades) |
| BTC | none (the spot bot trades BTC spot) | TS momentum: PF 1.69, 36 trades | **test adding it** |

The ETH swap and the BTC addition then went through the time machine
(`timemachine.py`, 10,000 replays, 2% risk). The portfolio row resamples whole historical
months, so coins that fell together still fall together.

| Lineup | 2 months: median | 2 months: bad 1-in-20 | 2 months: P(loss) | 2 months: chance of a drop over 20% |
|---|---|---|---|---|
| Current 8 | +18.0% | −15.9% | 22% | 17% |
| ETH → trend ensemble | +18.3% | −20.4% | 26% | 22% |
| + BTC TS momentum (9 slots) | +18.3% | −17.5% | 24% | 18% |

Over 12 months the ordering was the same. The ETH swap raised the median and made the bad case
clearly worse, with a bad-case drawdown of 47% against 41%. Adding BTC raised the median a little
and left the risk about the same. The 12-month medians (+240% and up) assume 2% risk compounding
over about 225 trades and every edge holding for a year. Treat them as a ceiling, not an
expectation.

**Decision:**
- **ETH swap: rejected.** The trend ensemble makes its money in a few big trends and loses small
  amounts in between. On a 2-month window it loses more often than trend pullback (P(loss) 53% on its
  own). Over a forward test, the extra drawdown costs more than the extra return is worth.
- **BTC TS momentum: not added (owner's call, 2026-10-23).** It is no worse on risk, but the gain
  is within noise and 36 trades is just over the gate. Its file stays in
  `strategies/tsmom_btc_4h_swap.json` for a later rebuild.

## Lessons

1. **More strategies did not make the honest number better.** The `auto` row picks the best
   strategy again in each fold, using only past data. With 13 strategies instead of 9 it got worse:
   the 4h `auto` returns summed to +33% across the 9 coins, against +104% in yesterday's run with 9
   strategies. More choice means more ways to fit noise. This is why the lineup changes only
   when a fixed rule says so.
2. **Breadth is better evidence than one good number.** A strategy that makes money on 14 of 18
   pairs with the same small grid is more believable than one row with PF 2.2. This is where the new
   trend rules beat the incumbents. If the lineup is rebuilt later, for example after the forward
   test, start from those two.
3. **Sizing is already volatility-scaled.** The paper's 25% volatility target mostly does what
   2% risk with an ATR stop already does: positions shrink when a coin gets wilder. Nothing new to add.
4. **Mean reversion does not carry over from equities.** RSI(2) and the overreaction fade lose
   after costs on most coins. LTC 4h Bollinger reversion is the one mean-reversion slot left, and it
   should be watched.

## Changes in this round

- `bot/strategies.py`: `donchian_ensemble`, `tsmom`, `rsi2_reversion`, `shock_reversal`.
- `bot/explain.py`: plain-language checks, trigger levels and chart overlays for each, so the
  console can show what they are waiting for.
- `web/src/lib/format.ts`: display names.
- Tests: signal consistency, and explanations that agree with signals.
- `strategies/`: new candidate files (BTC 4h TS momentum and EMA cross, ETH 4h trend ensemble and
  Donchian breakout). `.env` is unchanged, so the bots trade the same 8 + 1 as before.
