import pandas as pd
import yfinance as yf
import csv
from datetime import datetime, timedelta
from pytz import timezone
from statistics import stdev


YEARS_TO_MEASURE = 5 # how many years to go back to compute data. either 1, 5, or 10.
START = datetime.now() - timedelta(days = 365 * YEARS_TO_MEASURE) # will be off by a few days due to leap year. this should not be too problematic
CURRENT_MONTH = datetime.now().month # this script WILL not work if ran in December. see 'current_year_data' variable.
NY_TZ = timezone('America/New_York')


securities_table = {}

with open('securities.csv') as securities_file:
    for row in csv.reader(securities_file):
        securities_table[row[0]] = ''.join(row[1:])

roi_data = {}

for basket, list in securities_table.items():
    securities = yf.Tickers(list)
    for name, tick in securities.tickers.items():
        if name in roi_data:
            roi_data[name]['Basket'] = roi_data[name]['Basket'] + f', {basket}'
            continue
        hist = tick.history(period=f'{YEARS_TO_MEASURE}y', interval='1mo', start=f'{START.year}-01-01')
        hist['Average'] = hist[['Open', 'Close']].mean(axis=1)
        annual_returns = []
        confidence = 0
        for i in range(YEARS_TO_MEASURE, 0, -1):
            current_year_data = hist[
                datetime((START + timedelta(days=365 * (i - 1))).year, CURRENT_MONTH - 1, 1, tzinfo=NY_TZ) :
                datetime((START + timedelta(days=365 * i)).year, CURRENT_MONTH, 1, tzinfo=NY_TZ)
            ]
            if current_year_data.empty:
                continue
            
            confidence += len(current_year_data) - 1
            annualized_monthly_return = 1
            for mo in range(1, len(current_year_data)):
                prev_month = current_year_data.iloc[mo-1]
                curr_month = current_year_data.iloc[mo]

                start_of_month = datetime(curr_month.name.year, curr_month.name.month, 1, tzinfo=NY_TZ)
                end_of_month = start_of_month.replace(day=28) + timedelta(days=4)
                end_of_month = end_of_month - timedelta(days=end_of_month.day)
                div = tick.dividends[start_of_month : end_of_month]
                
                annualized_monthly_return *= (curr_month['Average'] + div.sum()) / prev_month['Average']
            annual_returns.append(annualized_monthly_return)
            
        try:
            avg_ann_return = sum(annual_returns) / len(annual_returns)
        except ZeroDivisionError:
            raise ValueError(f'{name} is an invalid security.')
        
        roi_data[name] = {
            'Annual Return': avg_ann_return - 1,
            'Volatility': stdev(annual_returns, xbar=avg_ann_return),
            'Confidence': confidence / (12 * YEARS_TO_MEASURE),
            'Name': tick.info['shortName'],
            'Basket': basket
        }

roi_data = pd.DataFrame(roi_data).T

roi_data.to_csv('data.csv')

print(roi_data)


