# P5 interpretation draft worksheet

**Status:** No real-data regressions have been run in this environment. Do not fill in invented alpha, beta, or p-values.

## A. P4 momentum strategy (200–300 words, write after results)

Dataset period: [start/end] · Months: [n] · Source: P4 cached daily prices and rankings.

- Alpha monthly: [value], annualized arithmetic: [value], HAC(3) t-stat: [value], p-value: [value].
- Beta market: [value], SMB: [value], HML: [value], R-squared: [value].
- Explain market, size, value exposures **in this specified model**. Do not imply causality.
- Required sentence: *"The alpha is / is not statistically distinguishable from zero because ..."*
- Acknowledge hindsight universe selection, nonhistorical constituent membership, fees/cost assumption, one regime.

## B. Second asset / ETF (200–300 words, write after results)

Source of adjusted total returns: [source] · Sample: [start/end].

- Alpha monthly: [value], annualized arithmetic: [value], HAC(3) t-stat: [value], p-value: [value].
- Factor loadings and interpretation: [write your own explanation].
- Required sentence: *"The alpha is / is not statistically distinguishable from zero because ..."*
- Caution: model dependence, missing factors (momentum), sampling and inference assumptions.

## C. Null-strategy experiment

Percentile of momentum Sharpe vs 1,000 random portfolios: [value].
Naive momentum-minus-SPY one-sample t-test: t=[value], p=[value].
This is **not** a corrected multiple-testing result. Explain why the randomized universe is also survivorship-biased.
