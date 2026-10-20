# Research run 20261020_195236 UTC

1095 days, 4-fold anchored walk-forward. Execution maker: maker 0.080%, taker 0.100% + 2 bps slippage, 70% assumed maker fills; expected cost 0.092%/side normal, 0.120% on stops, 0.184% round trip; entries skipped when costs exceed 20% of the risk. Risk 1.0%/trade. All figures are out-of-sample (last 80% of the period).

**Read with care:** 36 strategy/market combinations were tested, so a few will pass by luck alone. Trust a CANDIDATE more if the same strategy also does well on the other symbol, survives `--execution taker`, and keeps working in a forward demo run. The `auto` rows (picking among all strategies each fold) are the best single estimate of what this research process is worth.

```
symbol     tf    strategy             trades  win%    PF      avg%     return%   maxDD%   B&H%     folds+  verdict       
BTC/USDT   1h    ema_cross            211     25.1    0.85    -0.079   -16.93    -26.39   19.16    2      no edge       
BTC/USDT   1h    trend_pullback       70      28.6    0.72    -0.133   -9.23     -11.79   19.16    1      no edge       
BTC/USDT   1h    donchian_breakout    211     30.8    0.77    -0.146   -28.61    -33.57   19.16    0      no edge       
BTC/USDT   1h    bollinger_reversion  49      59.2    0.86    -0.05    -2.59     -6.78    19.16    2      no edge       
BTC/USDT   1h    supertrend           118     32.2    0.72    -0.179   -20.14    -30.46   19.16    0      no edge       
BTC/USDT   1h    ema_cross_adx        55      21.8    0.94    -0.013   -2.22     -10.94   19.16    2      no edge       
BTC/USDT   1h    breakout_htf         129     26.4    0.67    -0.249   -28.73    -35.63   19.16    0      no edge       
BTC/USDT   1h    pullback_htf         78      26.9    0.91    -0.059   -5.59     -20.5    19.16    2      no edge       
BTC/USDT   1h    chandelier_trend     187     31.0    0.8     -0.08    -15.01    -24.67   19.16    2      no edge       
BTC/USDT   1h    auto                 150     25.3    0.74    -0.134   -19.07    -24.55   19.16    1      no edge       
BTC/USDT   4h    ema_cross            83      27.7    1.12    0.072    4.54      -18.02   19.27    2      no edge       
BTC/USDT   4h    trend_pullback       26      23.1    0.86    -0.06    -1.72     -4.64    19.27    1      too few trades
BTC/USDT   4h    donchian_breakout    53      32.1    1.01    0.019    0.4       -11.68   19.27    2      no edge       
BTC/USDT   4h    bollinger_reversion  94      59.6    0.78    -0.084   -7.92     -11.11   19.27    2      no edge       
BTC/USDT   4h    supertrend           65      36.9    1.1     0.053    2.78      -10.79   19.27    1      no edge       
BTC/USDT   4h    ema_cross_adx        14      42.9    2.64    0.776    10.81     -7.82    19.27    2      too few trades
BTC/USDT   4h    breakout_htf         23      39.1    1.39    0.267    5.95      -5.46    19.27    2      too few trades
BTC/USDT   4h    pullback_htf         14      21.4    0.89    -0.078   -1.36     -8.27    19.27    1      too few trades
BTC/USDT   4h    chandelier_trend     55      30.9    1.75    0.369    20.11     -10.14   19.27    2      no edge       
BTC/USDT   4h    auto                 57      28.1    0.74    -0.145   -8.33     -13.61   19.27    1      no edge       
ETH/USDT   1h    ema_cross            293     28.0    0.76    -0.121   -31.21    -34.92   -37.03   1      no edge       
ETH/USDT   1h    trend_pullback       83      19.3    0.85    -0.053   -4.87     -10.88   -37.03   2      no edge       
ETH/USDT   1h    donchian_breakout    156     30.1    0.97    0.005    -2.58     -17.69   -37.03   1      no edge       
ETH/USDT   1h    bollinger_reversion  104     61.5    0.7     -0.073   -7.45     -10.31   -37.03   1      no edge       
ETH/USDT   1h    supertrend           167     29.3    0.79    -0.107   -17.43    -20.08   -37.03   1      no edge       
ETH/USDT   1h    ema_cross_adx        94      26.6    1.48    0.287    25.21     -13.91   -37.03   2      no edge       
ETH/USDT   1h    breakout_htf         110     30.0    1.02    0.022    1.21      -15.73   -37.03   2      no edge       
ETH/USDT   1h    pullback_htf         82      28.0    0.8     -0.128   -10.73    -14.33   -37.03   1      no edge       
ETH/USDT   1h    chandelier_trend     219     29.2    1.04    0.023    3.44      -15.02   -37.03   2      no edge       
ETH/USDT   1h    auto                 209     29.7    0.92    -0.029   -7.38     -20.23   -37.03   2      no edge       
ETH/USDT   4h    ema_cross            74      21.6    1.23    0.188    11.07     -15.95   -36.96   2      no edge       
ETH/USDT   4h    trend_pullback       18      27.8    1.5     0.269    4.67      -6.29    -36.96   2      too few trades
ETH/USDT   4h    donchian_breakout    43      32.6    1.27    0.166    6.83      -8.07    -36.96   2      no edge       
ETH/USDT   4h    bollinger_reversion  115     59.1    0.91    -0.032   -3.97     -12.83   -36.96   1      no edge       
ETH/USDT   4h    supertrend           81      24.7    1.04    0.03     1.4       -11.42   -36.96   2      no edge       
ETH/USDT   4h    ema_cross_adx        15      26.7    0.78    -0.136   -2.16     -8.68    -36.96   2      too few trades
ETH/USDT   4h    breakout_htf         14      35.7    1.84    0.556    7.62      -4.97    -36.96   2      too few trades
ETH/USDT   4h    pullback_htf         15      13.3    0.35    -0.565   -8.25     -12.52   -36.96   0      too few trades
ETH/USDT   4h    chandelier_trend     30      33.3    2.06    0.445    13.13     -7.77    -36.96   2      no edge       
ETH/USDT   4h    auto                 52      26.9    0.95    -0.021   -1.65     -15.51   -36.96   2      no edge       
```

## Parameters chosen per fold

- **BTC/USDT 1h ema_cross**: ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R -> 3.69%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> 0.76%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> -12.63%; ema_cross(fast=9,slow=100) stop=3.0ATR no tp -> -9.0%
- **BTC/USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -3.59%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -2.39%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -3.9%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> 0.37%
- **BTC/USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -1.54%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=2.0ATR no tp -> -16.6%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR no tp -> -8.5%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR no tp -> -4.99%
- **BTC/USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp -> -2.85%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp -> 0.85%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R -> -1.8%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R -> 1.25%
- **BTC/USDT 1h supertrend**: supertrend(mult=3.0,trend=200) stop=2.0ATR no tp -> -0.99%; supertrend(mult=3.0,trend=200) stop=2.0ATR no tp -> -6.62%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -9.42%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -4.64%
- **BTC/USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR no tp -> -3.2%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> -0.59%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp -> 0.34%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp -> 1.27%
- **BTC/USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> -3.58%; breakout_htf(entry_n=20,trend=400) stop=2.0ATR no tp -> -12.68%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR no tp -> -6.54%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR no tp -> -9.43%
- **BTC/USDT 1h pullback_htf**: pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> 7.03%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> 0.3%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -10.92%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -1.28%
- **BTC/USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp -> 1.7%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp -> 3.91%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp -> -13.15%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp -> -7.4%
- **BTC/USDT 1h auto**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -3.59%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> 0.76%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> -12.63%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -4.64%
- **BTC/USDT 4h ema_cross**: ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> 6.83%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> -0.75%; ema_cross(fast=9,slow=100) stop=2.0ATR no tp -> -7.2%; ema_cross(fast=9,slow=100) stop=2.0ATR no tp -> 6.24%
- **BTC/USDT 4h trend_pullback**: nothing qualified -> 0.0%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R -> -0.77%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> 0.92%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -1.85%
- **BTC/USDT 4h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 1.03%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> -0.75%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 1.31%; donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -1.17%
- **BTC/USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -5.97%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 1.9%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -4.18%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 0.29%
- **BTC/USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> 9.73%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -1.59%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -0.97%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -3.89%
- **BTC/USDT 4h ema_cross_adx**: nothing qualified -> 0.0%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> 1.34%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> -4.07%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> 13.99%
- **BTC/USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 3.4%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> -0.75%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 3.23%
- **BTC/USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> 5.6%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -4.35%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -2.35%
- **BTC/USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> 9.01%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp -> -0.2%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR no tp -> -1.63%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR no tp -> 12.23%
- **BTC/USDT 4h auto**: donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 1.03%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -1.59%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> -4.07%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -3.89%
- **ETH/USDT 1h ema_cross**: ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> 0.43%; ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> -5.1%; ema_cross(fast=9,slow=50) stop=3.0ATR no tp -> -13.18%; ema_cross(fast=20,slow=21) stop=2.0ATR no tp -> -16.87%
- **ETH/USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -7.38%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> -0.1%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> 0.87%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> 1.93%
- **ETH/USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> -2.45%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> -4.34%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -0.44%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR no tp -> 4.86%
- **ETH/USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -1.94%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> 0.48%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -2.35%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -3.81%
- **ETH/USDT 1h supertrend**: supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R -> -14.1%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> 1.07%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -4.24%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> -0.68%
- **ETH/USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> -1.12%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> 9.29%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> -8.71%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR no tp -> 26.91%
- **ETH/USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> -2.85%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> 7.2%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R -> -4.09%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> 1.32%
- **ETH/USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -10.63%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR tp=3.0R -> 3.13%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R -> -1.92%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R -> -1.26%
- **ETH/USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=2.0ATR no tp -> -1.07%; chandelier_trend(trend=200,mult=2.5) stop=2.0ATR no tp -> 9.41%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> -12.46%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R -> 9.17%
- **ETH/USDT 1h auto**: ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> 0.43%; ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> -5.1%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R -> -4.09%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> 1.32%
- **ETH/USDT 4h ema_cross**: ema_cross(fast=9,slow=21) stop=2.0ATR no tp -> -3.98%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> 15.35%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> -5.45%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> 6.05%
- **ETH/USDT 4h trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R -> 2.43%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> 2.19%
- **ETH/USDT 4h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 4.84%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 5.34%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -2.57%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -0.72%
- **ETH/USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -1.05%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -3.82%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -3.56%; bollinger_reversion(k=2.0,trend=200) stop=2.0ATR no tp -> 4.61%
- **ETH/USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> -0.49%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> 10.87%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp -> 0.55%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp -> -8.6%
- **ETH/USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> 3.75%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> -2.1%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> -4.28%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp -> 0.63%
- **ETH/USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR no tp -> 8.1%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> -1.22%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 0.79%
- **ETH/USDT 4h pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R -> -7.15%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -1.19%
- **ETH/USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp -> 5.11%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp -> -1.68%; chandelier_trend(trend=200,mult=3.5) stop=2.0ATR no tp -> -1.14%; chandelier_trend(trend=200,mult=3.5) stop=2.0ATR no tp -> 10.74%
- **ETH/USDT 4h auto**: donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 4.84%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 5.34%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -2.57%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp -> -8.6%
