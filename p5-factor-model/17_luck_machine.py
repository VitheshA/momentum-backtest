"""P5 Module 17: 1,000 random portfolios vs P4 momentum, same sample + costs."""
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.stats import ttest_1samp
from p5_core import (momentum_from_p4, random_portfolios,
                     annual_sharpe, monthly_return_file)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--p4-prices', required=True)
    p.add_argument('--p4-ranks', required=True)
    p.add_argument('--spy', required=True, help='CSV Date,Return (decimal) of monthly SPY total returns')
    p.add_argument('--out', default='output')
    args = p.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    strategy, forward = momentum_from_p4(args.p4_prices, args.p4_ranks)
    monkey = random_portfolios(forward, strategy.index)
    ranks = annual_sharpe(monkey)
    strategy_sharpe = annual_sharpe(strategy)
    percentile = float((ranks < strategy_sharpe).mean() * 100)
    ax = ranks.plot.hist(bins=35, figsize=(9, 5), title='1,000 random portfolios (same contemporary-universe bias)')
    ax.axvline(strategy_sharpe, color='black', label=f'Momentum Sharpe {strategy_sharpe:.2f}')
    ax.set_xlabel('Annualized Sharpe'); ax.legend()
    ax.figure.tight_layout(); ax.figure.savefig(out/'luck_machine.png', dpi=170)
    plt.close(ax.figure)
    spy = monthly_return_file(args.spy, 'SPY')
    aligned = strategy.to_frame().join(spy, how='inner')
    if len(aligned) != len(strategy):
        raise ValueError('SPY monthly returns do not cover every momentum month')
    test = ttest_1samp(aligned['Momentum'] - aligned['SPY'], 0.0)
    print(f'Momentum Sharpe: {strategy_sharpe:.3f}, randomized percentile: {percentile:.1f}%')
    print(f'Monthly momentum minus SPY, naive t={test.statistic:.3f}, p={test.pvalue:.4f}, n={len(aligned)}')
    print('Caution: overlapping effects/serial correlation and selection invalidate simple causal/skill claims.')
    aligned.to_csv(out/'aligned_returns.csv', index_label='Date')


if __name__ == '__main__': main()
