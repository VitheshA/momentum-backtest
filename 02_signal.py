import os

import pandas as pd
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta

end_date_obj = date.today()
start_date_obj = end_date_obj - relativedelta(years=11)
start_date1 = start_date_obj.strftime("%Y-%m-%d")
end_date1 = end_date_obj.isoformat() 
stocks = pd.read_csv("data/universe.csv")
stocks = stocks.sort_values(by='marketCap', ascending=False).head(100)
tickers = stocks['ticker'].astype(str).tolist()
stocks_daily = yf.download(tickers=tickers, start=start_date1, end=end_date1)['Close']
os.makedirs('data', exist_ok=True)
stocks_daily.to_csv('data/price.csv')
stocks_monthly = stocks_daily.resample('ME').last()
momentum = ((stocks_monthly.shift(1)/stocks_monthly.shift(12))-1)
momentum = momentum.stack().reset_index()
momentum.columns = ['Date','Ticker', 'Momentum']
momentum = momentum.sort_values(by=['Date', 'Momentum'], ascending=[True, False]).dropna()
momentum_rnk = momentum.groupby('Date').head(10)
momentum_rnk['rank'] = momentum_rnk.groupby('Date')['Momentum'].rank(ascending=False).astype(int)
momentum_rnk = momentum_rnk[['Date', 'rank', 'Ticker', 'Momentum']]
momentum_rnk.to_csv('data/rnk.csv', index=False)
last3= momentum_rnk.tail(30)
print(last3)

