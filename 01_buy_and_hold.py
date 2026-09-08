import os

import pandas as pd
import yfinance as yf
from matplotlib import pyplot as plt

initial = 10000

spy = yf.download('SPY', period='15y', auto_adjust=True)['Close']['SPY']
monthly_close = spy.resample('ME').last()
monthly_return = monthly_close.pct_change().dropna()

curve = (1 + monthly_return).cumprod() * initial
final_amt = curve.iloc[-1]

years = (curve.index[-1] - curve.index[0]).days / 365.25
CAGR = (final_amt / initial) ** (1 / years) - 1

print(f"{len(monthly_return)} months, {years:.1f} years")
print(f"Final amount: ${final_amt:,.2f}")
print(f"CAGR: {CAGR:.2%}")

# cross-check against the daily-data method from Module 05
daily_return = spy.pct_change().dropna()
daily_curve = (1 + daily_return).cumprod() * initial
daily_CAGR = (daily_curve.iloc[-1] / initial) ** (1 / years) - 1
print(f"CAGR from daily data: {daily_CAGR:.2%}")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(curve.index, curve, color='k')
ax.set_yscale('log')  # log scale so 2010 and 2025 moves are visually comparable
ax.set_title(f"SPY Buy and Hold — Growth of ${initial:,}")
ax.set_xlabel('Date')
ax.set_ylabel('Portfolio Value (USD, log scale)')

fig.tight_layout()

os.makedirs('output', exist_ok=True)
fig.savefig('output/buy_and_hold.png', dpi=150, bbox_inches='tight')
plt.show()
