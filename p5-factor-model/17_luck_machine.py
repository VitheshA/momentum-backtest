"""P5 Module 17: compare P4 momentum with 1,000 random portfolios."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from scipy.stats import ttest_1samp
from p5_core import momentum_from_p4, random_portfolios, annual_sharpe

HERE = Path(__file__).resolve().parent
P4 = HERE.parent / "data"
strategy, next_returns = momentum_from_p4(P4 / "price.csv", P4 / "rnk.csv")
random_returns = random_portfolios(next_returns, strategy.index)
random_sharpes = annual_sharpe(random_returns)
strategy_sharpe = annual_sharpe(strategy)
percentile = 100 * (random_sharpes < strategy_sharpe).mean()

ax = random_sharpes.hist(bins=30, figsize=(9, 5))
ax.axvline(strategy_sharpe, color="black", label="P4 momentum")
ax.set(title="P4 versus 1,000 random portfolios", xlabel="Sharpe ratio")
ax.legend()
(HERE / "output").mkdir(exist_ok=True)
plt.tight_layout()
plt.savefig(HERE / "output" / "luck_machine.png", dpi=150)
plt.close()

spy = yf.download("SPY", start="2010-01-01", auto_adjust=True, progress=False)["Close"]
if isinstance(spy, pd.DataFrame):
    spy = spy.iloc[:, 0]
spy_monthly = spy.resample("ME").last().pct_change().dropna()
spy_monthly.index = spy_monthly.index.to_period("M")
comparison = pd.concat([strategy, spy_monthly.rename("SPY")], axis=1).reindex(strategy.index)
if comparison.isna().any().any():
    raise ValueError("SPY has missing months; do not interpret an incomplete comparison")
t, p = ttest_1samp(comparison["Momentum"] - comparison["SPY"], 0)
print(f"Momentum Sharpe: {strategy_sharpe:.2f}; above {percentile:.1f}% of random portfolios")
print(f"Naive monthly P4-minus-SPY t={t:.2f}, p={p:.3f}; this is NOT evidence of real skill")
print("Important: the P4 stock universe was selected with hindsight.")