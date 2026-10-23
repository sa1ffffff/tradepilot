# Research run 20261023_112206 UTC

1095 days, 4-fold anchored walk-forward. Execution maker: maker 0.020%, taker 0.050% + 2 bps slippage, 54% assumed maker fills; expected cost 0.043%/side normal, 0.070% on stops, 0.086% round trip; entries skipped when costs exceed 20% of the risk. Risk 2.0%/trade. Perpetual swaps: long and short, isolated margin, leverage from volatility up to 5x with liquidation >= 3x the stop distance, margin <= 50% of equity, funding 0.010%/8h charged to both sides. All figures are out-of-sample (last 80% of the period).

**Read with care:** 351 strategy/market combinations were tested, so a few will pass by luck alone. Trust a CANDIDATE more if the same strategy also does well on the other symbol, survives `--execution taker`, and keeps working in a forward demo run. The `auto` rows (picking among all strategies each fold) are the best single estimate of what this research process is worth.

```
symbol     tf    strategy             trades  win%    PF      avg%     return%   maxDD%   B&H%     folds+  verdict       
BTC/USDT:USDT  1h    ema_cross            227     24.7    0.9     -0.027   -22.05    -42.97   20.41    2      no edge       
BTC/USDT:USDT  1h    trend_pullback       70      24.3    0.79    -0.179   -12.97    -20.55   20.41    1      no edge       
BTC/USDT:USDT  1h    donchian_breakout    252     33.3    0.89    -0.099   -28.11    -37.59   20.41    2      no edge       
BTC/USDT:USDT  1h    bollinger_reversion  114     65.8    1.04    0.032    2.56      -13.22   20.41    2      no edge       
BTC/USDT:USDT  1h    supertrend           254     36.2    1.16    0.194    41.18     -28.35   20.41    3      no edge       
BTC/USDT:USDT  1h    ema_cross_adx        84      25.0    1.08    0.25     7.68      -26.25   20.41    2      no edge       
BTC/USDT:USDT  1h    breakout_htf         201     32.3    0.85    -0.133   -29.6     -39.33   20.41    1      no edge       
BTC/USDT:USDT  1h    pullback_htf         107     29.9    1.02    0.081    2.73      -26.87   20.41    2      no edge       
BTC/USDT:USDT  1h    chandelier_trend     230     29.1    0.75    -0.241   -47.13    -54.15   20.41    0      no edge       
BTC/USDT:USDT  1h    donchian_ensemble    198     27.8    1.2     0.173    28.16     -26.78   20.41    2      no edge       
BTC/USDT:USDT  1h    tsmom                198     27.8    0.75    -0.2     -41.39    -45.53   20.41    0      no edge       
BTC/USDT:USDT  1h    rsi2_reversion       227     62.1    0.71    -0.098   -20.6     -23.98   20.41    1      no edge       
BTC/USDT:USDT  1h    shock_reversal       238     52.5    0.66    -0.267   -48.85    -52.0    20.41    0      no edge       
BTC/USDT:USDT  1h    auto                 217     25.3    0.82    -0.183   -37.2     -46.04   20.41    2      no edge       
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
BTC/USDT:USDT  1d    ema_cross            20      30.0    0.68    -0.249   -5.17     -9.53    19.04    1      too few trades
BTC/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      19.04    0      too few trades
BTC/USDT:USDT  1d    donchian_breakout    11      36.4    0.55    -0.427   -4.73     -9.65    19.04    2      too few trades
BTC/USDT:USDT  1d    bollinger_reversion  21      52.4    0.67    -0.237   -5.08     -8.26    19.04    0      too few trades
BTC/USDT:USDT  1d    supertrend           20      30.0    0.59    -0.398   -8.09     -14.74   19.04    1      too few trades
BTC/USDT:USDT  1d    ema_cross_adx        0       0.0     0.0     0.0      0.0       0.0      19.04    0      too few trades
BTC/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      19.04    0      too few trades
BTC/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      19.04    0      too few trades
BTC/USDT:USDT  1d    chandelier_trend     8       50.0    4.74    1.03     8.3       -3.08    19.04    1      too few trades
BTC/USDT:USDT  1d    donchian_ensemble    21      33.3    0.93    -0.035   -1.08     -9.29    19.04    1      too few trades
BTC/USDT:USDT  1d    tsmom                13      46.2    1.2     0.13     1.49      -5.24    19.04    1      too few trades
BTC/USDT:USDT  1d    rsi2_reversion       11      72.7    0.58    -0.175   -1.96     -4.13    19.04    0      too few trades
BTC/USDT:USDT  1d    shock_reversal       5       20.0    0.16    -1.07    -5.28     -6.42    19.04    0      too few trades
BTC/USDT:USDT  1d    auto                 18      55.6    0.4     -0.407   -7.19     -10.33   19.04    1      too few trades
ETH/USDT:USDT  1h    ema_cross            380     26.8    0.95    0.016    -14.74    -37.02   -35.88   1      no edge       
ETH/USDT:USDT  1h    trend_pullback       104     19.2    0.92    -0.028   -5.25     -20.29   -35.88   2      no edge       
ETH/USDT:USDT  1h    donchian_breakout    324     31.2    1.05    0.103    22.37     -32.92   -35.88   2      no edge       
ETH/USDT:USDT  1h    bollinger_reversion  123     64.2    0.81    -0.099   -12.36    -19.28   -35.88   1      no edge       
ETH/USDT:USDT  1h    supertrend           135     29.6    0.97    0.008    -3.97     -25.19   -35.88   2      no edge       
ETH/USDT:USDT  1h    ema_cross_adx        86      27.9    1.22    0.355    20.41     -23.04   -35.88   2      no edge       
ETH/USDT:USDT  1h    breakout_htf         229     31.9    1.06    0.141    23.11     -32.07   -35.88   2      no edge       
ETH/USDT:USDT  1h    pullback_htf         89      34.8    0.75    -0.256   -22.49    -29.33   -35.88   1      no edge       
ETH/USDT:USDT  1h    chandelier_trend     371     27.8    1.01    0.018    1.91      -29.58   -35.88   3      no edge       
ETH/USDT:USDT  1h    donchian_ensemble    176     29.5    0.99    0.049    -1.11     -28.78   -35.88   3      no edge       
ETH/USDT:USDT  1h    tsmom                254     30.7    1.18    0.146    34.77     -17.7    -35.88   3      no edge       
ETH/USDT:USDT  1h    rsi2_reversion       220     63.2    0.94    -0.021   -5.99     -20.11   -35.88   1      no edge       
ETH/USDT:USDT  1h    shock_reversal       186     58.6    0.65    -0.22    -34.76    -39.43   -35.88   0      no edge       
ETH/USDT:USDT  1h    auto                 306     29.7    1.0     0.029    0.22      -31.13   -35.88   2      no edge       
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
ETH/USDT:USDT  1d    ema_cross            11      36.4    1.88    0.78     8.35      -8.53    -36.29   2      too few trades
ETH/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      -36.29   0      too few trades
ETH/USDT:USDT  1d    donchian_breakout    17      41.2    1.39    0.455    7.16      -10.89   -36.29   2      too few trades
ETH/USDT:USDT  1d    bollinger_reversion  19      47.4    0.41    -0.465   -8.63     -9.62    -36.29   0      too few trades
ETH/USDT:USDT  1d    supertrend           13      46.2    1.43    0.457    5.47      -10.14   -36.29   2      too few trades
ETH/USDT:USDT  1d    ema_cross_adx        1       100.0   inf     5.77     5.77      -1.09    -36.29   1      too few trades
ETH/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      -36.29   0      too few trades
ETH/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      -36.29   0      too few trades
ETH/USDT:USDT  1d    chandelier_trend     9       33.3    1.87    0.34     2.91      -2.82    -36.29   1      too few trades
ETH/USDT:USDT  1d    donchian_ensemble    24      29.2    1.3     0.131    2.97      -5.85    -36.29   1      too few trades
ETH/USDT:USDT  1d    tsmom                11      45.5    2.52    0.556    6.12      -3.05    -36.29   2      too few trades
ETH/USDT:USDT  1d    rsi2_reversion       0       0.0     0.0     0.0      0.0       0.0      -36.29   0      too few trades
ETH/USDT:USDT  1d    shock_reversal       8       62.5    1.61    0.339    2.66      -2.05    -36.29   1      too few trades
ETH/USDT:USDT  1d    auto                 17      41.2    1.39    0.455    7.16      -10.89   -36.29   2      too few trades
SOL/USDT:USDT  1h    ema_cross            545     32.3    1.07    0.107    52.68     -31.39   -37.43   3      no edge       
SOL/USDT:USDT  1h    trend_pullback       82      23.2    1.18    0.183    13.14     -16.79   -37.43   2      no edge       
SOL/USDT:USDT  1h    donchian_breakout    261     30.3    0.91    -0.068   -24.67    -43.05   -37.43   0      no edge       
SOL/USDT:USDT  1h    bollinger_reversion  180     61.1    0.81    -0.109   -19.13    -32.25   -37.43   1      no edge       
SOL/USDT:USDT  1h    supertrend           273     35.2    1.09    0.11     24.63     -17.9    -37.43   3      no edge       
SOL/USDT:USDT  1h    ema_cross_adx        66      36.4    1.2     0.239    14.19     -13.06   -37.43   2      no edge       
SOL/USDT:USDT  1h    breakout_htf         236     36.9    1.15    0.219    50.0      -29.47   -37.43   4      no edge       
SOL/USDT:USDT  1h    pullback_htf         124     26.6    0.62    -0.424   -42.89    -44.37   -37.43   1      no edge       
SOL/USDT:USDT  1h    chandelier_trend     197     28.9    1.31    0.409    76.77     -45.23   -37.43   3      CANDIDATE     
SOL/USDT:USDT  1h    donchian_ensemble    245     27.8    1.13    0.082    16.91     -26.36   -37.43   2      no edge       
SOL/USDT:USDT  1h    tsmom                241     32.4    1.01    0.026    1.18      -23.11   -37.43   2      no edge       
SOL/USDT:USDT  1h    rsi2_reversion       254     57.9    0.87    -0.036   -9.36     -17.27   -37.43   0      no edge       
SOL/USDT:USDT  1h    shock_reversal       211     56.4    0.86    -0.09    -19.58    -29.36   -37.43   1      no edge       
SOL/USDT:USDT  1h    auto                 516     34.7    1.03    0.057    17.64     -31.39   -37.43   2      no edge       
SOL/USDT:USDT  4h    ema_cross            88      33.0    1.28    0.313    27.19     -15.3    -37.29   3      CANDIDATE     
SOL/USDT:USDT  4h    trend_pullback       50      22.0    1.09    0.099    3.5       -17.78   -37.29   1      no edge       
SOL/USDT:USDT  4h    donchian_breakout    75      36.0    1.55    0.409    30.78     -14.36   -37.29   3      CANDIDATE     
SOL/USDT:USDT  4h    bollinger_reversion  42      64.3    1.3     0.14     5.72      -6.02    -37.29   2      no edge       
SOL/USDT:USDT  4h    supertrend           54      33.3    0.96    -0.008   -2.27     -21.72   -37.29   2      no edge       
SOL/USDT:USDT  4h    ema_cross_adx        37      37.8    1.26    0.37     12.64     -14.63   -37.29   2      no edge       
SOL/USDT:USDT  4h    breakout_htf         66      27.3    1.02    0.072    1.58      -18.8    -37.29   2      no edge       
SOL/USDT:USDT  4h    pullback_htf         38      31.6    0.85    -0.17    -7.78     -18.18   -37.29   1      no edge       
SOL/USDT:USDT  4h    chandelier_trend     92      32.6    0.96    -0.009   -2.19     -14.03   -37.29   2      no edge       
SOL/USDT:USDT  4h    donchian_ensemble    65      33.8    1.15    0.163    7.96      -21.84   -37.29   3      no edge       
SOL/USDT:USDT  4h    tsmom                63      42.9    1.79    0.35     22.99     -6.73    -37.29   4      CANDIDATE     
SOL/USDT:USDT  4h    rsi2_reversion       148     61.5    0.81    -0.062   -9.27     -11.62   -37.29   1      no edge       
SOL/USDT:USDT  4h    shock_reversal       93      60.2    1.17    0.115    10.07     -12.87   -37.29   3      no edge       
SOL/USDT:USDT  4h    auto                 57      47.4    1.29    0.198    10.85     -11.79   -37.29   3      CANDIDATE     
SOL/USDT:USDT  1d    ema_cross            25      32.0    0.67    -0.209   -5.38     -13.79   -37.92   0      too few trades
SOL/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      -37.92   0      too few trades
SOL/USDT:USDT  1d    donchian_breakout    10      20.0    0.58    -0.439   -4.56     -11.01   -37.92   0      too few trades
SOL/USDT:USDT  1d    bollinger_reversion  18      66.7    0.85    -0.091   -1.85     -7.49    -37.92   1      too few trades
SOL/USDT:USDT  1d    supertrend           22      36.4    0.78    -0.143   -3.42     -11.07   -37.92   1      too few trades
SOL/USDT:USDT  1d    ema_cross_adx        1       0.0     0.0     -0.837   -0.84     -0.84    -37.92   0      too few trades
SOL/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      -37.92   0      too few trades
SOL/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      -37.92   0      too few trades
SOL/USDT:USDT  1d    chandelier_trend     12      16.7    0.3     -0.292   -3.46     -5.08    -37.92   0      too few trades
SOL/USDT:USDT  1d    donchian_ensemble    32      25.0    0.93    -0.022   -0.96     -8.65    -37.92   2      no edge       
SOL/USDT:USDT  1d    tsmom                7       42.9    0.63    -0.324   -2.35     -6.41    -37.92   0      too few trades
SOL/USDT:USDT  1d    rsi2_reversion       0       0.0     0.0     0.0      0.0       0.0      -37.92   0      too few trades
SOL/USDT:USDT  1d    shock_reversal       0       0.0     0.0     0.0      0.0       0.0      -37.92   0      too few trades
SOL/USDT:USDT  1d    auto                 26      26.9    0.57    -0.244   -6.39     -13.59   -37.92   0      too few trades
XRP/USDT:USDT  1h    ema_cross            275     28.4    1.15    0.194    53.62     -26.51   153.4    3      no edge       
XRP/USDT:USDT  1h    trend_pullback       81      24.7    1.09    0.1      6.0       -16.48   153.4    1      no edge       
XRP/USDT:USDT  1h    donchian_breakout    242     35.1    1.29    0.451    129.81    -33.19   153.4    4      CANDIDATE     
XRP/USDT:USDT  1h    bollinger_reversion  135     57.0    0.75    -0.171   -21.73    -23.78   153.4    1      no edge       
XRP/USDT:USDT  1h    supertrend           354     35.0    0.91    -0.071   -31.31    -48.23   153.4    2      no edge       
XRP/USDT:USDT  1h    ema_cross_adx        131     26.7    0.92    -0.063   -12.7     -28.18   153.4    1      no edge       
XRP/USDT:USDT  1h    breakout_htf         288     35.4    1.29    0.357    135.49    -24.22   153.4    4      CANDIDATE     
XRP/USDT:USDT  1h    pullback_htf         139     28.8    0.83    -0.214   -30.54    -38.55   153.4    1      no edge       
XRP/USDT:USDT  1h    chandelier_trend     162     27.2    0.54    -0.297   -39.43    -40.46   153.4    0      no edge       
XRP/USDT:USDT  1h    donchian_ensemble    171     26.9    1.73    0.547    112.09    -25.76   153.4    4      CANDIDATE     
XRP/USDT:USDT  1h    tsmom                79      24.1    1.31    0.447    29.36     -32.38   153.4    3      CANDIDATE     
XRP/USDT:USDT  1h    rsi2_reversion       376     59.6    0.76    -0.075   -25.24    -30.67   153.4    1      no edge       
XRP/USDT:USDT  1h    shock_reversal       278     57.6    0.72    -0.167   -38.77    -40.13   153.4    0      no edge       
XRP/USDT:USDT  1h    auto                 200     52.5    1.01    0.023    1.12      -24.2    153.4    1      no edge       
XRP/USDT:USDT  4h    ema_cross            90      27.8    1.17    0.22     14.06     -22.1    154.04   3      no edge       
XRP/USDT:USDT  4h    trend_pullback       40      15.0    0.41    -0.513   -18.91    -22.29   154.04   0      no edge       
XRP/USDT:USDT  4h    donchian_breakout    94      37.2    1.49    0.676    78.24     -18.33   154.04   4      CANDIDATE     
XRP/USDT:USDT  4h    bollinger_reversion  53      64.2    0.99    0.007    -0.2      -9.38    154.04   2      no edge       
XRP/USDT:USDT  4h    supertrend           90      33.3    1.01    0.048    0.48      -21.11   154.04   2      no edge       
XRP/USDT:USDT  4h    ema_cross_adx        36      36.1    0.97    -0.0     -1.35     -16.85   154.04   1      no edge       
XRP/USDT:USDT  4h    breakout_htf         29      37.9    1.57    0.767    22.35     -14.38   154.04   3      too few trades
XRP/USDT:USDT  4h    pullback_htf         24      25.0    0.74    -0.345   -8.91     -15.74   154.04   1      too few trades
XRP/USDT:USDT  4h    chandelier_trend     96      33.3    1.52    0.32     32.77     -11.8    154.04   4      CANDIDATE     
XRP/USDT:USDT  4h    donchian_ensemble    42      26.2    2.2     1.559    59.82     -20.49   154.04   3      CANDIDATE     
XRP/USDT:USDT  4h    tsmom                37      35.1    2.38    1.538    52.22     -15.77   154.04   2      no edge       
XRP/USDT:USDT  4h    rsi2_reversion       74      56.8    0.64    -0.16    -11.48    -11.8    154.04   1      no edge       
XRP/USDT:USDT  4h    shock_reversal       66      62.1    0.94    -0.022   -2.01     -18.95   154.04   2      no edge       
XRP/USDT:USDT  4h    auto                 77      54.5    0.93    -0.025   -3.36     -24.21   154.04   2      no edge       
XRP/USDT:USDT  1d    ema_cross            16      31.2    0.85    -0.144   -2.78     -12.29   152.3    1      too few trades
XRP/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      152.3    0      too few trades
XRP/USDT:USDT  1d    donchian_breakout    7       28.6    1.78    0.765    5.08      -7.96    152.3    2      too few trades
XRP/USDT:USDT  1d    bollinger_reversion  18      77.8    2.57    0.464    8.54      -2.87    152.3    3      too few trades
XRP/USDT:USDT  1d    supertrend           26      26.9    0.83    -0.124   -3.81     -11.09   152.3    0      too few trades
XRP/USDT:USDT  1d    ema_cross_adx        0       0.0     0.0     0.0      0.0       0.0      152.3    0      too few trades
XRP/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      152.3    0      too few trades
XRP/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      152.3    0      too few trades
XRP/USDT:USDT  1d    chandelier_trend     7       42.9    1.29    0.106    0.7       -1.33    152.3    1      too few trades
XRP/USDT:USDT  1d    donchian_ensemble    20      20.0    0.49    -0.216   -4.32     -7.68    152.3    1      too few trades
XRP/USDT:USDT  1d    tsmom                13      38.5    0.47    -0.416   -5.39     -6.43    152.3    0      too few trades
XRP/USDT:USDT  1d    rsi2_reversion       0       0.0     0.0     0.0      0.0       0.0      152.3    0      too few trades
XRP/USDT:USDT  1d    shock_reversal       16      75.0    1.54    0.306    4.81      -6.54    152.3    2      too few trades
XRP/USDT:USDT  1d    auto                 7       28.6    1.78    0.765    5.08      -7.96    152.3    2      too few trades
BNB/USDT:USDT  1h    ema_cross            368     29.1    0.85    -0.098   -36.95    -51.24   25.6     1      no edge       
BNB/USDT:USDT  1h    trend_pullback       71      11.3    0.38    -0.661   -38.21    -44.65   25.6     0      no edge       
BNB/USDT:USDT  1h    donchian_breakout    208     32.2    1.0     0.039    0.0       -39.99   25.6     2      no edge       
BNB/USDT:USDT  1h    bollinger_reversion  136     57.4    0.63    -0.269   -31.66    -33.52   25.6     0      no edge       
BNB/USDT:USDT  1h    supertrend           237     32.5    0.91    -0.059   -19.47    -47.48   25.6     2      no edge       
BNB/USDT:USDT  1h    ema_cross_adx        103     35.0    0.95    -0.026   -7.22     -31.55   25.6     1      no edge       
BNB/USDT:USDT  1h    breakout_htf         192     30.7    0.94    -0.033   -12.59    -41.73   25.6     1      no edge       
BNB/USDT:USDT  1h    pullback_htf         109     36.7    1.13    0.177    17.09     -20.16   25.6     2      no edge       
BNB/USDT:USDT  1h    chandelier_trend     225     32.0    0.84    -0.095   -24.05    -47.27   25.6     1      no edge       
BNB/USDT:USDT  1h    donchian_ensemble    133     29.3    1.02    0.078    3.22      -32.02   25.6     2      no edge       
BNB/USDT:USDT  1h    tsmom                92      38.0    1.42    0.409    38.26     -24.57   25.6     4      CANDIDATE     
BNB/USDT:USDT  1h    rsi2_reversion       353     59.5    0.77    -0.082   -26.11    -27.92   25.6     1      no edge       
BNB/USDT:USDT  1h    shock_reversal       126     59.5    0.82    -0.099   -13.01    -26.47   25.6     1      no edge       
BNB/USDT:USDT  1h    auto                 112     40.2    1.01    0.039    0.52      -24.57   25.6     3      no edge       
BNB/USDT:USDT  4h    ema_cross            58      37.9    1.29    0.331    18.62     -15.97   25.35    3      CANDIDATE     
BNB/USDT:USDT  4h    trend_pullback       38      23.7    1.33    0.22     7.61      -10.4    25.35    2      no edge       
BNB/USDT:USDT  4h    donchian_breakout    61      41.0    1.38    0.426    26.11     -14.97   25.35    4      CANDIDATE     
BNB/USDT:USDT  4h    bollinger_reversion  97      57.7    0.73    -0.197   -18.39    -22.23   25.35    1      no edge       
BNB/USDT:USDT  4h    supertrend           64      37.5    0.95    -0.024   -3.91     -18.16   25.35    2      no edge       
BNB/USDT:USDT  4h    ema_cross_adx        31      29.0    1.08    0.123    2.66      -14.92   25.35    2      no edge       
BNB/USDT:USDT  4h    breakout_htf         34      26.5    1.3     0.4      12.08     -14.09   25.35    2      no edge       
BNB/USDT:USDT  4h    pullback_htf         12      41.7    0.89    -0.113   -1.72     -10.13   25.35    1      too few trades
BNB/USDT:USDT  4h    chandelier_trend     63      38.1    1.02    0.024    0.79      -14.71   25.35    2      no edge       
BNB/USDT:USDT  4h    donchian_ensemble    67      34.3    1.04    0.067    2.23      -28.28   25.35    2      no edge       
BNB/USDT:USDT  4h    tsmom                70      35.7    1.22    0.248    14.56     -26.12   25.35    2      no edge       
BNB/USDT:USDT  4h    rsi2_reversion       121     62.0    0.53    -0.264   -27.96    -29.23   25.35    1      no edge       
BNB/USDT:USDT  4h    shock_reversal       86      65.1    0.75    -0.13    -11.17    -15.35   25.35    2      no edge       
BNB/USDT:USDT  4h    auto                 61      39.3    1.11    0.127    6.2       -15.97   25.35    3      no edge       
BNB/USDT:USDT  1d    ema_cross            11      45.5    1.82    0.513    5.42      -5.11    22.83    3      too few trades
BNB/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      22.83    0      too few trades
BNB/USDT:USDT  1d    donchian_breakout    12      50.0    2.45    1.243    15.23     -8.85    22.83    3      too few trades
BNB/USDT:USDT  1d    bollinger_reversion  19      47.4    0.58    -0.246   -4.68     -6.57    22.83    0      too few trades
BNB/USDT:USDT  1d    supertrend           16      25.0    1.32    0.24     3.46      -9.71    22.83    2      too few trades
BNB/USDT:USDT  1d    ema_cross_adx        0       0.0     0.0     0.0      0.0       0.0      22.83    0      too few trades
BNB/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      22.83    0      too few trades
BNB/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      22.83    0      too few trades
BNB/USDT:USDT  1d    chandelier_trend     11      27.3    0.55    -0.427   -4.84     -6.99    22.83    0      too few trades
BNB/USDT:USDT  1d    donchian_ensemble    22      13.6    0.79    -0.075   -1.76     -5.5     22.83    1      too few trades
BNB/USDT:USDT  1d    tsmom                14      35.7    0.84    -0.101   -1.61     -12.56   22.83    1      too few trades
BNB/USDT:USDT  1d    rsi2_reversion       0       0.0     0.0     0.0      0.0       0.0      22.83    0      too few trades
BNB/USDT:USDT  1d    shock_reversal       2       100.0   inf     1.592    3.21      -0.34    22.83    1      too few trades
BNB/USDT:USDT  1d    auto                 15      33.3    1.39    0.243    3.42      -7.27    22.83    2      too few trades
DOGE/USDT:USDT  1h    ema_cross            253     28.9    0.89    -0.129   -34.62    -57.28   -49.74   2      no edge       
DOGE/USDT:USDT  1h    trend_pullback       115     26.1    0.76    -0.217   -23.96    -32.16   -49.74   0      no edge       
DOGE/USDT:USDT  1h    donchian_breakout    379     36.1    1.04    0.076    20.01     -47.16   -49.74   2      no edge       
DOGE/USDT:USDT  1h    bollinger_reversion  49      61.2    0.88    -0.051   -2.78     -9.36    -49.74   2      no edge       
DOGE/USDT:USDT  1h    supertrend           400     30.2    0.88    -0.118   -47.02    -64.85   -49.74   1      no edge       
DOGE/USDT:USDT  1h    ema_cross_adx        130     29.2    0.78    -0.255   -31.85    -39.66   -49.74   1      no edge       
DOGE/USDT:USDT  1h    breakout_htf         181     34.8    1.19    0.262    48.84     -33.81   -49.74   3      no edge       
DOGE/USDT:USDT  1h    pullback_htf         156     34.6    1.0     0.039    -0.63     -26.8    -49.74   2      no edge       
DOGE/USDT:USDT  1h    chandelier_trend     211     26.1    0.63    -0.242   -41.63    -43.27   -49.74   0      no edge       
DOGE/USDT:USDT  1h    donchian_ensemble    343     25.9    1.05    0.063    10.61     -39.49   -49.74   2      no edge       
DOGE/USDT:USDT  1h    tsmom                249     28.9    1.41    0.292    85.67     -28.2    -49.74   3      CANDIDATE     
DOGE/USDT:USDT  1h    rsi2_reversion       158     61.4    1.04    0.013    1.73      -8.91    -49.74   1      no edge       
DOGE/USDT:USDT  1h    shock_reversal       133     54.9    0.66    -0.194   -23.62    -27.43   -49.74   1      no edge       
DOGE/USDT:USDT  1h    auto                 105     42.9    0.8     -0.132   -14.83    -29.74   -49.74   1      no edge       
DOGE/USDT:USDT  4h    ema_cross            54      37.0    1.65    0.822    50.52     -13.81   -49.8    3      CANDIDATE     
DOGE/USDT:USDT  4h    trend_pullback       47      29.8    1.5     0.307    14.23     -8.99    -49.8    2      no edge       
DOGE/USDT:USDT  4h    donchian_breakout    81      33.3    1.15    0.222    15.33     -25.01   -49.8    2      no edge       
DOGE/USDT:USDT  4h    bollinger_reversion  77      48.1    0.72    -0.245   -18.24    -31.34   -49.8    2      no edge       
DOGE/USDT:USDT  4h    supertrend           45      40.0    2.17    1.616    93.36     -11.3    -49.8    3      CANDIDATE     
DOGE/USDT:USDT  4h    ema_cross_adx        35      37.1    1.3     0.377    12.33     -10.79   -49.8    2      no edge       
DOGE/USDT:USDT  4h    breakout_htf         80      33.8    1.18    0.285    20.4      -21.18   -49.8    2      no edge       
DOGE/USDT:USDT  4h    pullback_htf         33      30.3    0.76    -0.297   -10.7     -16.59   -49.8    2      no edge       
DOGE/USDT:USDT  4h    chandelier_trend     52      42.3    1.5     0.281    14.5      -11.67   -49.8    3      CANDIDATE     
DOGE/USDT:USDT  4h    donchian_ensemble    44      29.5    2.36    1.348    58.91     -17.23   -49.8    2      no edge       
DOGE/USDT:USDT  4h    tsmom                60      31.7    1.44    0.335    19.69     -22.6    -49.8    3      CANDIDATE     
DOGE/USDT:USDT  4h    rsi2_reversion       60      55.0    0.52    -0.167   -9.71     -12.1    -49.8    0      no edge       
DOGE/USDT:USDT  4h    shock_reversal       61      70.5    1.18    0.101    5.75      -10.78   -49.8    3      no edge       
DOGE/USDT:USDT  4h    auto                 42      42.9    1.53    0.594    25.48     -11.3    -49.8    2      no edge       
DOGE/USDT:USDT  1d    ema_cross            21      38.1    0.77    -0.177   -3.93     -14.13   -50.6    1      too few trades
DOGE/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      -50.6    0      too few trades
DOGE/USDT:USDT  1d    donchian_breakout    9       33.3    1.61    0.559    4.74      -4.61    -50.6    2      too few trades
DOGE/USDT:USDT  1d    bollinger_reversion  20      50.0    0.41    -0.449   -8.75     -9.27    -50.6    0      too few trades
DOGE/USDT:USDT  1d    supertrend           17      35.3    0.54    -0.325   -5.53     -8.17    -50.6    0      too few trades
DOGE/USDT:USDT  1d    ema_cross_adx        0       0.0     0.0     0.0      0.0       0.0      -50.6    0      too few trades
DOGE/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      -50.6    0      too few trades
DOGE/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      -50.6    0      too few trades
DOGE/USDT:USDT  1d    chandelier_trend     11      45.5    2.28    0.566    6.17      -3.6     -50.6    2      too few trades
DOGE/USDT:USDT  1d    donchian_ensemble    16      25.0    0.57    -0.29    -4.65     -9.87    -50.6    1      too few trades
DOGE/USDT:USDT  1d    tsmom                11      45.5    0.68    -0.182   -2.07     -4.3     -50.6    0      too few trades
DOGE/USDT:USDT  1d    rsi2_reversion       0       0.0     0.0     0.0      0.0       0.0      -50.6    0      too few trades
DOGE/USDT:USDT  1d    shock_reversal       3       66.7    0.87    -0.077   -0.26     -2.15    -50.6    0      too few trades
DOGE/USDT:USDT  1d    auto                 9       33.3    1.61    0.559    4.74      -4.61    -50.6    2      too few trades
ADA/USDT:USDT  1h    ema_cross            292     30.5    1.02    0.087    9.26      -41.19   -51.96   4      no edge       
ADA/USDT:USDT  1h    trend_pullback       102     20.6    0.66    -0.212   -20.16    -20.16   -51.96   0      no edge       
ADA/USDT:USDT  1h    donchian_breakout    183     33.9    1.18    0.304    58.98     -26.4    -51.96   2      no edge       
ADA/USDT:USDT  1h    bollinger_reversion  56      58.9    0.97    -0.007   -0.81     -8.55    -51.96   2      no edge       
ADA/USDT:USDT  1h    supertrend           369     34.1    0.95    -0.015   -18.3     -58.24   -51.96   2      no edge       
ADA/USDT:USDT  1h    ema_cross_adx        147     32.0    1.02    0.086    4.28      -35.84   -51.96   2      no edge       
ADA/USDT:USDT  1h    breakout_htf         117     37.6    1.59    0.988    166.64    -21.7    -51.96   4      CANDIDATE     
ADA/USDT:USDT  1h    pullback_htf         84      33.3    0.99    0.02     -1.41     -16.55   -51.96   2      no edge       
ADA/USDT:USDT  1h    chandelier_trend     231     24.7    0.84    -0.084   -22.59    -37.42   -51.96   1      no edge       
ADA/USDT:USDT  1h    donchian_ensemble    249     29.7    1.11    0.105    18.95     -31.29   -51.96   2      no edge       
ADA/USDT:USDT  1h    tsmom                77      33.8    1.18    0.212    12.87     -25.19   -51.96   2      no edge       
ADA/USDT:USDT  1h    rsi2_reversion       773     62.4    0.93    -0.025   -21.88    -35.6    -51.96   0      no edge       
ADA/USDT:USDT  1h    shock_reversal       113     48.7    0.51    -0.369   -34.88    -37.06   -51.96   0      no edge       
ADA/USDT:USDT  1h    auto                 180     29.4    1.06    0.111    12.01     -35.76   -51.96   3      no edge       
ADA/USDT:USDT  4h    ema_cross            103     27.2    0.93    -0.029   -8.7      -37.24   -51.83   1      no edge       
ADA/USDT:USDT  4h    trend_pullback       66      22.7    0.82    -0.131   -9.99     -22.82   -51.83   1      no edge       
ADA/USDT:USDT  4h    donchian_breakout    75      33.3    1.21    0.245    16.55     -13.26   -51.83   4      CANDIDATE     
ADA/USDT:USDT  4h    bollinger_reversion  64      60.9    0.9     -0.064   -4.88     -15.22   -51.83   0      no edge       
ADA/USDT:USDT  4h    supertrend           73      43.8    2.15    1.06     106.76    -12.38   -51.83   4      CANDIDATE     
ADA/USDT:USDT  4h    ema_cross_adx        45      28.9    1.2     0.363    12.65     -23.14   -51.83   2      no edge       
ADA/USDT:USDT  4h    breakout_htf         44      31.8    0.79    -0.221   -10.72    -14.92   -51.83   0      no edge       
ADA/USDT:USDT  4h    pullback_htf         35      25.7    0.85    -0.165   -7.04     -13.43   -51.83   1      no edge       
ADA/USDT:USDT  4h    chandelier_trend     96      41.7    1.67    0.192    19.47     -8.62    -51.83   3      CANDIDATE     
ADA/USDT:USDT  4h    donchian_ensemble    151     27.8    1.11    0.125    11.15     -29.42   -51.83   2      no edge       
ADA/USDT:USDT  4h    tsmom                63      30.2    0.98    0.037    -1.02     -23.23   -51.83   1      no edge       
ADA/USDT:USDT  4h    rsi2_reversion       78      59.0    1.08    0.022    1.54      -4.9     -51.83   3      no edge       
ADA/USDT:USDT  4h    shock_reversal       41      58.5    0.79    -0.145   -6.26     -20.93   -51.83   3      no edge       
ADA/USDT:USDT  4h    auto                 70      58.6    1.69    0.25     18.01     -9.25    -51.83   4      CANDIDATE     
ADA/USDT:USDT  1d    ema_cross            14      28.6    0.53    -0.552   -7.8      -12.64   -52.54   1      too few trades
ADA/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      -52.54   0      too few trades
ADA/USDT:USDT  1d    donchian_breakout    11      9.1     0.43    -0.691   -7.57     -9.9     -52.54   1      too few trades
ADA/USDT:USDT  1d    bollinger_reversion  35      68.6    1.45    0.294    10.12     -6.87    -52.54   3      CANDIDATE     
ADA/USDT:USDT  1d    supertrend           23      30.4    0.3     -0.831   -17.75    -18.19   -52.54   0      too few trades
ADA/USDT:USDT  1d    ema_cross_adx        0       0.0     0.0     0.0      0.0       0.0      -52.54   0      too few trades
ADA/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      -52.54   0      too few trades
ADA/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      -52.54   0      too few trades
ADA/USDT:USDT  1d    chandelier_trend     10      50.0    7.14    0.643    6.45      -1.23    -52.54   1      too few trades
ADA/USDT:USDT  1d    donchian_ensemble    23      17.4    0.14    -0.526   -11.49    -11.62   -52.54   0      too few trades
ADA/USDT:USDT  1d    tsmom                21      23.8    0.45    -0.455   -9.31     -12.48   -52.54   1      too few trades
ADA/USDT:USDT  1d    rsi2_reversion       0       0.0     0.0     0.0      0.0       0.0      -52.54   0      too few trades
ADA/USDT:USDT  1d    shock_reversal       12      91.7    4.63    0.664    8.19      -2.09    -52.54   3      too few trades
ADA/USDT:USDT  1d    auto                 22      45.5    0.79    -0.158   -3.78     -9.9     -52.54   2      too few trades
AVAX/USDT:USDT  1h    ema_cross            372     25.8    1.03    0.102    24.28     -70.72   -74.9    3      no edge       
AVAX/USDT:USDT  1h    trend_pullback       78      19.2    0.78    -0.132   -10.62    -17.28   -74.9    1      no edge       
AVAX/USDT:USDT  1h    donchian_breakout    457     36.3    1.02    0.068    17.33     -58.19   -74.9    3      no edge       
AVAX/USDT:USDT  1h    bollinger_reversion  104     61.5    0.74    -0.144   -14.59    -19.68   -74.9    1      no edge       
AVAX/USDT:USDT  1h    supertrend           493     33.9    0.93    -0.057   -37.91    -73.03   -74.9    2      no edge       
AVAX/USDT:USDT  1h    ema_cross_adx        166     27.7    0.85    -0.189   -31.36    -53.67   -74.9    2      no edge       
AVAX/USDT:USDT  1h    breakout_htf         281     35.6    1.08    0.174    44.63     -42.16   -74.9    3      no edge       
AVAX/USDT:USDT  1h    pullback_htf         173     31.2    0.91    -0.076   -18.08    -36.05   -74.9    2      no edge       
AVAX/USDT:USDT  1h    chandelier_trend     486     22.2    0.86    -0.101   -44.8     -52.59   -74.9    2      no edge       
AVAX/USDT:USDT  1h    donchian_ensemble    275     30.2    1.01    0.072    3.13      -53.95   -74.9    3      no edge       
AVAX/USDT:USDT  1h    tsmom                464     34.1    1.0     0.014    -1.23     -38.45   -74.9    3      no edge       
AVAX/USDT:USDT  1h    rsi2_reversion       525     60.8    0.8     -0.07    -32.02    -34.52   -74.9    0      no edge       
AVAX/USDT:USDT  1h    shock_reversal       151     54.3    0.61    -0.24    -31.26    -34.22   -74.9    1      no edge       
AVAX/USDT:USDT  1h    auto                 361     25.5    0.98    -0.002   -12.58    -70.72   -74.9    3      no edge       
AVAX/USDT:USDT  4h    ema_cross            226     26.1    0.83    -0.204   -41.03    -60.2    -74.66   2      no edge       
AVAX/USDT:USDT  4h    trend_pullback       71      26.8    1.2     0.249    15.78     -17.41   -74.66   2      no edge       
AVAX/USDT:USDT  4h    donchian_breakout    155     31.6    0.88    -0.111   -19.2     -35.61   -74.66   1      no edge       
AVAX/USDT:USDT  4h    bollinger_reversion  71      62.0    1.01    0.018    0.46      -17.6    -74.66   3      no edge       
AVAX/USDT:USDT  4h    supertrend           83      38.6    1.38    0.445    39.39     -20.99   -74.66   3      CANDIDATE     
AVAX/USDT:USDT  4h    ema_cross_adx        29      27.6    0.74    -0.271   -8.55     -19.62   -74.66   2      too few trades
AVAX/USDT:USDT  4h    breakout_htf         16      31.2    1.49    0.616    9.09      -7.46    -74.66   2      too few trades
AVAX/USDT:USDT  4h    pullback_htf         34      32.4    1.01    0.044    0.24      -12.08   -74.66   1      no edge       
AVAX/USDT:USDT  4h    chandelier_trend     127     29.9    0.94    -0.034   -7.0      -35.08   -74.66   2      no edge       
AVAX/USDT:USDT  4h    donchian_ensemble    196     24.0    0.92    -0.029   -6.9      -25.12   -74.66   2      no edge       
AVAX/USDT:USDT  4h    tsmom                80      33.8    1.33    0.215    16.24     -17.3    -74.66   3      CANDIDATE     
AVAX/USDT:USDT  4h    rsi2_reversion       62      56.5    0.64    -0.197   -11.9     -17.79   -74.66   1      no edge       
AVAX/USDT:USDT  4h    shock_reversal       42      69.0    1.28    0.123    5.01      -6.07    -74.66   3      CANDIDATE     
AVAX/USDT:USDT  4h    auto                 125     36.0    0.99    0.015    -1.61     -20.99   -74.66   2      no edge       
AVAX/USDT:USDT  1d    ema_cross            13      30.8    1.75    0.653    8.2       -7.98    -74.65   2      too few trades
AVAX/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      -74.65   0      too few trades
AVAX/USDT:USDT  1d    donchian_breakout    15      20.0    0.87    -0.111   -2.18     -10.44   -74.65   1      too few trades
AVAX/USDT:USDT  1d    bollinger_reversion  24      54.2    0.69    -0.265   -6.48     -12.31   -74.65   1      too few trades
AVAX/USDT:USDT  1d    supertrend           23      39.1    1.17    0.141    2.76      -5.89    -74.65   2      too few trades
AVAX/USDT:USDT  1d    ema_cross_adx        0       0.0     0.0     0.0      0.0       0.0      -74.65   0      too few trades
AVAX/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      -74.65   0      too few trades
AVAX/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      -74.65   0      too few trades
AVAX/USDT:USDT  1d    chandelier_trend     4       25.0    4.11    1.131    4.44      -1.44    -74.65   1      too few trades
AVAX/USDT:USDT  1d    donchian_ensemble    25      36.0    1.61    0.201    4.96      -4.69    -74.65   2      too few trades
AVAX/USDT:USDT  1d    tsmom                6       50.0    0.84    -0.092   -0.6      -5.13    -74.65   1      too few trades
AVAX/USDT:USDT  1d    rsi2_reversion       9       55.6    0.55    -0.201   -1.82     -2.79    -74.65   0      too few trades
AVAX/USDT:USDT  1d    shock_reversal       5       40.0    0.68    -0.257   -1.34     -4.33    -74.65   0      too few trades
AVAX/USDT:USDT  1d    auto                 14      35.7    1.72    0.773    10.54     -7.98    -74.65   2      too few trades
LTC/USDT:USDT  1h    ema_cross            188     26.1    0.65    -0.463   -60.72    -69.1    -29.04   1      no edge       
LTC/USDT:USDT  1h    trend_pullback       82      15.9    0.63    -0.32    -24.4     -27.79   -29.04   0      no edge       
LTC/USDT:USDT  1h    donchian_breakout    375     30.4    0.86    -0.155   -51.15    -66.05   -29.04   1      no edge       
LTC/USDT:USDT  1h    bollinger_reversion  316     57.9    0.7     -0.203   -49.16    -53.45   -29.04   1      no edge       
LTC/USDT:USDT  1h    supertrend           237     31.2    0.77    -0.22    -45.23    -49.46   -29.04   0      no edge       
LTC/USDT:USDT  1h    ema_cross_adx        59      39.0    1.15    0.22     10.7      -21.55   -29.04   2      no edge       
LTC/USDT:USDT  1h    breakout_htf         259     31.7    0.9     -0.082   -26.81    -43.84   -29.04   1      no edge       
LTC/USDT:USDT  1h    pullback_htf         118     31.4    1.02    0.073    3.37      -20.4    -29.04   2      no edge       
LTC/USDT:USDT  1h    chandelier_trend     202     24.8    0.59    -0.335   -51.14    -52.5    -29.04   0      no edge       
LTC/USDT:USDT  1h    donchian_ensemble    189     26.5    0.9     -0.05    -14.74    -44.36   -29.04   2      no edge       
LTC/USDT:USDT  1h    tsmom                85      34.1    0.93    -0.036   -5.84     -32.58   -29.04   3      no edge       
LTC/USDT:USDT  1h    rsi2_reversion       376     58.5    0.79    -0.069   -24.13    -31.8    -29.04   2      no edge       
LTC/USDT:USDT  1h    shock_reversal       131     52.7    0.77    -0.168   -21.38    -32.44   -29.04   1      no edge       
LTC/USDT:USDT  1h    auto                 219     44.3    0.7     -0.246   -44.18    -56.94   -29.04   0      no edge       
LTC/USDT:USDT  4h    ema_cross            94      26.6    0.96    -0.005   -4.21     -29.9    -28.59   2      no edge       
LTC/USDT:USDT  4h    trend_pullback       33      12.1    0.58    -0.333   -10.99    -11.84   -28.59   1      no edge       
LTC/USDT:USDT  4h    donchian_breakout    70      28.6    0.77    -0.235   -17.55    -30.13   -28.59   1      no edge       
LTC/USDT:USDT  4h    bollinger_reversion  72      70.8    1.42    0.209    15.48     -7.65    -28.59   3      CANDIDATE     
LTC/USDT:USDT  4h    supertrend           44      38.6    1.52    0.415    18.2      -14.3    -28.59   3      CANDIDATE     
LTC/USDT:USDT  4h    ema_cross_adx        32      18.8    0.5     -0.63    -19.0     -27.67   -28.59   1      no edge       
LTC/USDT:USDT  4h    breakout_htf         31      32.3    1.17    0.273    6.89      -15.15   -28.59   1      no edge       
LTC/USDT:USDT  4h    pullback_htf         18      16.7    0.49    -0.799   -14.07    -14.07   -28.59   1      too few trades
LTC/USDT:USDT  4h    chandelier_trend     88      29.5    0.77    -0.123   -11.63    -22.39   -28.59   1      no edge       
LTC/USDT:USDT  4h    donchian_ensemble    67      19.4    0.81    -0.099   -7.52     -25.24   -28.59   2      no edge       
LTC/USDT:USDT  4h    tsmom                61      41.0    1.44    0.268    15.95     -11.46   -28.59   3      CANDIDATE     
LTC/USDT:USDT  4h    rsi2_reversion       170     61.2    0.98    -0.002   -1.33     -16.53   -28.59   2      no edge       
LTC/USDT:USDT  4h    shock_reversal       71      71.8    1.43    0.178    12.9      -11.5    -28.59   3      CANDIDATE     
LTC/USDT:USDT  4h    auto                 107     53.3    0.89    -0.052   -6.4      -16.73   -28.59   1      no edge       
LTC/USDT:USDT  1d    ema_cross            20      25.0    0.83    -0.159   -3.93     -11.1    -30.31   0      too few trades
LTC/USDT:USDT  1d    trend_pullback       0       0.0     0.0     0.0      0.0       0.0      -30.31   0      too few trades
LTC/USDT:USDT  1d    donchian_breakout    12      25.0    0.88    -0.099   -1.61     -10.67   -30.31   2      too few trades
LTC/USDT:USDT  1d    bollinger_reversion  21      61.9    0.97    -0.01    -0.42     -6.55    -30.31   2      too few trades
LTC/USDT:USDT  1d    supertrend           13      30.8    0.82    -0.109   -1.64     -8.48    -30.31   1      too few trades
LTC/USDT:USDT  1d    ema_cross_adx        0       0.0     0.0     0.0      0.0       0.0      -30.31   0      too few trades
LTC/USDT:USDT  1d    breakout_htf         0       0.0     0.0     0.0      0.0       0.0      -30.31   0      too few trades
LTC/USDT:USDT  1d    pullback_htf         0       0.0     0.0     0.0      0.0       0.0      -30.31   0      too few trades
LTC/USDT:USDT  1d    chandelier_trend     0       0.0     0.0     0.0      0.0       0.0      -30.31   0      too few trades
LTC/USDT:USDT  1d    donchian_ensemble    28      17.9    0.47    -0.325   -8.95     -10.87   -30.31   0      too few trades
LTC/USDT:USDT  1d    tsmom                6       33.3    0.86    -0.092   -0.63     -4.83    -30.31   0      too few trades
LTC/USDT:USDT  1d    rsi2_reversion       14      57.1    1.17    0.068    0.88      -2.56    -30.31   1      too few trades
LTC/USDT:USDT  1d    shock_reversal       9       66.7    1.3     0.105    0.91      -2.1     -30.31   2      too few trades
LTC/USDT:USDT  1d    auto                 34      58.8    0.99    0.002    -0.21     -6.55    -30.31   2      no edge       
```

## Parameters chosen per fold

- **BTC/USDT:USDT 1h ema_cross**: ema_cross(fast=20,slow=21) stop=2.0ATR no tp -> -6.28%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> 0.81%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> -20.52%; ema_cross(fast=9,slow=100) stop=3.0ATR no tp -> 3.81%
- **BTC/USDT:USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> 2.42%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -5.87%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -7.35%; trend_pullback(trend=100,rsi_entry=30,rsi_exit=65) stop=3.0ATR no tp +shorts -> -2.57%
- **BTC/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 0.92%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 2.6%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -9.28%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R +shorts -> -23.47%
- **BTC/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp +shorts -> -6.36%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp -> 3.4%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R -> -2.5%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R -> 8.64%
- **BTC/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> 11.75%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> 10.57%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -8.35%; supertrend(mult=2.0,trend=200) stop=3.0ATR no tp -> 24.67%
- **BTC/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR no tp -> -10.55%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp +shorts -> -1.96%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp -> 1.1%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp +shorts -> 21.46%
- **BTC/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R -> -11.9%; breakout_htf(entry_n=20,trend=400) stop=2.0ATR no tp -> -24.97%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R +shorts -> 29.93%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R +shorts -> -18.03%
- **BTC/USDT:USDT 1h pullback_htf**: pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR no tp -> 10.76%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> 5.37%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -6.46%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -5.9%
- **BTC/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=100,mult=2.5) stop=2.0ATR no tp -> -6.55%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR no tp -> -2.78%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR no tp -> -32.45%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> -13.85%
- **BTC/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 21.45%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> -0.33%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> -3.23%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 9.4%
- **BTC/USDT:USDT 1h tsmom**: tsmom(lookback=84,z=1.0) stop=3.0ATR no tp -> -9.47%; tsmom(lookback=84,z=0.5) stop=5.0ATR no tp -> -4.99%; tsmom(lookback=42,z=1.0) stop=3.0ATR no tp -> -6.98%; tsmom(lookback=42,z=1.0) stop=3.0ATR no tp +shorts -> -26.75%
- **BTC/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -9.15%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> 1.24%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -11.44%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -2.52%
- **BTC/USDT:USDT 1h shock_reversal**: shock_reversal(k=2.5) stop=2.0ATR tp=1.5R -> -32.83%; shock_reversal(k=2.5) stop=2.0ATR tp=1.5R -> -9.48%; shock_reversal(k=3.5) stop=2.0ATR no tp -> -10.7%; shock_reversal(k=3.5) stop=2.0ATR no tp -> -5.8%
- **BTC/USDT:USDT 1h auto**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> 2.42%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> 0.81%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> -20.52%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R +shorts -> -23.47%
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
- **BTC/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=9,slow=21) stop=2.0ATR no tp +shorts -> -4.18%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> -5.1%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> 4.29%
- **BTC/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BTC/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 0.05%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -5.39%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 0.63%
- **BTC/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> -0.74%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -3.49%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -0.92%
- **BTC/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp +shorts -> -8.04%; supertrend(mult=2.0,trend=0) stop=2.0ATR no tp -> -5.99%; supertrend(mult=2.0,trend=0) stop=2.0ATR no tp -> 6.31%
- **BTC/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BTC/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BTC/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BTC/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp +shorts -> 9.5%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp +shorts -> -1.09%
- **BTC/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> -3.38%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=3.0ATR no tp +shorts -> -0.32%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=3.0ATR no tp -> 2.71%
- **BTC/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> -2.33%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp -> 3.92%
- **BTC/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp +shorts -> -1.96%
- **BTC/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=2.0ATR no tp +shorts -> -5.28%
- **BTC/USDT:USDT 1d auto**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 0.05%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -5.39%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp +shorts -> -1.96%
- **ETH/USDT:USDT 1h ema_cross**: ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> 5.17%; ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> -10.86%; ema_cross(fast=9,slow=50) stop=3.0ATR no tp -> -6.17%; ema_cross(fast=9,slow=50) stop=3.0ATR no tp +shorts -> -3.07%
- **ETH/USDT:USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -9.8%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> -5.14%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> 6.06%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> 4.42%
- **ETH/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R -> -1.55%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R +shorts -> 30.49%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R +shorts -> 15.28%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R +shorts -> -17.37%
- **ETH/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.0,trend=200) stop=2.0ATR no tp -> -5.26%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> 1.81%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -3.89%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -5.46%
- **ETH/USDT:USDT 1h supertrend**: supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> -6.39%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> 0.54%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -2.91%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> 5.09%
- **ETH/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp -> -2.38%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR no tp -> 11.88%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR no tp -> -4.91%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR no tp +shorts -> 15.94%
- **ETH/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R -> -10.48%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R +shorts -> 51.68%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R +shorts -> 26.5%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R +shorts -> -28.32%
- **ETH/USDT:USDT 1h pullback_htf**: pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -25.09%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR tp=3.0R -> 10.99%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR tp=3.0R -> -3.13%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R -> -3.75%
- **ETH/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> 0.23%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R +shorts -> 20.19%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R +shorts -> -25.64%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> 13.77%
- **ETH/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=360,thr=0.34,lo=0.2) stop=3.0ATR no tp -> -20.19%; donchian_ensemble(max_n=360,thr=0.67,lo=0.0) stop=5.0ATR no tp +shorts -> 15.84%; donchian_ensemble(max_n=360,thr=0.67,lo=0.0) stop=5.0ATR no tp +shorts -> 6.6%; donchian_ensemble(max_n=360,thr=0.67,lo=0.0) stop=5.0ATR no tp +shorts -> 0.34%
- **ETH/USDT:USDT 1h tsmom**: tsmom(lookback=42,z=1.0) stop=5.0ATR no tp -> 3.65%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> 21.62%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> 11.28%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> -3.93%
- **ETH/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> 12.99%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> -1.25%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> -2.75%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> -13.36%
- **ETH/USDT:USDT 1h shock_reversal**: shock_reversal(k=3.5) stop=3.0ATR no tp -> -11.54%; shock_reversal(k=2.5) stop=3.0ATR no tp -> -22.52%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -3.82%; shock_reversal(k=3.5) stop=3.0ATR tp=1.5R -> -1.02%
- **ETH/USDT:USDT 1h auto**: ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> 5.17%; ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> -10.86%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> 11.28%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> -3.93%
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
- **ETH/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=9,slow=21) stop=3.0ATR tp=3.0R -> 10.71%; ema_cross(fast=9,slow=21) stop=3.0ATR tp=3.0R -> -5.03%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R -> 3.05%
- **ETH/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ETH/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R +shorts -> 10.01%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR tp=3.0R +shorts -> -3.74%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R +shorts -> 1.2%
- **ETH/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp +shorts -> -1.09%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -4.6%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -3.16%
- **ETH/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> 4.02%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> -8.14%; supertrend(mult=3.0,trend=0) stop=2.0ATR tp=3.0R +shorts -> 10.38%
- **ETH/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> 5.77%
- **ETH/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ETH/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ETH/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> 2.91%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR no tp +shorts -> 0.0%
- **ETH/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp +shorts -> 6.78%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp +shorts -> -3.25%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=3.0ATR no tp +shorts -> -0.33%
- **ETH/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> 1.23%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> 4.83%
- **ETH/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ETH/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=2.0ATR no tp +shorts -> 3.32%; shock_reversal(k=2.5) stop=2.0ATR no tp +shorts -> -0.65%
- **ETH/USDT:USDT 1d auto**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R +shorts -> 10.01%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR tp=3.0R +shorts -> -3.74%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R +shorts -> 1.2%
- **SOL/USDT:USDT 1h ema_cross**: ema_cross(fast=20,slow=21) stop=3.0ATR no tp -> 28.74%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> 38.61%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> 16.64%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> -26.65%
- **SOL/USDT:USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> 13.53%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -0.25%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -2.44%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR tp=3.0R -> 2.41%
- **SOL/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -0.6%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> -9.57%; donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -7.26%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -9.64%
- **SOL/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -2.5%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -19.9%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -4.27%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 8.16%
- **SOL/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> 3.84%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> 11.69%; supertrend(mult=2.0,trend=200) stop=3.0ATR tp=3.0R -> 14.29%; supertrend(mult=2.0,trend=200) stop=3.0ATR tp=3.0R -> -5.97%
- **SOL/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R -> 11.68%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R -> -1.54%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R +shorts -> 15.13%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R +shorts -> -9.8%
- **SOL/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=20,trend=400) stop=3.0ATR no tp -> 8.53%; breakout_htf(entry_n=20,trend=400) stop=3.0ATR tp=3.0R -> 21.06%; breakout_htf(entry_n=20,trend=400) stop=2.0ATR no tp +shorts -> 8.08%; breakout_htf(entry_n=20,trend=400) stop=3.0ATR tp=3.0R +shorts -> 5.63%
- **SOL/USDT:USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R +shorts -> -26.88%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -10.6%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R -> 2.47%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R -> -14.74%
- **SOL/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=2.0ATR no tp -> 21.0%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR no tp -> 13.67%; chandelier_trend(trend=200,mult=3.5) stop=2.0ATR no tp -> -14.6%; chandelier_trend(trend=200,mult=3.5) stop=2.0ATR no tp -> 50.5%
- **SOL/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 11.82%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 6.99%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> -1.8%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> -0.48%
- **SOL/USDT:USDT 1h tsmom**: tsmom(lookback=84,z=0.5) stop=5.0ATR no tp -> -1.16%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 5.56%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 0.61%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> -3.6%
- **SOL/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -0.8%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -5.58%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -2.27%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -0.98%
- **SOL/USDT:USDT 1h shock_reversal**: shock_reversal(k=2.5) stop=2.0ATR tp=1.5R -> -8.97%; shock_reversal(k=2.5) stop=2.0ATR tp=1.5R -> -10.17%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -8.84%; shock_reversal(k=3.5) stop=2.0ATR no tp -> 7.88%
- **SOL/USDT:USDT 1h auto**: rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -0.8%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> 38.61%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> 16.64%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> -26.65%
- **SOL/USDT:USDT 4h ema_cross**: ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R -> 16.35%; ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R -> 6.74%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R -> -5.42%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R -> 8.29%
- **SOL/USDT:USDT 4h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=3.0ATR no tp +shorts -> -5.98%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=3.0ATR no tp -> -3.13%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> 16.81%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> -2.71%
- **SOL/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR no tp -> 7.1%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR no tp -> 1.49%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR no tp -> -2.04%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR no tp -> 22.83%
- **SOL/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -1.04%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> 4.75%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> 5.12%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> -2.98%
- **SOL/USDT:USDT 4h supertrend**: supertrend(mult=3.0,trend=0) stop=2.0ATR tp=3.0R -> -6.83%; supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R -> 13.98%; supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R -> -15.38%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R -> 8.76%
- **SOL/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> 16.23%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR tp=3.0R +shorts -> 5.34%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> -1.18%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> -6.9%
- **SOL/USDT:USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> -5.74%; breakout_htf(entry_n=20,trend=400) stop=2.0ATR tp=3.0R +shorts -> 1.26%; breakout_htf(entry_n=20,trend=400) stop=3.0ATR tp=3.0R +shorts -> 6.43%
- **SOL/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -2.4%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp +shorts -> 8.59%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp +shorts -> -12.98%
- **SOL/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R -> -4.05%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR tp=3.0R +shorts -> 2.6%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> 8.52%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> -8.46%
- **SOL/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 3.51%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 0.07%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=3.0ATR no tp -> -8.65%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=3.0ATR no tp +shorts -> 14.09%
- **SOL/USDT:USDT 4h tsmom**: tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 1.76%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 3.87%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 3.25%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 12.7%
- **SOL/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp +shorts -> -4.83%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp +shorts -> 0.4%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp +shorts -> -2.48%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp +shorts -> -2.63%
- **SOL/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=2.0ATR no tp +shorts -> 6.9%; shock_reversal(k=2.5) stop=2.0ATR tp=1.5R -> 12.0%; shock_reversal(k=2.5) stop=2.0ATR no tp -> -9.18%; shock_reversal(k=2.5) stop=2.0ATR no tp -> 1.23%
- **SOL/USDT:USDT 4h auto**: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR no tp -> 7.1%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR no tp -> 1.49%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> 5.12%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> -2.98%
- **SOL/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=9,slow=21) stop=3.0ATR tp=3.0R +shorts -> -1.45%; ema_cross(fast=9,slow=21) stop=3.0ATR tp=3.0R -> -1.88%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> -2.15%
- **SOL/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **SOL/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -1.34%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -2.83%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -0.45%
- **SOL/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp +shorts -> -0.59%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -3.69%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> 2.52%
- **SOL/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> -2.34%; supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R -> -3.01%; supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> 1.96%
- **SOL/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R +shorts -> -0.84%
- **SOL/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **SOL/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **SOL/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> -1.64%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R -> -1.11%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> -0.76%
- **SOL/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> -2.51%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=3.0ATR no tp +shorts -> 0.03%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp +shorts -> 1.55%
- **SOL/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp +shorts -> -0.62%; tsmom(lookback=84,z=0.5) stop=5.0ATR no tp +shorts -> -1.74%
- **SOL/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **SOL/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **SOL/USDT:USDT 1d auto**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> -2.51%; ema_cross(fast=9,slow=21) stop=3.0ATR tp=3.0R -> -1.88%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> -2.15%
- **XRP/USDT:USDT 1h ema_cross**: ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R -> 9.21%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R -> 22.5%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R +shorts -> 16.6%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R +shorts -> -1.53%
- **XRP/USDT:USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R +shorts -> -0.48%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=2.0ATR no tp +shorts -> -0.23%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=2.0ATR tp=3.0R +shorts -> -2.5%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=2.0ATR tp=3.0R +shorts -> 9.49%
- **XRP/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> 35.27%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 22.46%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> 6.57%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=2.0ATR no tp +shorts -> 30.19%
- **XRP/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -8.82%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> 7.81%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> -6.96%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> -14.42%
- **XRP/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R -> 3.39%; supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> 9.88%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> -24.77%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp +shorts -> -19.62%
- **XRP/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR tp=3.0R -> -5.5%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> -1.03%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> 9.47%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> -14.73%
- **XRP/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=20,trend=800) stop=2.0ATR no tp +shorts -> 37.4%; breakout_htf(entry_n=20,trend=800) stop=3.0ATR tp=3.0R +shorts -> 17.06%; breakout_htf(entry_n=20,trend=800) stop=3.0ATR tp=3.0R +shorts -> 28.37%; breakout_htf(entry_n=20,trend=800) stop=3.0ATR tp=3.0R +shorts -> 14.05%
- **XRP/USDT:USDT 1h pullback_htf**: pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 3.05%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -5.76%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -2.29%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp +shorts -> -26.8%
- **XRP/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=3.0ATR no tp -> -16.3%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R -> -6.68%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R -> -11.85%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R -> -12.04%
- **XRP/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp -> 46.37%; donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 11.77%; donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=5.0ATR no tp -> 10.14%; donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=5.0ATR no tp -> 17.7%
- **XRP/USDT:USDT 1h tsmom**: tsmom(lookback=42,z=1.0) stop=3.0ATR no tp -> 15.57%; tsmom(lookback=168,z=1.0) stop=5.0ATR no tp -> 17.26%; tsmom(lookback=168,z=1.0) stop=5.0ATR no tp -> -6.38%; tsmom(lookback=168,z=1.0) stop=5.0ATR no tp -> 1.96%
- **XRP/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 5.56%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -9.99%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -3.4%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -18.55%
- **XRP/USDT:USDT 1h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR no tp -> -11.45%; shock_reversal(k=2.5) stop=3.0ATR no tp -> -10.35%; shock_reversal(k=3.5) stop=3.0ATR tp=1.5R +shorts -> -13.05%; shock_reversal(k=3.5) stop=3.0ATR tp=1.5R +shorts -> -11.3%
- **XRP/USDT:USDT 1h auto**: rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 5.56%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=2.0ATR no tp +shorts -> -0.23%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=65) stop=2.0ATR tp=3.0R +shorts -> -2.5%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R +shorts -> -1.53%
- **XRP/USDT:USDT 4h ema_cross**: ema_cross(fast=9,slow=100) stop=2.0ATR tp=3.0R -> 3.13%; ema_cross(fast=20,slow=21) stop=3.0ATR no tp -> 10.71%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> -5.67%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> 5.9%
- **XRP/USDT:USDT 4h trend_pullback**: trend_pullback(trend=200,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp +shorts -> -3.7%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp -> -7.91%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R -> -4.51%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> -4.25%
- **XRP/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=2.0ATR tp=3.0R +shorts -> 55.11%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 5.32%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> 7.63%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> 1.37%
- **XRP/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -0.75%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> -1.03%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 0.04%; bollinger_reversion(k=2.0,trend=200) stop=2.0ATR no tp +shorts -> 1.56%
- **XRP/USDT:USDT 4h supertrend**: supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 10.22%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> 2.01%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> -7.87%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> -3.0%
- **XRP/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R +shorts -> 8.14%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR no tp +shorts -> -2.9%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR tp=3.0R +shorts -> -2.36%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR tp=3.0R +shorts -> -3.78%
- **XRP/USDT:USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 8.69%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 5.21%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 7.0%
- **XRP/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 0.66%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -4.24%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp +shorts -> -5.49%
- **XRP/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R -> 12.8%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR no tp +shorts -> 1.39%; chandelier_trend(trend=200,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 13.77%; chandelier_trend(trend=200,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 2.03%
- **XRP/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=360,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 71.13%; donchian_ensemble(max_n=360,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 3.64%; donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=3.0ATR no tp -> 0.1%; donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=3.0ATR no tp -> -9.97%
- **XRP/USDT:USDT 4h tsmom**: tsmom(lookback=84,z=0.5) stop=5.0ATR no tp +shorts -> 54.27%; tsmom(lookback=84,z=0.5) stop=5.0ATR no tp -> 4.56%; tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> -3.24%; tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> -2.47%
- **XRP/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -2.4%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR tp=1.5R -> -8.54%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> 0.45%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -1.27%
- **XRP/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR tp=1.5R +shorts -> -14.86%; shock_reversal(k=3.5) stop=2.0ATR tp=1.5R -> 10.21%; shock_reversal(k=3.5) stop=2.0ATR no tp -> 7.02%; shock_reversal(k=3.5) stop=2.0ATR tp=1.5R -> -2.41%
- **XRP/USDT:USDT 4h auto**: shock_reversal(k=2.5) stop=3.0ATR tp=1.5R +shorts -> -14.86%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> 8.69%; shock_reversal(k=3.5) stop=2.0ATR no tp -> 7.02%; shock_reversal(k=3.5) stop=2.0ATR tp=1.5R -> -2.41%
- **XRP/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=20,slow=21) stop=2.0ATR no tp +shorts -> 2.5%; ema_cross(fast=20,slow=21) stop=2.0ATR no tp +shorts -> -1.95%; ema_cross(fast=20,slow=21) stop=2.0ATR no tp +shorts -> -3.27%
- **XRP/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **XRP/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> 0.48%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -1.3%; donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> 5.96%
- **XRP/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> 4.29%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp -> 0.89%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp -> 3.16%
- **XRP/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=2.0ATR no tp +shorts -> -0.48%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp +shorts -> -0.43%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> -2.93%
- **XRP/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **XRP/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **XRP/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **XRP/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp +shorts -> -0.63%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp +shorts -> 1.33%
- **XRP/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp +shorts -> -3.84%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> -1.68%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp -> 1.2%
- **XRP/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> -2.31%; tsmom(lookback=42,z=1.0) stop=3.0ATR no tp +shorts -> -1.72%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> -1.46%
- **XRP/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **XRP/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=2.0ATR tp=1.5R +shorts -> 4.7%; shock_reversal(k=2.5) stop=2.0ATR tp=1.5R +shorts -> 6.14%; shock_reversal(k=2.5) stop=2.0ATR tp=1.5R +shorts -> -5.69%
- **XRP/USDT:USDT 1d auto**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> 0.48%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -1.3%; donchian_breakout(entry_n=55,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> 5.96%
- **BNB/USDT:USDT 1h ema_cross**: ema_cross(fast=9,slow=100) stop=3.0ATR no tp -> -9.5%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp -> -9.71%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R +shorts -> -25.38%; ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R -> 3.42%
- **BNB/USDT:USDT 1h trend_pullback**: trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -27.34%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -6.01%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -6.91%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=2.0ATR no tp +shorts -> -2.8%
- **BNB/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> -14.48%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> -1.75%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR no tp -> 8.01%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 10.2%
- **BNB/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -20.72%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> -2.18%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp -> -0.87%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp -> -11.1%
- **BNB/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=200) stop=3.0ATR tp=3.0R -> -7.3%; supertrend(mult=3.0,trend=200) stop=3.0ATR no tp -> -17.53%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> 4.96%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> 0.35%
- **BNB/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> -3.63%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> 6.04%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> -6.28%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> -3.13%
- **BNB/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R -> -1.35%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R -> -9.76%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> 6.45%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> -7.76%
- **BNB/USDT:USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R -> -10.64%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R -> 31.55%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR no tp -> 12.07%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR no tp -> -11.12%
- **BNB/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> -6.01%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> -9.99%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> -10.67%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> 0.48%
- **BNB/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=3.0ATR no tp -> 10.17%; donchian_ensemble(max_n=360,thr=0.34,lo=0.0) stop=5.0ATR no tp -> -8.66%; donchian_ensemble(max_n=360,thr=0.67,lo=0.0) stop=5.0ATR no tp -> 6.89%; donchian_ensemble(max_n=360,thr=0.67,lo=0.0) stop=5.0ATR no tp -> -4.04%
- **BNB/USDT:USDT 1h tsmom**: tsmom(lookback=168,z=0.5) stop=5.0ATR no tp -> 11.05%; tsmom(lookback=168,z=0.5) stop=5.0ATR no tp -> 18.2%; tsmom(lookback=168,z=0.5) stop=5.0ATR no tp -> 2.38%; tsmom(lookback=168,z=0.5) stop=5.0ATR no tp -> 2.88%
- **BNB/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> 0.61%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -3.59%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR tp=1.5R -> -12.78%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR tp=1.5R +shorts -> -12.66%
- **BNB/USDT:USDT 1h shock_reversal**: shock_reversal(k=3.5) stop=3.0ATR no tp -> -10.0%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -5.82%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -6.78%; shock_reversal(k=3.5) stop=2.0ATR tp=1.5R -> 10.11%
- **BNB/USDT:USDT 1h auto**: shock_reversal(k=3.5) stop=3.0ATR no tp -> -10.0%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> 6.04%; tsmom(lookback=168,z=0.5) stop=5.0ATR no tp -> 2.38%; tsmom(lookback=168,z=0.5) stop=5.0ATR no tp -> 2.88%
- **BNB/USDT:USDT 4h ema_cross**: ema_cross(fast=20,slow=21) stop=3.0ATR no tp -> 8.33%; ema_cross(fast=9,slow=100) stop=2.0ATR tp=3.0R -> 9.81%; ema_cross(fast=9,slow=100) stop=2.0ATR tp=3.0R -> 9.59%; ema_cross(fast=9,slow=100) stop=2.0ATR no tp -> -9.0%
- **BNB/USDT:USDT 4h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> 4.67%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> -1.07%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> 4.95%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> -0.99%
- **BNB/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 5.85%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 1.9%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 10.14%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 6.15%
- **BNB/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp -> -9.11%; bollinger_reversion(k=2.0,trend=200) stop=2.0ATR no tp -> -8.3%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -2.95%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp +shorts -> 0.89%
- **BNB/USDT:USDT 4h supertrend**: supertrend(mult=3.0,trend=0) stop=3.0ATR no tp -> -3.85%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 5.17%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> 5.28%; supertrend(mult=3.0,trend=200) stop=2.0ATR no tp +shorts -> -9.74%
- **BNB/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR no tp +shorts -> -11.11%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> 16.01%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> -1.52%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> 1.09%
- **BNB/USDT:USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=20,trend=400) stop=3.0ATR tp=3.0R +shorts -> -3.96%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR no tp -> 13.54%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR no tp -> 2.79%
- **BNB/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR no tp -> 4.79%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -2.17%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR no tp -> -4.13%
- **BNB/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=3.0ATR no tp -> 8.68%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR no tp -> 0.61%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R -> -4.03%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R -> -3.95%
- **BNB/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=360,thr=0.34,lo=0.2) stop=3.0ATR no tp -> 3.28%; donchian_ensemble(max_n=360,thr=0.34,lo=0.0) stop=3.0ATR no tp -> 6.78%; donchian_ensemble(max_n=360,thr=0.34,lo=0.0) stop=5.0ATR no tp -> -4.04%; donchian_ensemble(max_n=360,thr=0.34,lo=0.0) stop=3.0ATR no tp -> -3.4%
- **BNB/USDT:USDT 4h tsmom**: tsmom(lookback=42,z=0.5) stop=3.0ATR no tp -> 4.96%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp -> 13.56%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp -> -3.78%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> -0.12%
- **BNB/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp -> -18.59%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp +shorts -> -8.19%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp +shorts -> 1.68%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp +shorts -> -5.22%
- **BNB/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR no tp +shorts -> -7.97%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 1.47%; shock_reversal(k=2.5) stop=3.0ATR no tp -> -6.47%; shock_reversal(k=2.5) stop=3.0ATR no tp -> 1.71%
- **BNB/USDT:USDT 4h auto**: donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 5.85%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR no tp -> 0.61%; ema_cross(fast=9,slow=100) stop=2.0ATR tp=3.0R -> 9.59%; ema_cross(fast=9,slow=100) stop=2.0ATR no tp -> -9.0%
- **BNB/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=9,slow=21) stop=3.0ATR tp=3.0R -> 3.05%; ema_cross(fast=9,slow=21) stop=3.0ATR tp=3.0R -> 0.16%; ema_cross(fast=20,slow=50) stop=2.0ATR tp=3.0R +shorts -> 2.14%
- **BNB/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BNB/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 10.0%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> 1.25%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> 3.47%
- **BNB/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp +shorts -> -3.08%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp -> -1.24%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp -> -0.42%
- **BNB/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> 0.26%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> -0.05%; supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R -> 3.25%
- **BNB/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BNB/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BNB/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BNB/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> -0.62%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> -4.24%
- **BNB/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp +shorts -> -0.87%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> -1.21%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 0.31%
- **BNB/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> -0.06%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp -> 0.8%; tsmom(lookback=42,z=1.0) stop=3.0ATR no tp +shorts -> -2.33%
- **BNB/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **BNB/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=3.0ATR tp=1.5R +shorts -> 3.21%
- **BNB/USDT:USDT 1d auto**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> 0.26%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> -0.05%; shock_reversal(k=2.5) stop=3.0ATR tp=1.5R +shorts -> 3.21%
- **DOGE/USDT:USDT 1h ema_cross**: ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R -> 22.06%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R -> 7.48%; ema_cross(fast=20,slow=100) stop=2.0ATR no tp -> -3.03%; ema_cross(fast=20,slow=100) stop=2.0ATR no tp +shorts -> -48.61%
- **DOGE/USDT:USDT 1h trend_pullback**: trend_pullback(trend=200,rsi_entry=40,rsi_exit=65) stop=2.0ATR tp=3.0R +shorts -> -9.12%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp -> -5.05%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=2.0ATR no tp +shorts -> -7.66%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=2.0ATR no tp +shorts -> -4.57%
- **DOGE/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 43.93%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 30.11%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=3.0ATR tp=3.0R +shorts -> -8.81%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=3.0ATR tp=3.0R +shorts -> -29.71%
- **DOGE/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 0.03%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -3.7%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 2.91%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -1.92%
- **DOGE/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> 22.64%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> -12.93%; supertrend(mult=3.0,trend=0) stop=2.0ATR no tp +shorts -> -31.78%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> -27.27%
- **DOGE/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR tp=3.0R -> -8.42%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp +shorts -> 16.63%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR tp=3.0R -> -14.52%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> -25.35%
- **DOGE/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=20,trend=800) stop=3.0ATR tp=3.0R -> 19.3%; breakout_htf(entry_n=20,trend=400) stop=3.0ATR tp=3.0R -> 27.12%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R +shorts -> 5.88%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R +shorts -> -7.31%
- **DOGE/USDT:USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> 12.55%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -11.52%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 8.06%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> -7.66%
- **DOGE/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> -5.29%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R -> -2.75%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R -> -15.01%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> -25.44%
- **DOGE/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp -> 29.24%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 10.2%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp +shorts -> -6.38%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp +shorts -> -17.04%
- **DOGE/USDT:USDT 1h tsmom**: tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 45.26%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 21.06%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 6.68%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> -1.03%
- **DOGE/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> 7.98%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -0.51%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -0.82%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -4.52%
- **DOGE/USDT:USDT 1h shock_reversal**: shock_reversal(k=3.5) stop=3.0ATR no tp -> -4.94%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -13.68%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -9.62%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 3.0%
- **DOGE/USDT:USDT 1h auto**: bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 0.03%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -0.51%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=2.0ATR no tp +shorts -> -7.66%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR tp=3.0R +shorts -> -7.31%
- **DOGE/USDT:USDT 4h ema_cross**: ema_cross(fast=20,slow=50) stop=3.0ATR no tp -> 19.22%; ema_cross(fast=9,slow=50) stop=3.0ATR tp=3.0R -> 12.87%; ema_cross(fast=9,slow=100) stop=2.0ATR tp=3.0R +shorts -> 16.43%; ema_cross(fast=9,slow=100) stop=2.0ATR tp=3.0R +shorts -> -3.93%
- **DOGE/USDT:USDT 4h trend_pullback**: nothing qualified -> 0.0%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R +shorts -> -2.09%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> 11.3%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> 4.81%
- **DOGE/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R +shorts -> 18.81%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> 7.0%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> -7.95%; donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=2.0ATR tp=3.0R +shorts -> -1.44%
- **DOGE/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.5,trend=0) stop=2.0ATR tp=3.0R +shorts -> -17.84%; bollinger_reversion(k=2.5,trend=0) stop=2.0ATR no tp -> -9.53%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> 8.21%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> 1.66%
- **DOGE/USDT:USDT 4h supertrend**: supertrend(mult=3.0,trend=0) stop=2.0ATR no tp -> 48.22%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 24.55%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R -> -1.51%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 6.34%
- **DOGE/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp +shorts -> 6.92%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> 7.21%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> -0.8%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R -> -1.22%
- **DOGE/USDT:USDT 4h breakout_htf**: breakout_htf(entry_n=20,trend=400) stop=2.0ATR tp=3.0R +shorts -> 23.65%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R +shorts -> 1.87%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R +shorts -> -3.4%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R -> -1.05%
- **DOGE/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp +shorts -> 0.07%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp +shorts -> 5.43%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp +shorts -> -15.36%
- **DOGE/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R -> 1.9%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R +shorts -> 12.03%; chandelier_trend(trend=200,mult=2.5) stop=2.0ATR tp=3.0R -> 1.72%; chandelier_trend(trend=200,mult=2.5) stop=2.0ATR tp=3.0R -> -1.4%
- **DOGE/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=360,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 56.55%; donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=3.0ATR no tp -> 4.86%; donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=5.0ATR no tp -> -2.74%; donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=5.0ATR no tp -> -0.47%
- **DOGE/USDT:USDT 4h tsmom**: tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 9.43%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> 6.82%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> -8.24%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp +shorts -> 11.58%
- **DOGE/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -3.81%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -1.16%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -3.54%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -1.53%
- **DOGE/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=2.0ATR no tp -> 6.26%; shock_reversal(k=2.5) stop=3.0ATR no tp -> 6.9%; shock_reversal(k=2.5) stop=3.0ATR no tp -> -8.11%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 1.31%
- **DOGE/USDT:USDT 4h auto**: rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp -> -3.81%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 24.55%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R -> -1.51%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 6.34%
- **DOGE/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp +shorts -> -0.82%; ema_cross(fast=9,slow=21) stop=3.0ATR no tp +shorts -> -5.75%; ema_cross(fast=9,slow=21) stop=2.0ATR no tp -> 2.77%
- **DOGE/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **DOGE/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 1.29%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -1.69%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 5.17%
- **DOGE/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp +shorts -> -3.69%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp +shorts -> -2.99%; bollinger_reversion(k=2.5,trend=0) stop=2.0ATR no tp -> -2.32%
- **DOGE/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR no tp +shorts -> -0.35%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> -4.6%; supertrend(mult=3.0,trend=0) stop=3.0ATR no tp -> -0.63%
- **DOGE/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **DOGE/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **DOGE/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **DOGE/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> 0.2%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> 5.96%
- **DOGE/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> 0.43%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=3.0ATR no tp -> -3.3%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp -> -1.82%
- **DOGE/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> -1.55%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> -0.52%
- **DOGE/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **DOGE/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=2.0ATR no tp +shorts -> -0.26%
- **DOGE/USDT:USDT 1d auto**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 1.29%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -1.69%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 5.17%
- **ADA/USDT:USDT 1h ema_cross**: ema_cross(fast=9,slow=50) stop=2.0ATR tp=3.0R -> 0.19%; ema_cross(fast=20,slow=100) stop=2.0ATR tp=3.0R +shorts -> 4.21%; ema_cross(fast=20,slow=100) stop=2.0ATR no tp +shorts -> 4.21%; ema_cross(fast=20,slow=100) stop=2.0ATR no tp +shorts -> 0.42%
- **ADA/USDT:USDT 1h trend_pullback**: trend_pullback(trend=200,rsi_entry=40,rsi_exit=65) stop=3.0ATR no tp -> -4.61%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> -1.15%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=3.0ATR tp=3.0R +shorts -> -7.02%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> -8.94%
- **ADA/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> 78.83%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> -11.05%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> 7.59%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -7.11%
- **ADA/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> -5.96%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> -0.03%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 2.62%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp -> 2.82%
- **ADA/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R -> 21.09%; supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R -> -26.85%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp -> -13.49%; supertrend(mult=2.0,trend=200) stop=2.0ATR no tp +shorts -> 6.63%
- **ADA/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR tp=3.0R +shorts -> -6.12%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR tp=3.0R +shorts -> 1.06%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR no tp +shorts -> 13.93%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR no tp +shorts -> -3.53%
- **ADA/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=400) stop=2.0ATR no tp -> 83.44%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 15.65%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 16.34%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 8.04%
- **ADA/USDT:USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR no tp -> -6.72%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> 7.32%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -3.12%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R -> 1.65%
- **ADA/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=2.0ATR tp=3.0R -> -5.55%; chandelier_trend(trend=200,mult=2.5) stop=2.0ATR no tp -> -19.82%; chandelier_trend(trend=200,mult=3.5) stop=2.0ATR no tp -> 7.79%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> -5.17%
- **ADA/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 28.48%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> -5.03%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp -> -4.2%; donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=3.0ATR no tp +shorts -> 1.77%
- **ADA/USDT:USDT 1h tsmom**: tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> 17.69%; tsmom(lookback=168,z=1.0) stop=3.0ATR no tp -> -2.55%; tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> -10.98%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp -> 10.56%
- **ADA/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp +shorts -> -1.59%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> -1.4%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> -5.71%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> -14.61%
- **ADA/USDT:USDT 1h shock_reversal**: shock_reversal(k=3.5) stop=2.0ATR no tp -> -17.15%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -11.31%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -7.01%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -4.7%
- **ADA/USDT:USDT 1h auto**: ema_cross(fast=9,slow=50) stop=2.0ATR tp=3.0R -> 0.19%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> -11.05%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 16.34%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 8.04%
- **ADA/USDT:USDT 4h ema_cross**: ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> 28.44%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp -> -16.75%; ema_cross(fast=9,slow=50) stop=2.0ATR tp=3.0R +shorts -> -4.63%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R +shorts -> -10.46%
- **ADA/USDT:USDT 4h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=2.0ATR no tp +shorts -> -11.72%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> -8.72%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> 11.78%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> -0.08%
- **ADA/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=3.0ATR tp=3.0R +shorts -> 3.28%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> 5.3%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> 2.74%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> 4.3%
- **ADA/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -2.7%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -0.5%; bollinger_reversion(k=2.5,trend=0) stop=2.0ATR no tp -> -1.55%; bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> -0.2%
- **ADA/USDT:USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=3.0ATR no tp -> 22.94%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 20.13%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 24.25%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 12.67%
- **ADA/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR no tp +shorts -> 23.32%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR tp=3.0R +shorts -> -6.93%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=2.0ATR no tp +shorts -> -10.12%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=2.0ATR tp=3.0R +shorts -> 9.2%
- **ADA/USDT:USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=20,trend=800) stop=2.0ATR tp=3.0R +shorts -> -4.23%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> -3.78%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R +shorts -> -3.11%
- **ADA/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> -3.0%; pullback_htf(trend=800,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 7.26%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR no tp +shorts -> -10.66%
- **ADA/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=2.5) stop=3.0ATR no tp +shorts -> 14.82%; chandelier_trend(trend=100,mult=2.5) stop=3.0ATR tp=3.0R +shorts -> -2.18%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R +shorts -> 0.68%; chandelier_trend(trend=200,mult=2.5) stop=3.0ATR tp=3.0R +shorts -> 5.65%
- **ADA/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 37.43%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> -10.75%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> -11.35%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> 2.21%
- **ADA/USDT:USDT 4h tsmom**: tsmom(lookback=84,z=0.5) stop=5.0ATR no tp +shorts -> 14.15%; tsmom(lookback=84,z=0.5) stop=5.0ATR no tp +shorts -> -2.32%; tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> -4.13%; tsmom(lookback=84,z=0.5) stop=5.0ATR no tp +shorts -> -7.41%
- **ADA/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 1.81%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 1.97%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 0.88%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> -3.05%
- **ADA/USDT:USDT 4h shock_reversal**: shock_reversal(k=3.5) stop=2.0ATR tp=1.5R +shorts -> -12.3%; shock_reversal(k=2.5) stop=3.0ATR no tp -> 3.43%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 2.14%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 1.18%
- **ADA/USDT:USDT 4h auto**: rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 1.81%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 1.97%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp -> 0.88%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R +shorts -> 12.67%
- **ADA/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=20,slow=21) stop=2.0ATR no tp +shorts -> -5.7%; ema_cross(fast=20,slow=21) stop=2.0ATR no tp +shorts -> -3.98%; ema_cross(fast=20,slow=50) stop=2.0ATR no tp +shorts -> 1.83%
- **ADA/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ADA/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 1.9%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -2.58%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -6.89%
- **ADA/USDT:USDT 1d bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> 4.1%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> 6.72%; bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp -> -3.29%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> 2.49%
- **ADA/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> -2.47%; supertrend(mult=2.0,trend=0) stop=2.0ATR no tp -> -10.53%; supertrend(mult=2.0,trend=0) stop=2.0ATR no tp -> -5.75%
- **ADA/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ADA/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ADA/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ADA/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> -0.69%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> 7.19%
- **ADA/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=3.0ATR no tp +shorts -> -7.38%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> -2.59%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> -1.9%
- **ADA/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> -8.76%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> 1.55%; tsmom(lookback=42,z=0.5) stop=3.0ATR no tp +shorts -> -2.12%
- **ADA/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **ADA/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=2.0ATR no tp +shorts -> 4.76%; shock_reversal(k=2.5) stop=3.0ATR no tp +shorts -> 2.6%; shock_reversal(k=2.5) stop=3.0ATR no tp +shorts -> 0.66%
- **ADA/USDT:USDT 1d auto**: bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> 4.1%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 1.9%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -2.58%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> -6.89%
- **AVAX/USDT:USDT 1h ema_cross**: ema_cross(fast=9,slow=100) stop=2.0ATR no tp -> 67.93%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R +shorts -> 80.9%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R +shorts -> 26.07%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R +shorts -> -67.55%
- **AVAX/USDT:USDT 1h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=65) stop=3.0ATR no tp +shorts -> -5.36%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR tp=3.0R +shorts -> 7.59%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -6.44%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -6.17%
- **AVAX/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=2.0ATR tp=3.0R -> 62.25%; donchian_breakout(entry_n=55,exit_n=20,trend=0) stop=3.0ATR tp=3.0R +shorts -> 19.23%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=3.0ATR tp=3.0R +shorts -> 18.92%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=3.0ATR tp=3.0R +shorts -> -49.0%
- **AVAX/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=200) stop=3.0ATR no tp +shorts -> -6.3%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -4.94%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> 0.52%; bollinger_reversion(k=2.0,trend=200) stop=3.0ATR no tp -> -4.6%
- **AVAX/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R -> 33.45%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> 23.0%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> -22.46%; supertrend(mult=2.0,trend=0) stop=2.0ATR no tp +shorts -> -51.22%
- **AVAX/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR no tp +shorts -> 18.12%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR no tp +shorts -> -7.11%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR no tp +shorts -> 27.78%; ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> -51.04%
- **AVAX/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> 69.09%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> 23.99%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R +shorts -> 3.21%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> -33.16%
- **AVAX/USDT:USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> 6.52%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R +shorts -> -19.47%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> 2.33%; pullback_htf(trend=800,rsi_entry=45) stop=3.0ATR no tp +shorts -> -6.67%
- **AVAX/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=200,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> 8.1%; chandelier_trend(trend=200,mult=3.5) stop=3.0ATR tp=3.0R +shorts -> -16.88%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 1.31%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> -39.36%
- **AVAX/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=360,thr=0.67,lo=0.0) stop=3.0ATR no tp +shorts -> 49.9%; donchian_ensemble(max_n=360,thr=0.67,lo=0.0) stop=3.0ATR no tp +shorts -> 8.44%; donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=3.0ATR no tp +shorts -> 21.05%; donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=3.0ATR no tp +shorts -> -47.59%
- **AVAX/USDT:USDT 1h tsmom**: tsmom(lookback=84,z=0.5) stop=5.0ATR no tp +shorts -> 10.46%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> 15.15%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> 4.59%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> -25.76%
- **AVAX/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp +shorts -> -6.14%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp +shorts -> -11.05%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR no tp +shorts -> -1.68%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR tp=1.5R +shorts -> -17.17%
- **AVAX/USDT:USDT 1h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR no tp -> -21.69%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 0.59%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -11.52%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -1.36%
- **AVAX/USDT:USDT 1h auto**: ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR no tp +shorts -> 18.12%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R +shorts -> 80.9%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R +shorts -> 26.07%; ema_cross(fast=9,slow=100) stop=3.0ATR tp=3.0R +shorts -> -67.55%
- **AVAX/USDT:USDT 4h ema_cross**: ema_cross(fast=9,slow=50) stop=2.0ATR tp=3.0R +shorts -> 25.41%; ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R +shorts -> 1.13%; ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R +shorts -> -6.47%; ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R +shorts -> -50.28%
- **AVAX/USDT:USDT 4h trend_pullback**: trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> -5.7%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R +shorts -> 4.64%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> 29.54%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp +shorts -> -9.42%
- **AVAX/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R -> 18.7%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R +shorts -> -5.8%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R +shorts -> -5.61%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=3.0ATR tp=3.0R +shorts -> -23.43%
- **AVAX/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.0,trend=0) stop=3.0ATR no tp -> -13.15%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 0.52%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> 7.88%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR no tp +shorts -> 6.66%
- **AVAX/USDT:USDT 4h supertrend**: supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R -> 13.17%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> 17.92%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> 11.29%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> -6.14%
- **AVAX/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=2.0ATR tp=3.0R +shorts -> 1.34%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR tp=3.0R +shorts -> -11.18%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp +shorts -> -1.32%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp +shorts -> 2.96%
- **AVAX/USDT:USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=20,trend=400) stop=3.0ATR tp=3.0R -> -1.75%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR no tp -> 3.5%; breakout_htf(entry_n=55,trend=800) stop=3.0ATR no tp -> 7.27%
- **AVAX/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp +shorts -> -0.13%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R +shorts -> 9.91%; pullback_htf(trend=400,rsi_entry=45) stop=3.0ATR tp=3.0R +shorts -> -8.69%
- **AVAX/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 12.98%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> 21.63%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> -5.25%; chandelier_trend(trend=100,mult=3.5) stop=2.0ATR tp=3.0R +shorts -> -28.57%
- **AVAX/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> 10.83%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp -> -1.23%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp +shorts -> 3.56%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=5.0ATR no tp +shorts -> -17.88%
- **AVAX/USDT:USDT 4h tsmom**: tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> 13.0%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> -1.29%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> 1.49%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp -> 2.68%
- **AVAX/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp +shorts -> -6.86%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> -4.52%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> -3.92%; rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp -> 3.11%
- **AVAX/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR no tp -> 4.59%; shock_reversal(k=2.5) stop=3.0ATR no tp -> 1.91%; shock_reversal(k=3.5) stop=3.0ATR no tp -> 0.23%; shock_reversal(k=3.5) stop=3.0ATR no tp -> -1.72%
- **AVAX/USDT:USDT 4h auto**: rsi2_reversion(lo=5,trend=200) stop=2.0ATR no tp +shorts -> -6.86%; ema_cross(fast=9,slow=21) stop=2.0ATR tp=3.0R +shorts -> 1.13%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> 11.29%; supertrend(mult=3.0,trend=200) stop=3.0ATR tp=3.0R +shorts -> -6.14%
- **AVAX/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R +shorts -> -2.13%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R +shorts -> 5.55%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R +shorts -> 4.75%
- **AVAX/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **AVAX/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -0.02%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -3.97%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R +shorts -> 1.89%
- **AVAX/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> -0.75%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -7.35%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> 1.69%
- **AVAX/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R +shorts -> -4.72%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> 1.08%; supertrend(mult=2.0,trend=0) stop=2.0ATR tp=3.0R +shorts -> 6.7%
- **AVAX/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **AVAX/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **AVAX/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **AVAX/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> -0.23%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> 4.69%
- **AVAX/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp +shorts -> -2.35%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp +shorts -> 3.16%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp +shorts -> 4.19%
- **AVAX/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; tsmom(lookback=42,z=1.0) stop=3.0ATR no tp +shorts -> -2.45%; tsmom(lookback=42,z=1.0) stop=5.0ATR no tp +shorts -> 1.89%
- **AVAX/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; rsi2_reversion(lo=10,trend=200) stop=3.0ATR no tp +shorts -> -1.82%
- **AVAX/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=2.0ATR tp=1.5R +shorts -> -1.34%
- **AVAX/USDT:USDT 1d auto**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=10,trend=0) stop=2.0ATR tp=3.0R -> -0.02%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R +shorts -> 5.55%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R +shorts -> 4.75%
- **LTC/USDT:USDT 1h ema_cross**: ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R -> 8.27%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R -> -20.45%; ema_cross(fast=20,slow=100) stop=2.0ATR no tp +shorts -> -51.48%; ema_cross(fast=20,slow=100) stop=3.0ATR tp=3.0R -> -5.99%
- **LTC/USDT:USDT 1h trend_pullback**: trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R -> -6.88%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=3.0ATR tp=3.0R -> -14.87%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -4.6%; trend_pullback(trend=200,rsi_entry=30,rsi_exit=75) stop=3.0ATR no tp +shorts -> -0.04%
- **LTC/USDT:USDT 1h donchian_breakout**: donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R +shorts -> -12.41%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R +shorts -> 10.76%; donchian_breakout(entry_n=55,exit_n=10,trend=200) stop=2.0ATR tp=3.0R +shorts -> -37.82%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R +shorts -> -19.01%
- **LTC/USDT:USDT 1h bollinger_reversion**: bollinger_reversion(k=2.5,trend=0) stop=3.0ATR tp=3.0R +shorts -> -25.78%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR tp=3.0R +shorts -> -26.98%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R +shorts -> 11.04%; bollinger_reversion(k=2.5,trend=200) stop=2.0ATR tp=3.0R +shorts -> -15.53%
- **LTC/USDT:USDT 1h supertrend**: supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> -14.61%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> -18.62%; supertrend(mult=2.0,trend=200) stop=3.0ATR tp=3.0R -> -10.94%; supertrend(mult=2.0,trend=200) stop=2.0ATR tp=3.0R -> -11.5%
- **LTC/USDT:USDT 1h ema_cross_adx**: ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR tp=3.0R -> 10.63%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR tp=3.0R -> -8.51%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> 12.0%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> -2.35%
- **LTC/USDT:USDT 1h breakout_htf**: breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R +shorts -> -18.65%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> 31.42%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> -15.82%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> -18.68%
- **LTC/USDT:USDT 1h pullback_htf**: pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> 2.78%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -12.38%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> 20.57%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR tp=3.0R -> -4.79%
- **LTC/USDT:USDT 1h chandelier_trend**: chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R -> -19.04%; chandelier_trend(trend=100,mult=3.5) stop=3.0ATR tp=3.0R -> -7.1%; chandelier_trend(trend=200,mult=2.5) stop=2.0ATR no tp -> -27.71%; chandelier_trend(trend=200,mult=2.5) stop=2.0ATR no tp -> -10.14%
- **LTC/USDT:USDT 1h donchian_ensemble**: donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=3.0ATR no tp +shorts -> 10.04%; donchian_ensemble(max_n=90,thr=0.67,lo=0.2) stop=5.0ATR no tp +shorts -> -13.29%; donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=5.0ATR no tp -> -14.11%; donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=5.0ATR no tp -> 4.04%
- **LTC/USDT:USDT 1h tsmom**: tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> 6.58%; tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> 4.18%; tsmom(lookback=84,z=1.0) stop=5.0ATR no tp -> -16.46%; tsmom(lookback=168,z=0.5) stop=5.0ATR no tp -> 1.51%
- **LTC/USDT:USDT 1h rsi2_reversion**: rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp -> -25.82%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR tp=1.5R -> 2.38%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR tp=1.5R +shorts -> 0.02%; rsi2_reversion(lo=5,trend=200) stop=3.0ATR tp=1.5R +shorts -> -0.12%
- **LTC/USDT:USDT 1h shock_reversal**: shock_reversal(k=3.5) stop=2.0ATR no tp -> -8.64%; shock_reversal(k=3.5) stop=2.0ATR no tp -> -12.46%; shock_reversal(k=3.5) stop=2.0ATR no tp -> -8.08%; shock_reversal(k=3.5) stop=2.0ATR no tp -> 6.94%
- **LTC/USDT:USDT 1h auto**: bollinger_reversion(k=2.5,trend=0) stop=3.0ATR tp=3.0R +shorts -> -25.78%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR tp=3.0R -> -8.51%; breakout_htf(entry_n=55,trend=400) stop=3.0ATR tp=3.0R +shorts -> -15.82%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=2.0ATR tp=3.0R +shorts -> -2.35%
- **LTC/USDT:USDT 4h ema_cross**: ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R -> 7.41%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R -> 2.13%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R -> -8.8%; ema_cross(fast=20,slow=21) stop=2.0ATR tp=3.0R -> -4.25%
- **LTC/USDT:USDT 4h trend_pullback**: trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=3.0ATR no tp +shorts -> -5.2%; trend_pullback(trend=200,rsi_entry=40,rsi_exit=75) stop=2.0ATR tp=3.0R +shorts -> 0.08%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -0.68%; trend_pullback(trend=100,rsi_entry=40,rsi_exit=75) stop=2.0ATR no tp -> -5.54%
- **LTC/USDT:USDT 4h donchian_breakout**: donchian_breakout(entry_n=20,exit_n=20,trend=200) stop=2.0ATR tp=3.0R -> -9.6%; donchian_breakout(entry_n=55,exit_n=20,trend=200) stop=3.0ATR tp=3.0R -> -6.77%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> -7.87%; donchian_breakout(entry_n=20,exit_n=10,trend=200) stop=2.0ATR tp=3.0R -> 6.18%
- **LTC/USDT:USDT 4h bollinger_reversion**: bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 4.43%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 9.73%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 3.52%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -2.65%
- **LTC/USDT:USDT 4h supertrend**: supertrend(mult=3.0,trend=0) stop=3.0ATR tp=3.0R -> 2.92%; supertrend(mult=2.0,trend=200) stop=3.0ATR tp=3.0R -> 1.37%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R -> -7.59%; supertrend(mult=3.0,trend=200) stop=2.0ATR tp=3.0R -> 22.6%
- **LTC/USDT:USDT 4h ema_cross_adx**: ema_cross_adx(fast=20,slow=50,adx_min=20) stop=3.0ATR tp=3.0R +shorts -> -13.05%; ema_cross_adx(fast=20,slow=100,adx_min=20) stop=3.0ATR no tp -> -4.51%; ema_cross_adx(fast=20,slow=100,adx_min=25) stop=3.0ATR no tp -> -5.59%; ema_cross_adx(fast=20,slow=50,adx_min=25) stop=3.0ATR no tp -> 3.33%
- **LTC/USDT:USDT 4h breakout_htf**: nothing qualified -> 0.0%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> -0.08%; breakout_htf(entry_n=55,trend=800) stop=2.0ATR tp=3.0R -> -4.54%; breakout_htf(entry_n=55,trend=400) stop=2.0ATR tp=3.0R -> 12.06%
- **LTC/USDT:USDT 4h pullback_htf**: nothing qualified -> 0.0%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -5.47%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> 1.14%; pullback_htf(trend=400,rsi_entry=45) stop=2.0ATR no tp -> -10.12%
- **LTC/USDT:USDT 4h chandelier_trend**: chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> -10.05%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R -> -3.03%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R -> -3.39%; chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R -> 4.87%
- **LTC/USDT:USDT 4h donchian_ensemble**: donchian_ensemble(max_n=90,thr=0.67,lo=0.0) stop=5.0ATR no tp -> 1.95%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp -> 5.13%; donchian_ensemble(max_n=90,thr=0.34,lo=0.0) stop=5.0ATR no tp -> -12.89%; donchian_ensemble(max_n=360,thr=0.67,lo=0.2) stop=3.0ATR no tp -> -0.94%
- **LTC/USDT:USDT 4h tsmom**: tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 6.96%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> 8.34%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp -> -3.56%; tsmom(lookback=168,z=1.0) stop=3.0ATR no tp +shorts -> 3.76%
- **LTC/USDT:USDT 4h rsi2_reversion**: rsi2_reversion(lo=5,trend=200) stop=2.0ATR tp=1.5R +shorts -> -9.69%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp -> -4.16%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> 10.12%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> 3.52%
- **LTC/USDT:USDT 4h shock_reversal**: shock_reversal(k=2.5) stop=3.0ATR no tp -> 4.39%; shock_reversal(k=2.5) stop=3.0ATR no tp -> 9.29%; shock_reversal(k=2.5) stop=3.0ATR no tp -> -2.58%; shock_reversal(k=2.5) stop=3.0ATR no tp -> 1.59%
- **LTC/USDT:USDT 4h auto**: chandelier_trend(trend=100,mult=2.5) stop=2.0ATR tp=3.0R +shorts -> -10.05%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> 9.73%; shock_reversal(k=2.5) stop=3.0ATR no tp -> -2.58%; bollinger_reversion(k=2.5,trend=0) stop=3.0ATR no tp -> -2.65%
- **LTC/USDT:USDT 1d ema_cross**: nothing qualified -> 0.0%; ema_cross(fast=9,slow=50) stop=2.0ATR no tp +shorts -> -0.68%; ema_cross(fast=20,slow=21) stop=3.0ATR tp=3.0R +shorts -> -2.5%; ema_cross(fast=20,slow=50) stop=2.0ATR tp=3.0R +shorts -> -0.8%
- **LTC/USDT:USDT 1d trend_pullback**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **LTC/USDT:USDT 1d donchian_breakout**: nothing qualified -> 0.0%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R +shorts -> 3.69%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> -7.93%; donchian_breakout(entry_n=20,exit_n=20,trend=0) stop=3.0ATR tp=3.0R -> 3.05%
- **LTC/USDT:USDT 1d bollinger_reversion**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> 0.69%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -1.75%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> 0.67%
- **LTC/USDT:USDT 1d supertrend**: nothing qualified -> 0.0%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> 4.56%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> -5.23%; supertrend(mult=2.0,trend=0) stop=3.0ATR tp=3.0R -> -0.73%
- **LTC/USDT:USDT 1d ema_cross_adx**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **LTC/USDT:USDT 1d breakout_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **LTC/USDT:USDT 1d pullback_htf**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **LTC/USDT:USDT 1d chandelier_trend**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%
- **LTC/USDT:USDT 1d donchian_ensemble**: nothing qualified -> 0.0%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp +shorts -> -2.26%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> -5.53%; donchian_ensemble(max_n=90,thr=0.34,lo=0.2) stop=3.0ATR no tp -> -1.39%
- **LTC/USDT:USDT 1d tsmom**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; tsmom(lookback=42,z=0.5) stop=5.0ATR no tp +shorts -> -0.33%; tsmom(lookback=84,z=0.5) stop=3.0ATR no tp +shorts -> -0.3%
- **LTC/USDT:USDT 1d rsi2_reversion**: nothing qualified -> 0.0%; nothing qualified -> 0.0%; nothing qualified -> 0.0%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> 0.88%
- **LTC/USDT:USDT 1d shock_reversal**: nothing qualified -> 0.0%; shock_reversal(k=2.5) stop=3.0ATR no tp +shorts -> 0.66%; shock_reversal(k=2.5) stop=3.0ATR no tp +shorts -> 2.33%; shock_reversal(k=2.5) stop=3.0ATR no tp -> -2.04%
- **LTC/USDT:USDT 1d auto**: nothing qualified -> 0.0%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp +shorts -> 0.69%; bollinger_reversion(k=2.0,trend=0) stop=2.0ATR no tp -> -1.75%; rsi2_reversion(lo=10,trend=200) stop=2.0ATR no tp +shorts -> 0.88%
