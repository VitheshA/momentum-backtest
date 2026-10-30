# momentum-backtest

A 12–1 momentum backtest compared with SPY over roughly ten years.

![tearsheet](output/tearsheet.png)

## Strategy

At each month-end, rank 100 large-cap stocks by their return over the previous 12 months, excluding the most recent month. Hold the top 10 equally for one month and rebalance. Assume a 0.2% cost per rebalance.

## Results

| | 12–1 Momentum |
|---|---|
| Total return | 1,104% |
| CAGR | 28.5% |
| Annualized volatility | 28.0% |
| Sharpe ratio | 1.03 |
| Max drawdown | −26.4% |

**These results are overstated by selection bias.** The backtest uses companies that are large today, so it excludes stocks that failed or left the index. Historical membership data would be needed for a more credible test.

## Scripts

- `01_buy_and_hold.py` — checks the SPY buy-and-hold calculation
- `02_signal.py` — saves monthly momentum rankings
- `03_backtest.py` — runs the strategy and saves charts

## Run

```bash
pip install -r requirements.txt
python 03_backtest.py
```

Run from the repository root. The script uses cached price and ranking files.

## Limitations

The current-day stock universe creates survivorship and selection bias. The signal uses prior prices and earns the following month's return, but that does not fix the universe problem. The 0.2% trading cost is an estimate, and this sample covers only one historical period.

Educational project, not investment advice.
