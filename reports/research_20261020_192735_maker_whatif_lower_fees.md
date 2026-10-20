# Research run 20261020_192735 UTC

1095 days, 4-fold anchored walk-forward. Execution maker: maker 0.040%, taker 0.060% + 2 bps slippage, 70% assumed maker fills; expected cost 0.052%/side normal, 0.080% on stops, 0.104% round trip; entries skipped when costs exceed 20% of the risk. Risk 1.0%/trade. All figures are out-of-sample (last 80% of the period).

```
symbol     tf    strategy             trades  win%    PF      avg%     return%   maxDD%   B&H%     folds+  verdict       
BTC/USDT   1h    ema_cross            232     24.6    1.0     0.016    -0.42     -22.75   19.16    2      no edge       
BTC/USDT   1h    trend_pullback       92      28.3    0.94    -0.02    -2.38     -11.76   19.16    2      no edge       
BTC/USDT   1h    donchian_breakout    300     28.7    0.86    -0.079   -23.31    -34.78   19.16    1      no edge       
BTC/USDT   1h    bollinger_reversion  65      67.7    1.18    0.058    3.61      -4.33    19.16    2      no edge       
BTC/USDT   1h    supertrend           138     34.8    0.99    0.008    -1.12     -18.86   19.16    2      no edge       
BTC/USDT   1h    ema_cross_adx        73      19.2    1.15    0.145    7.16      -17.46   19.16    2      no edge       
BTC/USDT   1h    breakout_htf         146     29.5    0.82    -0.105   -15.47    -24.04   19.16    1      no edge       
BTC/USDT   1h    pullback_htf         100     30.0    1.12    0.096    8.51      -13.85   19.16    3      no edge       
BTC/USDT   1h    chandelier_trend     215     27.9    0.73    -0.13    -25.75    -32.46   19.16    0      no edge       
BTC/USDT   1h    auto                 245     29.4    0.94    -0.023   -7.48     -22.75   19.16    2      no edge       
BTC/USDT   4h    ema_cross            111     27.9    1.05    0.035    2.45      -17.33   19.27    3      no edge       
BTC/USDT   4h    trend_pullback       26      26.9    0.97    -0.005   -0.28     -4.42    19.27    2      too few trades
BTC/USDT   4h    donchian_breakout    59      30.5    0.99    0.005    -0.36     -11.8    19.27    2      no edge       
BTC/USDT   4h    bollinger_reversion  94      59.6    0.8     -0.075   -7.06     -10.41   19.27    2      no edge       
BTC/USDT   4h    supertrend           64      39.1    1.12    0.064    3.46      -10.63   19.27    1      no edge       
BTC/USDT   4h    ema_cross_adx        15      33.3    1.5     0.287    4.16      -7.77    19.27    2      too few trades
BTC/USDT   4h    breakout_htf         23      39.1    1.31    0.204    4.46      -7.12    19.27    2      too few trades
BTC/USDT   4h    pullback_htf         14      21.4    0.6     -0.322   -4.54     -7.69    19.27    1      too few trades
BTC/USDT   4h    chandelier_trend     56      37.5    1.94    0.443    25.53     -9.32    19.27    3      CANDIDATE     
BTC/USDT   4h    auto                 71      28.2    0.79    -0.118   -8.6      -19.36   19.27    1      no edge       
ETH/USDT   1h    ema_cross            312     27.6    0.8     -0.096   -27.45    -32.74   -37.04   1      no edge       
ETH/USDT   1h    trend_pullback       85      18.8    0.92    -0.021   -2.36     -9.78    -37.04   3      no edge       
ETH/USDT   1h    donchian_breakout    177     31.1    0.99    0.001    -1.22     -14.37   -37.04   1      no edge       
ETH/USDT   1h    bollinger_reversion  135     63.0    0.84    -0.052   -7.14     -14.99   -37.04   2      no edge       
ETH/USDT   1h    supertrend           169     30.2    0.83    -0.083   -14.31    -17.04   -37.04   2      no edge       
ETH/USDT   1h    ema_cross_adx        114     27.2    1.39    0.24     25.33     -13.44   -37.04   3      CANDIDATE     
ETH/USDT   1h    breakout_htf         130     26.2    1.08    0.082    7.03      -21.9    -37.04   2      no edge       
ETH/USDT   1h    pullback_htf         88      27.3    0.79    -0.132   -11.79    -16.4    -37.04   1      no edge       
ETH/USDT   1h    chandelier_trend     217     30.0    0.98    0.0      -1.08     -13.12   -37.04   2      no edge       
ETH/USDT   1h    auto                 256     27.3    0.89    -0.037   -12.46    -30.47   -37.04   2      no edge       
ETH/USDT   4h    ema_cross            74      21.6    1.28    0.219    13.51     -15.48   -36.97   2      no edge       
ETH/USDT   4h    trend_pullback       14      14.3    0.41    -0.226   -3.16     -4.5     -36.97   1      too few trades
ETH/USDT   4h    donchian_breakout    43      37.2    1.3     0.179    7.43      -7.87    -36.97   2      no edge       
ETH/USDT   4h    bollinger_reversion  123     61.8    0.85    -0.053   -6.66     -12.6    -36.97   1      no edge       
ETH/USDT   4h    supertrend           80      25.0    1.1     0.058    3.66      -10.96   -36.97   2      no edge       
ETH/USDT   4h    ema_cross_adx        19      15.8    0.33    -0.487   -8.95     -12.59   -36.97   2      too few trades
ETH/USDT   4h    breakout_htf         14      42.9    1.89    0.576    7.93      -4.85    -36.97   2      too few trades
ETH/USDT   4h    pullback_htf         15      13.3    0.37    -0.54    -7.9      -12.25   -36.97   0      too few trades
ETH/USDT   4h    chandelier_trend     37      27.0    0.78    -0.064   -2.44     -7.15    -36.97   1      no edge       
ETH/USDT   4h    auto                 48      25.0    0.71    -0.172   -8.29     -15.04   -36.97   1      no edge       
```

## Parameters chosen per fold

- **BTC/USDT 1h ema_cross**: ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R -> -1.02%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> 3.66%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> -11.22%; ema_cross(fast=9,slow=100) stop=3.0ATR no tp -> 9.34%
- **BTC/USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> 1.64%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -2.45%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -1.91%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> 0.37%
- **BTC/USDT 1h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> 4.77%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> -8.91%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> -13.36%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -7.24%
- **BTC/USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp -> -0.92%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp -> 1.92%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R -> -1.23%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R -> 3.87%
- **BTC/USDT 1h supertrend**: supertrend(mult=3.0,trend=200) stop=2.0ATR no tp -> 7.72%; supertrend(mult=3.0,trend=200) stop=2.0ATR no tp -> 2.28%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -6.47%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -4.04%
- **BTC/USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR no tp -> -10.48%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> 7.47%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> -8.29%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp -> 21.45%
- **BTC/USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> 1.77%; breakout_htf(entry_n=20,trend=400) stop=2.0ATR tp=3.0R -> -12.55%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> -0.18%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> -4.85%
- **BTC/USDT 1h pullback_htf**: pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR no tp -> 5.5%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> 5.58%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -5.1%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> 2.66%
- **BTC/USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=3.0ATR no tp -> -0.92%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR no tp -> -1.43%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR no tp -> -16.9%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR no tp -> -8.52%
- **BTC/USDT 1h auto**: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> 4.77%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> 3.66%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> -11.22%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -4.04%
- **BTC/USDT 4h ema_cross**: ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R -> 3.78%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> 0.17%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp -> -7.76%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> 6.84%
- **BTC/USDT 4h trend_pullback**: nothing qualified -> 0.0%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> 0.02%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R -> 1.07%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R -> -1.36%
- **BTC/USDT 4h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 0.41%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> -1.11%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 1.0%; donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -0.65%
- **BTC/USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -5.95%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 2.58%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -4.22%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 0.58%
- **BTC/USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> 9.21%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -0.67%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -1.25%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -3.42%
- **BTC/USDT 4h ema_cross_adx**: nothing qualified -> 0.0%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> 0.45%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> -3.94%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR tp=3.0R -> 7.94%
- **BTC/USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 3.79%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR no tp -> -1.72%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 2.41%
- **BTC/USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR no tp -> 1.83%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -4.2%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -2.15%
- **BTC/USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> 10.49%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR no tp -> 1.23%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR no tp -> -1.23%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR no tp -> 13.63%
- **BTC/USDT 4h auto**: donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 0.41%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> -0.67%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp -> -7.76%; donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -0.65%
- **ETH/USDT 1h ema_cross**: ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> 2.63%; ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> -2.83%; ema_cross(fast=9,slow=50) stop=3.0ATR no tp -> -12.28%; ema_cross(fast=20,slow=21) stop=2.0ATR no tp -> -17.07%
- **ETH/USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -6.44%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> 0.21%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> 1.39%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> 2.71%
- **ETH/USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -2.24%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> 2.8%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -1.29%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -0.42%
- **ETH/USDT 1h bollinger_reversion**: bollinger_reversion(k=2.0,trend=200) stop=2.0ATR no tp -> 0.11%; bollinger_reversion(k=2.0,trend=200) stop=2.0ATR no tp -> 0.48%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -1.88%; bollinger_reversion(k=2.0,trend=200) stop=2.0ATR no tp -> -5.91%
- **ETH/USDT 1h supertrend**: supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R -> -11.4%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> 2.05%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -5.31%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> 0.08%
- **ETH/USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> 2.89%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> 8.71%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> -8.1%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> 21.93%
- **ETH/USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=800) stop=3.0ATR no tp -> -3.64%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R -> 15.89%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R -> -4.21%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR no tp -> 0.06%
- **ETH/USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -12.94%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR tp=3.0R -> 4.62%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R -> -1.16%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R -> -2.02%
- **ETH/USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=2.0ATR no tp -> -3.6%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> 7.7%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> -9.58%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> 5.37%
- **ETH/USDT 1h auto**: ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> 2.63%; ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> -2.83%; ema_cross(fast=9,slow=50) stop=3.0ATR no tp -> -12.28%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR no tp -> 0.06%
- **ETH/USDT 4h ema_cross**: ema_cross(fast=9,slow=21) stop=2.0ATR no tp -> -3.1%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> 15.78%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> -5.18%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> 6.72%
- **ETH/USDT 4h trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> 0.22%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -3.37%
- **ETH/USDT 4h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 3.99%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 6.48%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -2.31%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -0.68%
- **ETH/USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -1.31%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -3.47%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -3.04%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 1.05%
- **ETH/USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> 12.16%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp -> 0.74%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp -> -8.26%
- **ETH/USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> 0.85%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR no tp -> -5.45%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp -> -5.14%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp -> 0.66%
- **ETH/USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR no tp -> 8.19%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> -1.08%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 0.85%
- **ETH/USDT 4h pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R -> -7.01%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -0.96%
- **ETH/USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=2.5) stop=3.0ATR tp=3.0R -> 4.34%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR tp=3.0R -> -1.59%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp -> -3.79%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp -> -1.24%
- **ETH/USDT 4h auto**: donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 3.99%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR tp=3.0R -> -1.59%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -2.31%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp -> -8.26%
