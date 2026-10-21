# Futures slot selection (2026-10-21)

Every perpetual-swap CANDIDATE from the maker-cost walk-forward (3 years, 1h/4h; 15m: 1 year) was re-run through the same walk-forward with **taker-only costs** (0.05% + 2 bps slippage on every fill). It passes if return > 0, profit factor >= 1.1 and >= 3 of 4 out-of-sample segments are profitable.

Slots: one per coin, among passes on 1h/4h with >= 40 trades and maker drawdown no worse than -35%, highest taker t-stat. BTC has no slot: none of its 1h/4h candidates survived taker costs.

| strategy | maker return | maker PF | taker return | taker PF | taker folds+ | trades | pass | slot |
|---|---|---|---|---|---|---|---|---|
| BTC/USDT:USDT 15m bollinger_reversion | 11.02% | 1.4 | 4.89% | 1.37 | 3 | 30 | True |  |
| LTC/USDT:USDT 4h bollinger_reversion | 16.81% | 1.45 | 15.12% | 1.41 | 3 | 73 | True | **yes** |
| ADA/USDT:USDT 1h breakout_htf | 107.39% | 1.42 | 97.19% | 1.38 | 4 | 118 | True |  |
| DOGE/USDT:USDT 4h breakout_htf | 25.87% | 1.28 | 24.41% | 1.26 | 3 | 62 | True |  |
| XRP/USDT:USDT 1h breakout_htf | 65.17% | 1.2 | 110.64% | 1.5 | 4 | 118 | True |  |
| BTC/USDT:USDT 4h chandelier_trend | 20.06% | 1.29 | 16.01% | 1.23 | 2 | 81 | False |  |
| SOL/USDT:USDT 1h chandelier_trend | 72.17% | 1.29 | 57.85% | 1.24 | 3 | 196 | True |  |
| XRP/USDT:USDT 4h chandelier_trend | 37.33% | 1.54 | 32.44% | 1.46 | 4 | 94 | True |  |
| BNB/USDT:USDT 4h donchian_breakout | 16.78% | 1.22 | 13.71% | 1.18 | 3 | 80 | True | **yes** |
| SOL/USDT:USDT 4h donchian_breakout | 22.67% | 1.33 | 13.08% | 1.19 | 3 | 78 | True |  |
| XRP/USDT:USDT 4h donchian_breakout | 64.3% | 1.49 | 60.43% | 1.46 | 4 | 85 | True | **yes** |
| ETH/USDT:USDT 1h ema_cross_adx | 58.98% | 1.57 | 52.68% | 1.51 | 3 | 95 | True | **yes** |
| LTC/USDT:USDT 1h ema_cross_adx | 37.15% | 1.23 | 30.23% | 1.19 | 3 | 93 | True |  |
| SOL/USDT:USDT 4h ema_cross_adx | 57.11% | 2.28 | 55.84% | 2.25 | 4 | 42 | True | **yes** |
| BNB/USDT:USDT 4h ema_cross | 46.61% | 1.7 | 15.82% | 1.18 | 3 | 65 | True |  |
| DOGE/USDT:USDT 4h ema_cross | 146.04% | 2.17 | 142.97% | 2.14 | 3 | 54 | True |  |
| BTC/USDT:USDT 1h pullback_htf | 34.05% | 1.2 | -8.72% | 0.93 | 1 | 88 | False |  |
| ADA/USDT:USDT 4h supertrend | 63.32% | 1.75 | 60.59% | 1.71 | 4 | 85 | True | **yes** |
| AVAX/USDT:USDT 4h supertrend | 28.75% | 1.29 | 26.8% | 1.27 | 3 | 83 | True | **yes** |
| BTC/USDT:USDT 1h supertrend | 54.76% | 1.26 | -4.48% | 0.97 | 1 | 132 | False |  |
| DOGE/USDT:USDT 4h supertrend | 106.03% | 2.13 | 103.14% | 2.09 | 3 | 56 | True | **yes** |
| SOL/USDT:USDT 4h supertrend | 13.86% | 1.38 | 13.0% | 1.36 | 2 | 31 | False |  |
| DOGE/USDT:USDT 4h trend_pullback | 17.66% | 1.73 | 16.61% | 1.67 | 3 | 46 | True |  |
| ETH/USDT:USDT 4h trend_pullback | 13.49% | 1.26 | 11.85% | 1.22 | 3 | 53 | True |  |
