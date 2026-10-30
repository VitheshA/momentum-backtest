"""P5 Module 18: factor regression for P4 momentum and SPY."""
from pathlib import Path
import pandas as pd
import yfinance as yf
from p5_core import load_ff3, momentum_from_p4, ff_regression, regression_row

HERE = Path(__file__).resolve().parent
P4 = HERE.parent / "data"
factors = load_ff3(HERE / "data" / "F-F_Research_Data_Factors_CSV.zip")
momentum, _ = momentum_from_p4(P4 / "price.csv", P4 / "rnk.csv")
spy = yf.download("SPY", start="2010-01-01", auto_adjust=True, progress=False)["Close"]
if isinstance(spy, pd.DataFrame):
    spy = spy.iloc[:, 0]
spy = spy.resample("ME").last().pct_change().dropna()
spy.index = spy.index.to_period("M")

results = []
for name, returns in [("P4 momentum", momentum), ("SPY", spy)]:
    model, aligned = ff_regression(returns, factors)
    print(f"\n{name}: {len(aligned)} months\n{model.summary()}")
    results.append(regression_row(name, model, len(aligned)))

out = HERE / "output"
out.mkdir(exist_ok=True)
table = pd.DataFrame(results)
table.to_csv(out / "results_table.csv", index=False)
print("\n", table.to_string(index=False))
print("Alpha is a model intercept, NOT evidence of trading skill due to P4 universe bias.")