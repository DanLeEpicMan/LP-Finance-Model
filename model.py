import numpy as np
import pandas as pd
from scipy.optimize import linprog

AMOUNT_TO_INVEST = 5000


data = pd.read_csv('data.csv', index_col=0)
data['Annual Return'] = data['Annual Return'] + 1
# data['Volatility'] = data['Volatility'] + 1


baskets = list(dict.fromkeys(', '.join(data['Basket'].unique()).split(', ')))
variables = data.index.tolist()

c = -1 * data['Annual Return'].to_numpy(dtype=np.float64)

A = np.empty((len(baskets) + 1, len(variables)), dtype=np.float64)

for i in range(len(baskets)):
    basket = baskets[i]
    for j in range(len(variables)):
        var = variables[j]
        A[i, j] = (1 / data['Confidence'][var]) * data['Volatility'][var] if basket in data['Basket'][var] else 0
        # A[i, j] = (1 / data['Confidence'][var]) if basket in data['Basket'][var] else 0


A[len(baskets)] = np.ones(shape=len(variables), dtype=np.float64)

# "uniform" partition of b
zeros = np.count_nonzero(A, axis=1)
zeros[-1] = 0
b_uniform = zeros * (AMOUNT_TO_INVEST / sum(zeros))
b_uniform[-1] = AMOUNT_TO_INVEST

# "volatile" partition of b
b_volatile = np.empty(shape=len(baskets) + 1, dtype=np.float64)
b_volatile[-1] = AMOUNT_TO_INVEST 

for i in range(len(baskets)):
    average_volatility = data[data['Basket'].str.contains(baskets[i])]['Volatility'].mean()
    b_volatile[i] = (average_volatility) * AMOUNT_TO_INVEST

result = linprog(c, A_ub = A, b_ub = b_volatile)

# print(result)

formatted_result = {}

for i in range(len(variables)):
    formatted_result[data['Name'][variables[i]]] = result.x[i]

print(formatted_result)
# print(b_volatile)

