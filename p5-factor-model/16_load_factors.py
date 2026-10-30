"""P5 Module 16: plot historical Fama-French factors from the official CSV."""
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from p5_core import load_ff3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ff3', required=True, help='Official F-F_Research_Data_Factors_CSV.zip or unzipped CSV')
    parser.add_argument('--out', default='output')
    args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    data = load_ff3(args.ff3)
    # The source begins July 1926, not January; do not assert incorrect full-year start.
    if data.index[0].year != 1926:
        raise ValueError('Expected factors beginning in 1926')
    factors = data.loc['1990-01':, ['Mkt-RF', 'SMB', 'HML']]
    wealth = (1 + factors).cumprod()
    ax = wealth.plot(logy=True, figsize=(10, 5), title='Illustrative $1 compounded in FF3 factor returns since 1990')
    ax.set_ylabel('Compound factor return ($1 initial, log scale)')
    ax.set_xlabel('Month')
    ax.figure.tight_layout(); ax.figure.savefig(out/'factor_race.png', dpi=170)
    plt.close(ax.figure)
    for name, r in factors.items():
        year_mean = float(r.mean() * 12)
        rolling = ((1 + r).rolling(12).apply(np.prod, raw=True) - 1).dropna()
        print(f'{name:6s} mean annualized (arithmetic): {year_mean:+.2%}; worst 12 months: {rolling.min():+.2%}')
    print(f'Months: {len(data)}; saved {out/"factor_race.png"}')


if __name__ == '__main__': main()
