import numpy as np
import pandas as pd
import scipy.optimize as opt
import yfinance as yf
import csv


securities_str = ''

with open('securities.csv') as securities_file:
    for row in csv.reader(securities_file):
        securities_str += ''.join(row[1:])

securities = yf.Tickers(securities_str)

roi_data = {}

for name, tick in securities.tickers.items():
    hist = tick.history(period='5y', interval='1mo').filter(like='10-01', axis=0)
    annual_return = 0
    counted_years = 0
    for i in range(1, len(hist)):
        prev_row = hist.iloc[i-1]
        curr_row = hist.iloc[i]
        if curr_row.name.year - prev_row.name.year != 1:
            continue
        annual_return += (prev_row['Open'] + prev_row['Close']) / (curr_row['Open'] + curr_row['Close'])
        counted_years += 1
    print(annual_return / counted_years - 1)




opt.linprog


'''
spy = yf.Ticker('GC=F')
print(spy.info['shortName'])
hist = spy.history(period='5y')
'''

