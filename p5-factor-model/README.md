# P5 | Fama-French factor attribution and a luck test

**Work in progress.** A reproducible, code-first extension of [P4 Momentum Backtest](https://github.com/VitheshA/momentum-backtest). Scripts cover dashboard Modules 16–18. No empirical results are claimed until the actual source files have been run through all three scripts.

## Data and method

- **Factor data:** [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html), *Fama/French 3 Factors (monthly, CSV)*. Download the ZIP and supply via `--ff3`. The loader excludes the annual table and divides percentage-point values by 100.
- **P4 prices/holdings:** `momentum-backtest/data/price.csv` and `data/rnk.csv`. Reconstruct next-month monthly returns with the same **0.2% flat monthly rebalance cost** used by P4; no new universe or backtest parameters.
- **SPY and a second asset/ETF:** Supply independently sourced, month-end-adjusted **total** return data as CSV with columns `Date,Return`, where returns are decimals (e.g. `0.03` for 3%). Monthly labels may be month-start or month-end. Do not combine price returns with total-return factor data.
- **Luck machine:** 1,000 seeded random ten-stock portfolios, each evaluated in the same **biased** P4 contemporary universe, with the same next-month timing and cost assumption; no in-sample strategy search. This is a descriptive comparison, not a valid trading-edge test.
- **Regression:** Excess return on FF3 market, size, value + intercept. HAC/Newey-West standard errors at lag 3 (method choice declared rather than disguised); alpha reported as `12 × monthly intercept`. p-values are conditional on the model and data quality.

## Run

```sh
pip install -r requirements.txt
python 16_load_factors.py --ff3 /path/to/F-F_Research_Data_Factors_CSV.zip
python 17_luck_machine.py --p4-prices /path/to/momentum-backtest/data/price.csv --p4-ranks /path/to/momentum-backtest/data/rnk.csv --spy /path/to/spy_monthly.csv
python 18_ff_regression.py --ff3 /path/to/F-F_Research_Data_Factors_CSV.zip --p4-prices /path/to/momentum-backtest/data/price.csv --p4-ranks /path/to/momentum-backtest/data/rnk.csv --asset /path/to/qqq_monthly.csv --asset-name QQQ
python -m pytest -q
```

## Limitations

P4 selects the present-day large-cap universe and runs it backward. This creates **survivorship/selection bias**, so P5's fitted alpha and any random-portfolio percentile cannot establish true strategy skill. The naive SPY difference t-test ignores potential serial correlation; the regression uses HAC uncertainty but is still not a causal, out-of-sample test. ETF adjusted prices should include distributions and need source and sampling details. This project is educational, not investment advice.

## What is left to call P5 complete

1. Fetch source data from official French library and a verifiable SPY/second-asset total-return source.
2. Run the scripts against P4's real cached files, inspect any date/missing-data errors, and preserve reproducibility.
3. Review results and write two original 200–300 word interpretations in `writeup.md`, reporting alpha significance and limitations.
4. Add sourced figures/output and a reviewed report. Do not claim experimental findings until completed.

*AI transparency: The initial scaffolding and tests were assisted by OpenAI GPT-6. They require human review and independent verification before adoption or external submission.*
