"""P5 Module 18: FF3 on P4 momentum and a user-supplied second asset or ETF."""
import argparse
from pathlib import Path
import pandas as pd
from p5_core import (load_ff3, momentum_from_p4, monthly_return_file,
                     ff_regression, regression_row)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ff3', required=True)
    p.add_argument('--p4-prices', required=True)
    p.add_argument('--p4-ranks', required=True)
    p.add_argument('--asset', required=True, help='Second asset CSV with Date,Return decimals')
    p.add_argument('--asset-name', default='ETF')
    p.add_argument('--out', default='output')
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    factors = load_ff3(args.ff3)
    momentum, _ = momentum_from_p4(args.p4_prices, args.p4_ranks)
    second = monthly_return_file(args.asset, args.asset_name)
    results = []
    for name, series in [('12-1 Momentum', momentum), (args.asset_name, second)]:
        model, joined = ff_regression(series, factors)
        print(f'\n### {name} ({len(joined)} months)\n{model.summary()}')
        results.append(regression_row(name, model, len(joined)))
    table = pd.DataFrame(results)
    table.to_csv(out/'results_table.csv', index=False)
    print('\n', table.to_string(index=False))
    print('\nHAC(3) robust standard errors; alpha conditional on chosen FF3 specification.')
    print('P4 uses a current-day selected stock universe: observed alpha is NOT an unbiased trading edge estimate.')


if __name__ == '__main__': main()
