# P5 | Factor Model

This extends my [P4 momentum backtest](https://github.com/VitheshA/momentum-backtest). It uses the same cached P4 price and holdings data to study factor exposures and compare its apparent returns with random portfolios.

## Run it

1. Download **Fama/French 3 Factors — monthly CSV ZIP** from [Kenneth French's Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).
2. Put the file at `p5-factor-model/data/F-F_Research_Data_Factors_CSV.zip`.
3. From the `momentum-backtest` repo root, run:

```bash
pip install -r p5-factor-model/requirements.txt
python p5-factor-model/16_load_factors.py
python p5-factor-model/17_luck_machine.py
python p5-factor-model/18_ff_regression.py
python -m pytest p5-factor-model/tests -q
```

Scripts 17–18 also download adjusted SPY prices from Yahoo Finance, so you need an internet connection. Outputs are saved in `p5-factor-model/output/`.

## What the files do

- `16_load_factors.py`: plots Fama-French market, size and value factors since 1990.
- `17_luck_machine.py`: tests P4 versus 1,000 random equal-weight ten-stock portfolios and performs a basic SPY comparison.
- `18_ff_regression.py`: runs three-factor regressions for P4 and SPY and saves the coefficients.
- `p5_core.py`: reusable parsing and statistics, with six synthetic-data tests.
- `writeup.md`: questions to answer after running the real data.

## Limits

P4's universe consists of large companies selected **today** and carried backward. That introduces severe survivorship and selection bias. Random portfolios are drawn from that same biased universe, so their rankings do not measure real skill. Positive regression alpha is conditional on a chosen factor specification and **does not repair the underlying dataset**.

**Current status:** Code published with six passing synthetic tests. I have not verified the complete real-data run with the official factor ZIP, the P4 files and Yahoo Finance in one environment. Numerical findings and write-up remain pending.

The implementation was AI-assisted. Review and understand the code, inputs, and results before describing it as personally completed independent research.