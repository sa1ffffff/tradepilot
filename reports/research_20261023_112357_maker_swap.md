# Research run 20261023_112357 UTC

1095 days, 4-fold anchored walk-forward. Execution maker: maker 0.020%, taker 0.050% + 2 bps slippage, 54% assumed maker fills; expected cost 0.043%/side normal, 0.070% on stops, 0.086% round trip; entries skipped when costs exceed 20% of the risk. Risk 2.0%/trade. Perpetual swaps: long and short, isolated margin, leverage from volatility up to 5x with liquidation >= 3x the stop distance, margin <= 50% of equity, funding 0.010%/8h charged to both sides. All figures are out-of-sample (last 80% of the period).

**Read with care:** 26 strategy/market combinations were tested, so a few will pass by luck alone. Trust a CANDIDATE more if the same strategy also does well on the other symbol, survives `--execution taker`, and keeps working in a forward demo run. The `auto` rows (picking among all strategies each fold) are the best single estimate of what this research process is worth.

```
symbol     tf    strategy             trades  win%    PF      avg%     return%   maxDD%   B&H%     folds+  verdict       
BTC/USDT:USDT  4h    ema_cross            76      32.9    1.4     0.506    35.84     -28.12   20.24    3      CANDIDATE     
BTC/USDT:USDT  4h    trend_pullback       65      27.7    0.97    0.005    -1.31     -18.68   20.24    1      no edge       
BTC/USDT:USDT  4h    donchian_breakout    54      33.3    1.11    0.179    7.36      -18.92   20.24    3      no edge       
BTC/USDT:USDT  4h    bollinger_reversion  94      58.5    0.78    -0.16    -15.03    -20.13   20.24    1      no edge       
BTC/USDT:USDT  4h    supertrend           77      36.4    1.09    0.109    5.78      -18.73   20.24    1      no edge       
BTC/USDT:USDT  4h    ema_cross_adx        25      44.0    2.87    1.739    46.31     -12.17   20.24    3      too few trades
BTC/USDT:USDT  4h    breakout_htf         31      29.0    0.92    -0.062   -3.46     -14.87   20.24    1      no edge       
BTC/USDT:USDT  4h    pullback_htf         24      25.0    0.73    -0.391   -10.13    -18.4    20.24    1      too few trades
BTC/USDT:USDT  4h    chandelier_trend     82      28.0    1.18    0.194    11.88     -23.28   20.24    2      no edge       
BTC/USDT:USDT  4h    donchian_ensemble    113     27.4    1.16    0.117    10.73     -20.0    20.24    3      no edge       
BTC/USDT:USDT  4h    tsmom                36      47.2    1.69    0.759    27.06     -14.57   20.24    3      CANDIDATE     
BTC/USDT:USDT  4h    rsi2_reversion       62      62.9    0.72    -0.123   -7.66     -13.2    20.24    1      no edge       
BTC/USDT:USDT  4h    shock_reversal       56      73.2    1.17    0.094    4.91      -8.38    20.24    2      no edge       
BTC/USDT:USDT  4h    auto                 60      50.0    0.97    -0.002   -1.72     -17.54   20.24    2      no edge       
ETH/USDT:USDT  4h    ema_cross            73      26.0    1.0     0.116    -0.21     -35.5    -35.79   2      no edge       
ETH/USDT:USDT  4h    trend_pullback       41      34.1    1.36    0.362    14.07     -9.46    -35.79   3      CANDIDATE     
ETH/USDT:USDT  4h    donchian_breakout    49      42.9    1.37    0.482    23.41     -13.71   -35.79   3      CANDIDATE     
ETH/USDT:USDT  4h    bollinger_reversion  104     60.6    0.92    -0.044   -5.58     -20.03   -35.79   1      no edge       
ETH/USDT:USDT  4h    supertrend           89      25.8    1.07    0.117    5.63      -23.56   -35.79   3      no edge       
ETH/USDT:USDT  4h    ema_cross_adx        25      32.0    0.59    -0.48    -11.95    -19.2    -35.79   2      too few trades
ETH/USDT:USDT  4h    breakout_htf         59      32.2    0.9     -0.077   -6.66     -23.29   -35.79   2      no edge       
ETH/USDT:USDT  4h    pullback_htf         33      27.3    0.7     -0.428   -14.36    -23.29   -35.79   1      no edge       
ETH/USDT:USDT  4h    chandelier_trend     88      29.5    1.01    0.036    1.05      -25.39   -35.79   3      no edge       
ETH/USDT:USDT  4h    donchian_ensemble    104     31.7    1.43    0.392    40.44     -20.71   -35.79   3      CANDIDATE     
ETH/USDT:USDT  4h    tsmom                34      38.2    1.63    0.644    20.98     -12.71   -35.79   2      no edge       
ETH/USDT:USDT  4h    rsi2_reversion       186     65.6    1.0     0.006    0.09      -12.51   -35.79   2      no edge       
ETH/USDT:USDT  4h    shock_reversal       41      58.5    0.79    -0.152   -6.51     -13.19   -35.79   1      no edge       
ETH/USDT:USDT  4h    auto                 56      30.4    0.74    -0.248   -14.06    -26.2    -35.79   2      no edge       
```

## Parameters chosen per fold

- **BTC/USDT:USDT 4h ema_cross**: ema_cross(fast=9,slow=50) stop=2.0ATR no tp -> 15.32%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp -> 7.39%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp -> -7.94%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp -> 19.16%
- **BTC/USDT:USDT 4h trend_pullback**: trend_pullback(trend=200,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp +shorts -> -6.85%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=65) stop=3.0ATR no tp -> -0.01%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> 12.33%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> -5.67%
- **BTC/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 7.01%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 5.33%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> -6.48%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 1.85%
- **BTC/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -10.76%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 4.91%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -7.86%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -1.5%
- **BTC/USDT:USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> 21.53%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> -3.67%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -1.87%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -7.92%
- **BTC/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp +shorts -> -0.04%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> 6.0%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> 4.53%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> 32.1%
- **BTC/USDT:USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R +shorts -> -0.92%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> -4.5%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 2.02%
- **BTC/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp +shorts -> 5.82%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -3.27%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp +shorts -> -12.21%
- **BTC/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> 19.24%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp -> -0.51%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R -> -6.43%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp +shorts -> 0.79%
- **BTC/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> 7.61%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> 3.95%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> -10.42%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 10.5%
- **BTC/USDT:USDT 4h tsmom**: tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> 15.39%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> 17.73%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> -7.67%; tsmom(lookback=84,z=1.0) stop=3.0ATR no tp -> 1.31%
- **BTC/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=2.0ATR tp=1.5R -> -2.63%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> -4.87%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> -1.47%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp +shorts -> 1.19%
- **BTC/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR no tp -> 5.17%; shock_reversal(k=2.5) stop=3.0ATR no tp -> 7.03%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -5.91%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -0.94%
- **BTC/USDT:USDT 4h auto**: rsi2_reversion(lo=5,trend=200) stop=2.0ATR tp=1.5R -> -2.63%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 5.33%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -5.91%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 1.85%
- **ETH/USDT:USDT 4h ema_cross**: ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> 11.0%; ema_cross(fast=20,slow=100) stop=2.0ATR tp=3.0R -> -7.86%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp -> -3.54%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp +shorts -> 1.15%
- **ETH/USDT:USDT 4h trend_pullback**: nothing qualified -> 0.0%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> 10.65%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> 0.44%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=2.0ATR no tp +shorts -> 2.64%
- **ETH/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 4.51%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 25.96%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -7.74%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 1.61%
- **ETH/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -1.96%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -7.25%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp +shorts -> -0.09%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp +shorts -> 3.93%
- **ETH/USDT:USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=2.0ATR no tp -> -9.61%; supertrend(mult=3.0,trend=200) stop=2.0ATR no tp +shorts -> 7.63%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp +shorts -> 0.06%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp +shorts -> 8.5%
- **ETH/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR no tp +shorts -> -8.39%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR tp=3.0R -> -8.72%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR no tp -> 1.71%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> 3.53%
- **ETH/USDT:USDT 4h breakout_htf**: breakout_htf(entry_n=20,trend=400) stop=2.0ATR tp=3.0R +shorts -> -0.07%; breakout_htf(entry_n=20,trend=800) stop=3.0ATR tp=3.0R +shorts -> 1.33%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R -> -9.24%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 1.56%
- **ETH/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 2.62%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -10.1%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -7.17%
- **ETH/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=2.5) stop=3.0ATR tp=3.0R -> 6.76%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 3.82%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 8.48%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> -15.96%
- **ETH/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=360,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> 15.49%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=3.0ATR no tp -> 12.69%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=3.0ATR no tp -> -6.55%; donchian_ensemble(max_n=360,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> 15.47%
- **ETH/USDT:USDT 4h tsmom**: tsmom(lookback=42,z=0.5) stop=3.0ATR no tp -> -1.4%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> 25.26%; tsmom(lookback=84,z=1.0) stop=3.0ATR no tp -> -8.51%; tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> 7.06%
- **ETH/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp -> -6.05%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp -> -3.93%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> 2.69%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> 7.99%
- **ETH/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR no tp -> -4.12%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 4.49%; shock_reversal(k=3.5) stop=2.0ATR tp=1.5R -> -4.27%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -2.51%
- **ETH/USDT:USDT 4h auto**: chandelier_trend(trend=100,mult=2.5) stop=3.0ATR tp=3.0R -> 6.76%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 3.82%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -7.74%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> -15.96%
