# P5 — Factor Model

Fama-French factor analysis of my [P4 momentum backtest](https://github.com/VitheshA/momentum-backtest), plus 1,000 random-portfolio comparisons.

## Run

Download the monthly **Fama/French 3 Factors CSV ZIP** from [Kenneth French's library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) and save it as `p5-factor-model/data/F-F_Research_Data_Factors_CSV.zip`.

From the `momentum-backtest` repository root:

```bash
pip install -r p5-factor-model/requirements.txt
python p5-factor-model/16_load_factors.py
python p5-factor-model/17_luck_machine.py
python p5-factor-model/18_ff_regression.py
python -m pytest p5-factor-model/tests -q
```

Scripts 17–18 also download SPY prices. Figures and regression tables go in `p5-factor-model/output/`.

## Scripts

- `16_load_factors.py` — factor return chart
- `17_luck_machine.py` — momentum versus random portfolios
- `18_ff_regression.py` — factor regressions for momentum and SPY
- `p5_core.py` — shared functions

## Status and limitations

Source is published and six synthetic tests passed. The complete real-data run and results have **not** been verified.

P4 uses today's large companies in a historical backtest. This creates selection and survivorship bias; neither random-portfolio rankings nor regression alpha establish trading skill.

AI-assisted implementation.
