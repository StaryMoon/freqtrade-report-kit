# Freqtrade Backtest Risk Report

Source: `examples/backtest-result.sample.json`

## Executive Summary

- Best strategy by return: **MomentumScalper**
- Return: **18.24%**
- Realized profit: **182.4200 USDT**
- Max drawdown: **11.80%**
- Profit factor: **1.740**
- Risk label: **Clean candidate**

## Strategy Ranking

| Strategy | Trades | Win rate | Return | Profit | Max DD | PF | Label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| MomentumScalper | 8 | 62.50% | 18.24% | 182.4200 USDT | 11.80% | 1.740 | Clean candidate |
| MeanReversionGuard | 6 | 50.00% | 4.41% | 44.1200 USDT | 21.40% | 1.130 | Elevated drawdown |

## MomentumScalper

| Metric | Value |
| --- | ---: |
| Trades | 8 |
| Wins / Losses / Draws | 5 / 3 / 0 |
| Win rate | 62.50% |
| Return | 18.24% |
| Realized profit | 182.4200 USDT |
| Profit factor | 1.740 |
| Expectancy | 22.800 |
| Max drawdown | 11.80% |
| Max drawdown abs | 91.6000 USDT |
| Sharpe / Sortino / Calmar | 1.290 / 1.770 / 1.540 |
| Market change | 6.30% |

### Pair Contribution

| Pair | Trades | Win rate | Avg profit | Total profit | Profit abs |
| --- | ---: | ---: | ---: | ---: | ---: |
| BTC/USDT | 3 | 66.67% | 2.94% | 8.81% | 88.1000 USDT |
| ETH/USDT | 3 | 66.67% | 2.38% | 7.13% | 71.3000 USDT |
| SOL/USDT | 2 | 50.00% | 1.15% | 2.30% | 23.0200 USDT |

### Trade Sample

| Pair | Open | Close | Profit | Profit % | Exit |
| --- | --- | --- | ---: | ---: | --- |
| BTC/USDT | 2026-01-03 04:00:00 | 2026-01-04 12:00:00 | 41.2000 USDT | 4.12% | roi |
| ETH/USDT | 2026-01-08 09:00:00 | 2026-01-10 19:00:00 | -18.9000 USDT | -1.89% | stop_loss |
| SOL/USDT | 2026-02-14 03:00:00 | 2026-02-15 06:00:00 | 31.5000 USDT | 3.15% | trailing_stop_loss |

## MeanReversionGuard

| Metric | Value |
| --- | ---: |
| Trades | 6 |
| Wins / Losses / Draws | 3 / 3 / 0 |
| Win rate | 50.00% |
| Return | 4.41% |
| Realized profit | 44.1200 USDT |
| Profit factor | 1.130 |
| Expectancy | 7.350 |
| Max drawdown | 21.40% |
| Max drawdown abs | 136.9000 USDT |
| Sharpe / Sortino / Calmar | 0.380 / 0.510 / 0.210 |
| Market change | 6.30% |

### Pair Contribution

| Pair | Trades | Win rate | Avg profit | Total profit | Profit abs |
| --- | ---: | ---: | ---: | ---: | ---: |
| BTC/USDT | 2 | 50.00% | 2.75% | 5.51% | 55.1000 USDT |
| ETH/USDT | 4 | 50.00% | -0.27% | -1.10% | -10.9800 USDT |

### Trade Sample

| Pair | Open | Close | Profit | Profit % | Exit |
| --- | --- | --- | ---: | ---: | --- |
| BTC/USDT | 2026-02-01 10:00:00 | 2026-02-03 11:00:00 | 55.1000 USDT | 5.51% | roi |
| ETH/USDT | 2026-03-07 18:00:00 | 2026-03-09 02:00:00 | -31.2000 USDT | -3.12% | stop_loss |

## Risk Review Checklist

- Check whether profit comes from one pair or from broad pair contribution.
- Treat high return with high drawdown as a fragile candidate, not a finished strategy.
- Compare the strategy return with market change before trusting the alpha.
- Re-run the backtest with fresh data, fees, realistic slippage, and at least one out-of-sample period.
- Never enable live trading from a single pretty report.
