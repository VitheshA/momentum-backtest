import importlib.util
import numpy as np
import pandas as pd
import pytest
from p5_core import (load_ff3, random_portfolios, ff_regression,
                     regression_row, momentum_from_p4)


def test_ff3_parser_stops_before_annual_and_converts_percent(tmp_path):
    file = tmp_path/'FF.csv'
    file.write_text('explanations\nmore\n,Mkt-RF,SMB,HML,RF\n192607, 2.5, 0.8, -0.4, 0.1\n192608, -1.0, 0.6, 0.2, 0.1\n\n Annual Factors\n1927,3.2,1,1,0.1\n')
    data = load_ff3(file)
    assert len(data) == 2 and data.index[0] == pd.Period('1926-07', freq='M')
    assert np.isclose(data.iloc[0]['Mkt-RF'], .025)
    assert np.isclose(data.iloc[0]['RF'], .001)


def test_ff3_parser_zip(tmp_path):
    import zipfile
    file = tmp_path/'FF.zip'
    with zipfile.ZipFile(file, 'w') as z:
        z.writestr('FF.CSV', ',Mkt-RF,SMB,HML,RF\n192607,2,1,2,0.2\n')
    assert np.isclose(load_ff3(file)['RF'].iloc[0], .002)


def test_momentum_one_month_shift_and_fixed_cost(tmp_path):
    ix = pd.to_datetime(['2025-01-31','2025-02-28','2025-03-31'])
    prices = pd.DataFrame({'AAA':[100,110,99],'BBB':[100,120,130]}, index=ix)
    prices.index.name='Date'
    price_path=tmp_path/'price.csv'; prices.to_csv(price_path)
    ranks=tmp_path/'rnk.csv'; ranks.write_text('Date,Ticker\n2025-01-31,AAA\n2025-02-28,BBB\n')
    series, fwd = momentum_from_p4(price_path, ranks, cost=.002)
    assert np.isclose(series.iloc[0], .098)
    assert np.isclose(series.iloc[1], 130/120-1-.002)
    assert list(fwd.index) == list(series.index) + [pd.Period('2025-03','M')]


def test_random_portfolios_reproducible_and_costs():
    months = pd.period_range('2025-01', periods=3, freq='M')
    fwd = pd.DataFrame(np.tile([.05,.03,.01,-.01], (3,1)), index=months)
    a = random_portfolios(fwd, months, n_sim=100, n_hold=2, seed=4)
    b = random_portfolios(fwd, months, n_sim=100, n_hold=2, seed=4)
    pd.testing.assert_frame_equal(a,b)
    assert ((a.values <= .05) & (a.values >= -.012)).all()


def test_regression_recovers_known_exposures():
    rng = np.random.default_rng(42)
    months = pd.period_range('2019-01', periods=120, freq='M')
    ff = pd.DataFrame({'Mkt-RF': rng.normal(.006,.04,120), 'SMB': rng.normal(.001,.02,120),
                       'HML': rng.normal(.002,.025,120), 'RF': np.full(120,.002)},index=months)
    r = .002 + ff['RF'] + 1.2*ff['Mkt-RF'] + .35*ff['SMB'] - .4*ff['HML']
    model, join=ff_regression(r.rename('synthetic'), ff)
    assert np.isclose(model.params['const'], .002, atol=1e-10)
    assert np.isclose(model.params['Mkt-RF'], 1.2, atol=1e-10)
    assert np.isclose(model.params['SMB'], .35, atol=1e-10)
    assert np.isclose(model.params['HML'], -.4, atol=1e-10)
    assert regression_row('mock',model,len(join))['n_months']==120


def test_regression_rejects_too_few_months():
    months = pd.period_range('2025-01', periods=5, freq='M')
    ff = pd.DataFrame(np.zeros((5,4)),index=months,columns=['Mkt-RF','SMB','HML','RF'])
    with pytest.raises(ValueError, match='>=24'):
        ff_regression(pd.Series(np.zeros(5),index=months),ff)
