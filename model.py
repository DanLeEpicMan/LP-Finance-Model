import numpy as np
import pandas as pd
from scipy.optimize import linprog

AMOUNT_TO_INVEST = 5000


data = pd.read_csv('data.csv', index_col=0)
data['Annual Return'] = data['Annual Return'] + 1
data['Volatility'] = data['Volatility'] + 1


categories = list(dict.fromkeys(', '.join(data['Category'].unique()).split(', ')))
variables = data.index.tolist()

c = -1 * data['Annual Return'].to_numpy(dtype=np.float64)

A = np.empty((len(categories) + 1, len(data)), dtype=np.float64)

for i in range(len(categories)):
    category = categories[i]
    for j in range(len(variables)):
        var = variables[j]
        A[i, j] = data['Volatility'][var] if category in data['Category'][var] else 0

A[len(categories)] = np.ones(shape=len(variables), dtype=np.float64)

zeros = np.count_nonzero(A, axis=1)
zeros[-1] = 0
b = zeros * (AMOUNT_TO_INVEST / sum(zeros))
b[-1] = AMOUNT_TO_INVEST


result = linprog(c, A_ub = A, b_ub = b)

formatted_result = {}

for i in range(len(variables)):
    formatted_result[variables[i]] = result.x[i]

print(formatted_result)