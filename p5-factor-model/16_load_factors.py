"""P5 Module 16: read the official Fama-French file and plot factor returns."""
from pathlib import Path
import matplotlib.pyplot as plt
from p5_core import load_ff3

HERE = Path(__file__).resolve().parent
ff = load_ff3(HERE / "data" / "F-F_Research_Data_Factors_CSV.zip")
factors = ff.loc["1990-01":, ["Mkt-RF", "SMB", "HML"]]

ax = (1 + factors).cumprod().plot(figsize=(10, 5), logy=True)
ax.set(title="Growth of $1 in three Fama-French factors since 1990",
       xlabel="Month", ylabel="Cumulative growth (log scale)")
(HERE / "output").mkdir(exist_ok=True)
plt.tight_layout()
plt.savefig(HERE / "output" / "factor_race.png", dpi=150)
plt.close()

for name in factors.columns:
    growth = (1 + factors[name]).rolling(12).apply(lambda x: x.prod(), raw=False) - 1
    print(f"{name}: annualized arithmetic mean {factors[name].mean()*12:.1%}; "
          f"worst 12 months {growth.min():.1%}")