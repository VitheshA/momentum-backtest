import os

import numpy as np
import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt

cost = 0.002
initial = 10000

# parse_dates turns the date strings into real timestamps so resample works
price = pd.read_csv('data/price.csv', index_col='Date', parse_dates=True)
holdings = pd.read_csv('data/rnk.csv', parse_dates=['Date'])

monthly = price.resample('ME').last()
returns = monthly.pct_change()

# row t now holds the return earned AFTER t, which is what a portfolio picked at t earns
next_return = returns.shift(-1)

dates = holdings['Date'].unique()
strategy = {}
for date in dates:
    tickers = holdings[holdings['Date'] == date]['Ticker']
    strategy[date] = next_return.loc[date, tickers].mean() - cost

strategy = pd.Series(strategy).dropna()

spy = yf.download('SPY', start=price.index[0], end=price.index[-1])['Close']['SPY']
spy = spy.resample('ME').last().pct_change()
spy = spy.reindex(strategy.index).dropna()
strategy = strategy.reindex(spy.index)

strategy_curve = (1 + strategy).cumprod() * initial
spy_curve = (1 + spy).cumprod() * initial

strategy_dd = strategy_curve / strategy_curve.cummax() - 1
spy_dd = spy_curve / spy_curve.cummax() - 1

years = (strategy_curve.index[-1] - strategy_curve.index[0]).days / 365.25

stats = {}
stats['Momentum'] = {
    'Total Return': f"{strategy_curve.iloc[-1] / initial - 1:.1%}",
    'CAGR': f"{(strategy_curve.iloc[-1] / initial) ** (1 / years) - 1:.2%}",
    'Annualized Vol': f"{strategy.std() * np.sqrt(12):.2%}",
    'Sharpe': f"{strategy.mean() / strategy.std() * np.sqrt(12):.2f}",
    'Max Drawdown': f"{strategy_dd.min():.1%}",
}
stats['SPY'] = {
    'Total Return': f"{spy_curve.iloc[-1] / initial - 1:.1%}",
    'CAGR': f"{(spy_curve.iloc[-1] / initial) ** (1 / years) - 1:.2%}",
    'Annualized Vol': f"{spy.std() * np.sqrt(12):.2%}",
    'Sharpe': f"{spy.mean() / spy.std() * np.sqrt(12):.2f}",
    'Max Drawdown': f"{spy_dd.min():.1%}",
}

print(f"{len(strategy)} months, {years:.1f} years, ${initial:,} start\n")
print(pd.DataFrame(stats).to_string())

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 9), sharex=True)

axes[0].plot(strategy_curve.index, strategy_curve, label='12-1 Momentum', color='r')
axes[0].plot(spy_curve.index, spy_curve, label='SPY', color='k')
axes[0].set_yscale('log')
axes[0].set_title(f"Growth of ${initial:,} — 12-1 Momentum vs SPY")
axes[0].set_ylabel('Portfolio Value (USD, log scale)')
axes[0].legend()

axes[1].plot(strategy_dd.index, strategy_dd, label='12-1 Momentum', color='r')
axes[1].plot(spy_dd.index, spy_dd, label='SPY', color='k')
axes[1].set_title('Drawdown from Peak')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Drawdown')
axes[1].yaxis.set_major_formatter('{x:.0%}')
axes[1].legend()

fig.tight_layout()

os.makedirs('output', exist_ok=True)
fig.savefig('output/tearsheet.png', dpi=150, bbox_inches='tight')

print("\nThree reasons not to trust this:")
print("  1. Survivorship — the universe is today's largest S&P 500 companies, so the")
print("     backtest never holds a company that failed or left the index.")
print("  2. Costs — 0.2% per rebalance is a guess. Real slippage on monthly turnover")
print("     of ten names could be higher.")
print(f"  3. Drawdown — the strategy fell {abs(strategy_dd.min()):.0%} from its peak. Holding")
print("     through that in real time is a different thing from seeing it on a chart.")

plt.show()