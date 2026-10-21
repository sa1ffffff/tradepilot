# Research run 20261021_073408 UTC

365 days, 4-fold anchored walk-forward. Execution maker: maker 0.020%, taker 0.050% + 2 bps slippage, 70% assumed maker fills; expected cost 0.035%/side normal, 0.070% on stops, 0.070% round trip; entries skipped when costs exceed 20% of the risk. Risk 2.0%/trade. Perpetual swaps: long and short, isolated margin, leverage from volatility up to 5x with liquidation >= 3x the stop distance, margin <= 50% of equity, funding 0.010%/8h charged to both sides. All figures are out-of-sample (last 80% of the period).

**Read with care:** 18 strategy/market combinations were tested, so a few will pass by luck alone. Trust a CANDIDATE more if the same strategy also does well on the other symbol, survives `--execution taker`, and keeps working in a forward demo run. The `auto` rows (picking among all strategies each fold) are the best single estimate of what this research process is worth.

```
symbol     tf    strategy             trades  win%    PF      avg%     return%   maxDD%   B&H%     folds+  verdict       
BTC/USDT:USDT  15m   ema_cross            427     22.0    0.58    -0.388   -83.7     -83.7    -6.47    0      no edge       
BTC/USDT:USDT  15m   trend_pullback       69      21.7    0.64    -0.237   -15.64    -18.97   -6.47    0      no edge       
BTC/USDT:USDT  15m   donchian_breakout    253     30.8    0.85    -0.077   -29.64    -46.8    -6.47    1      no edge       
BTC/USDT:USDT  15m   bollinger_reversion  74      68.9    1.4     0.147    11.02     -6.97    -6.47    3      CANDIDATE     
BTC/USDT:USDT  15m   supertrend           305     28.5    0.81    -0.146   -47.32    -64.04   -6.47    1      no edge       
BTC/USDT:USDT  15m   ema_cross_adx        120     24.2    0.6     -0.452   -44.16    -45.83   -6.47    0      no edge       
BTC/USDT:USDT  15m   breakout_htf         382     28.8    0.86    -0.109   -47.29    -61.21   -6.47    1      no edge       
BTC/USDT:USDT  15m   pullback_htf         226     30.5    0.98    0.016    -4.29     -33.83   -6.47    2      no edge       
BTC/USDT:USDT  15m   chandelier_trend     216     27.8    0.65    -0.229   -40.68    -43.34   -6.47    0      no edge       
BTC/USDT:USDT  15m   auto                 85      49.4    0.66    -0.218   -17.93    -24.63   -6.47    2      no edge       
ETH/USDT:USDT  15m   ema_cross            460     23.0    0.84    -0.185   -63.42    -74.09   -18.75   1      no edge       
ETH/USDT:USDT  15m   trend_pullback       158     22.8    0.98    0.008    -2.61     -23.92   -18.75   2      no edge       
ETH/USDT:USDT  15m   donchian_breakout    351     29.9    0.87    -0.127   -42.93    -53.42   -18.75   0      no edge       
ETH/USDT:USDT  15m   bollinger_reversion  135     63.0    0.62    -0.225   -26.98    -30.73   -18.75   0      no edge       
ETH/USDT:USDT  15m   supertrend           354     26.3    0.83    -0.128   -50.49    -57.74   -18.75   0      no edge       
ETH/USDT:USDT  15m   ema_cross_adx        72      22.2    0.8     -0.249   -20.11    -43.14   -18.75   2      no edge       
ETH/USDT:USDT  15m   breakout_htf         195     28.2    0.9     -0.072   -21.2     -36.45   -18.75   1      no edge       
ETH/USDT:USDT  15m   pullback_htf         114     33.3    1.1     0.164    15.07     -21.78   -18.75   3      no edge       
ETH/USDT:USDT  15m   chandelier_trend     354     23.7    0.78    -0.115   -40.48    -50.75   -18.75   1      no edge       
ETH/USDT:USDT  15m   auto                 102     27.5    0.9     -0.098   -12.82    -32.62   -18.75   2      no edge       
```

## Parameters chosen per fold

- **BTC/USDT:USDT 15m ema_cross**: ema_cross(fast=20,slow=100) stop=2.0ATR tp=3.0R -> -26.03%; ema_cross(fast=9,slow=100) stop=3.0ATR no tp +shorts -> -49.05%; ema_cross(fast=20,slow=50) stop=3.0ATR no tp +shorts -> -36.68%; ema_cross(fast=20,slow=50) stop=3.0ATR no tp +shorts -> -31.68%
- **BTC/USDT:USDT 15m trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=3.0ATR tp=3.0R -> -6.66%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=3.0ATR tp=3.0R +shorts -> -2.08%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=2.0ATR tp=3.0R -> -2.49%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=3.0ATR tp=3.0R +shorts -> -5.35%
- **BTC/USDT:USDT 15m donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -11.43%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -14.48%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -23.54%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR no tp +shorts -> 21.49%
- **BTC/USDT:USDT 15m bollinger_reversion**: bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 8.08%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 3.34%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 2.85%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -3.35%
- **BTC/USDT:USDT 15m supertrend**: supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -4.11%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp +shorts -> -18.39%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp +shorts -> -44.99%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp +shorts -> 22.38%
- **BTC/USDT:USDT 15m ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> -20.1%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp +shorts -> -3.17%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp +shorts -> -19.82%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp +shorts -> -9.98%
- **BTC/USDT:USDT 15m breakout_htf**: breakout_htf(entry_n=20,trend=400) stop=2.0ATR tp=3.0R +shorts -> -11.0%; breakout_htf(entry_n=20,trend=400) stop=2.0ATR tp=3.0R +shorts -> -26.74%; breakout_htf(entry_n=20,trend=400) stop=2.0ATR no tp +shorts -> -32.16%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR no tp +shorts -> 19.17%
- **BTC/USDT:USDT 15m pullback_htf**: pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> -1.61%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 15.77%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> -25.35%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 12.55%
- **BTC/USDT:USDT 15m chandelier_trend**: chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp -> -13.48%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp -> -7.9%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp -> -14.91%; chandelier_trend(trend=200,mult=2.5) stop=2.0ATR no tp -> -12.51%
- **BTC/USDT:USDT 15m auto**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> -20.1%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 3.34%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 2.85%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -3.35%
- **ETH/USDT:USDT 15m ema_cross**: ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R +shorts -> 15.14%; ema_cross(fast=9,slow=100) stop=3.0ATR no tp +shorts -> -22.17%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R +shorts -> -39.45%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R +shorts -> -32.59%
- **ETH/USDT:USDT 15m trend_pullback**: trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> -0.71%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> 0.11%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> 1.44%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR tp=3.0R -> -3.4%
- **ETH/USDT:USDT 15m donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R +shorts -> -1.42%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R +shorts -> -25.82%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -16.23%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -6.83%
- **ETH/USDT:USDT 15m bollinger_reversion**: bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -7.8%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -3.97%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -4.15%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -13.95%
- **ETH/USDT:USDT 15m supertrend**: supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> -14.88%; supertrend(mult=2.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> -12.73%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp +shorts -> -32.13%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -1.81%
- **ETH/USDT:USDT 15m ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR no tp -> 23.82%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R -> 10.96%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R -> -19.04%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR no tp +shorts -> -28.17%
- **ETH/USDT:USDT 15m breakout_htf**: breakout_htf(entry_n=55,trend=400) stop=2.0ATR no tp +shorts -> -5.28%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> -17.08%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> 3.96%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> -3.5%
- **ETH/USDT:USDT 15m pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> 7.96%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR tp=3.0R -> -5.98%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR tp=3.0R -> 6.86%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR no tp -> 6.09%
- **ETH/USDT:USDT 15m chandelier_trend**: chandelier_trend(trend=200,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> -42.36%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R -> -1.42%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> -2.18%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> 7.09%
- **ETH/USDT:USDT 15m auto**: pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> 7.96%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR tp=3.0R -> -5.98%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R -> -19.04%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR no tp -> 6.09%
