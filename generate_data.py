import pandas as pd
import yfinance as yf
import csv
from datetime import datetime, timedelta
from statistics import stdev


YEARS_TO_MEASURE = 5 # how many years to go back to compute data. either 1, 5, or 10.
START = datetime.now() - timedelta(days = 365 * YEARS_TO_MEASURE) # starting time. 
# will be off by a few days due to leap year, however only year is used. just don't run this around new years.


securities_table = {}

with open('securities.csv') as securities_file:
    for row in csv.reader(securities_file):
        securities_table[row[0]] = ''.join(row[1:])

roi_data = {}

for category, list in securities_table.items():
    securities = yf.Tickers(list)
    for name, tick in securities.tickers.items():
        if name in roi_data:
            roi_data[name]['Category'] = roi_data[name]['Category'] + f', {category}'
            continue

        hist = tick.history(period=f'{YEARS_TO_MEASURE}y', interval='1mo')
        hist['Average'] = hist[['Open', 'Close']].mean(axis=1)
        annual_returns = []
        for i in range(YEARS_TO_MEASURE + 1):
            current_year_data = hist.filter(
                like=str((START + timedelta(days=365 * i)).year),
                axis=0
            )
            if current_year_data.empty:
                continue

            annualized_monthly_return = 1
            for mo in range(1, len(current_year_data)):
                prev_month = current_year_data.iloc[mo-1]
                curr_month = current_year_data.iloc[mo]
                annualized_monthly_return *= curr_month['Average'] / prev_month['Average']
            annual_returns.append(annualized_monthly_return)

        try:
            avg_ann_return = sum(annual_returns) / len(annual_returns)
        except ZeroDivisionError:
            raise ValueError(f'{name} is an invalid security.')
        
        roi_data[name] = {
            'Annual Return': avg_ann_return - 1,
            'Volatility': stdev(annual_returns, xbar=avg_ann_return),
            'Name': tick.info['shortName'],
            'Category': category
        }

roi_data = pd.DataFrame(roi_data).T

roi_data.to_csv('data.csv')

print(roi_data)


