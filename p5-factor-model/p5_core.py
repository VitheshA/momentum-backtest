"""Reusable methods for P5; outputs are descriptive, not trading advice."""
from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import ttest_1samp

FACTORS = ["Mkt-RF", "SMB", "HML", "RF"]


def load_ff3(path: str | Path) -> pd.DataFrame:
    """Read Kenneth French's monthly FF3 CSV or ZIP, excluding annual/daily sections.

    Input contains percentages (e.g. 1.5 for 1.5%); output contains decimals.
    Supports altered descriptive preambles and CRLF/UTF-8 BOM.
    """
    path = Path(path)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            matches = [name for name in z.namelist() if name.lower().endswith('.csv')]
            if len(matches) != 1:
                raise ValueError("Expected one CSV in the official Fama-French ZIP")
            raw = z.read(matches[0]).decode("utf-8-sig", errors="replace")
    else:
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = raw.splitlines()
    header = next((i for i, line in enumerate(lines)
                   if re.search(r'\bMkt-RF\b', line) and all(k in line for k in FACTORS)), None)
    if header is None:
        raise ValueError("Could not find FF3 factor header")
    rows = []
    for line in lines[header+1:]:
        cells = [cell.strip() for cell in line.split(',')]
        if re.fullmatch(r'\d{6}', cells[0] if cells else ''):
            if len(cells) < 5:
                raise ValueError("Missing factor values in a monthly row")
            rows.append(cells[:5])
        elif rows:
            break
    if not rows:
        raise ValueError("No monthly factors found")
    frame = pd.DataFrame(rows, columns=['month', *FACTORS])
    months = pd.PeriodIndex(frame.pop('month'), freq='M')
    frame = frame.apply(pd.to_numeric, errors='raise') / 100.0
    frame.index = months
    if frame.isna().any().any() or not frame.index.is_unique or not frame.index.is_monotonic_increasing:
        raise ValueError("Bad factor data: NaN, duplicate months, or unsorted months")
    return frame


def monthly_prices(path: str | Path) -> pd.DataFrame:
    """P4's cached daily adjusted-close matrix -> month-end closes."""
    prices = pd.read_csv(path, index_col='Date', parse_dates=True).sort_index()
    if prices.empty or not prices.index.is_unique:
        raise ValueError("Price data empty or duplicate dates")
    prices = prices.apply(pd.to_numeric, errors='coerce')
    return prices.resample('ME').last()


def momentum_from_p4(price_path: str | Path, holdings_path: str | Path, cost: float = .002) -> tuple[pd.Series, pd.DataFrame]:
    """Rebuild exactly P4's next-month equal-weight held returns, before any FF fit."""
    month_prices = monthly_prices(price_path)
    next_month = month_prices.pct_change(fill_method=None).shift(-1)
    holdings = pd.read_csv(holdings_path, parse_dates=['Date'])
    if not {'Date', 'Ticker'}.issubset(holdings.columns):
        raise ValueError("Holdings must have Date and Ticker columns")
    records = {}
    for date, group in holdings.groupby('Date'):
        date = pd.Timestamp(date)
        tickers = group['Ticker'].tolist()
        if date not in next_month.index:
            raise ValueError(f"Holdings date {date} not in price data")
        missing = sorted(set(tickers).difference(next_month.columns))
        if missing:
            raise ValueError(f"Tickers missing from price data: {missing}")
        ret = next_month.loc[date, tickers]
        if ret.isna().any():
            # Never silently drop missing holdings and re-weight survivors.
            raise ValueError(f"Missing next-month return at {date}")
        records[date.to_period('M')] = float(ret.mean() - cost)
    return pd.Series(records, name='Momentum', dtype=float).sort_index(), next_month.to_period('M')


def random_portfolios(next_month_returns: pd.DataFrame, months: pd.PeriodIndex, *,
                      n_sim: int = 1000, n_hold: int = 10,
                      cost: float = .002, seed: int = 2026) -> pd.DataFrame:
    """Random, equal-weight stock picks per month, all using P4's same biased universe."""
    rng = np.random.default_rng(seed)
    result = np.empty((len(months), n_sim), dtype=float)
    for i, month in enumerate(months):
        row = next_month_returns.loc[month].dropna().to_numpy(float)
        if len(row) < n_hold:
            raise ValueError(f"Only {len(row)} valid assets for {month}")
        # Samples without replacement within a portfolio. Vectorized across trials.
        ranks = rng.random((n_sim, len(row)))
        choices = np.argpartition(ranks, n_hold - 1, axis=1)[:, :n_hold]
        result[i] = row[choices].mean(axis=1) - cost
    return pd.DataFrame(result, index=months)


def annual_sharpe(returns: pd.Series | pd.DataFrame):
    return returns.mean() / returns.std(ddof=1) * np.sqrt(12)


def monthly_return_file(path: str | Path, name: str) -> pd.Series:
    """CSV with Date and Return fields, decimals and monthly dated rows."""
    df = pd.read_csv(path)
    if not {'Date', 'Return'}.issubset(df.columns):
        raise ValueError(f'{path} needs Date,Return columns')
    dates = pd.to_datetime(df['Date'], errors='raise').dt.to_period('M')
    out = pd.Series(pd.to_numeric(df['Return'], errors='raise').to_numpy(float),
                    index=pd.PeriodIndex(dates, freq='M'), name=name)
    if not out.index.is_unique:
        raise ValueError('Duplicate monthly dates')
    return out.sort_index()


def ff_regression(returns: pd.Series, factors: pd.DataFrame):
    """FF3 OLS on excess returns. HAC(3) errors for exploratory monthly data."""
    joined = factors.join(returns.rename('asset'), how='inner').dropna()
    if len(joined) < 24:
        raise ValueError(f'Need >=24 aligned monthly observations, got {len(joined)}')
    y = joined['asset'] - joined['RF']
    x = sm.add_constant(joined[FACTORS[:-1]], has_constant='add')
    model = sm.OLS(y, x).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
    return model, joined


def regression_row(label: str, model, n: int) -> dict:
    def val(key): return float(model.params[key])
    return {'asset': label, 'n_months': n, 'alpha_monthly': val('const'),
            'alpha_ann_arithmetic': val('const') * 12,
            'alpha_t_hac': float(model.tvalues['const']),
            'alpha_p_hac': float(model.pvalues['const']),
            'beta_market': val('Mkt-RF'), 'beta_smb': val('SMB'),
            'beta_hml': val('HML'), 'r_squared': float(model.rsquared)}
