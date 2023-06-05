import numpy as np
import pandas as pd
from scipy.optimize import linprog

AMOUNT_TO_INVEST = 5000


data = pd.read_csv('data.csv', index_col=0)
data['Annual Return'] = data['Annual Return'] + 1
#data['Volatility'] = data['Volatility'] + 1


baskets = list(dict.fromkeys(', '.join(data['Basket'].unique()).split(', ')))
variables = data.index.tolist()

c = -1 * np.append(data['Annual Return'].to_numpy(dtype=np.float64), 1) 

A = np.zeros((len(baskets), len(variables) + 1), dtype=np.float64)

for i in range(len(baskets)):
    basket = baskets[i]
    for j in range(len(variables)):
        var = variables[j]
        A[i, j] = (1 / data['Confidence'][var]) * (1 + data['Volatility'][var]) if basket in data['Basket'][var] else 0
        #A[i, j] = (1 / data['Confidence'][var]) * (data['Volatility'][var]) if basket in data['Basket'][var] else 0


# "uniform" partition of b
zeros = np.count_nonzero(A, axis=1)
b_uniform = zeros * (AMOUNT_TO_INVEST / sum(zeros))

# "volatile" partition of b
b_volatile = np.empty(shape=len(baskets), dtype=np.float64)
for i in range(len(baskets)):
    average_volatility = data[data['Basket'].str.contains(baskets[i])]['Volatility'].mean()
    b_volatile[i] = (1 / (1 + average_volatility)) * AMOUNT_TO_INVEST

result = linprog(c, 
                 A_ub = A, 
                 b_ub = b_volatile, 
                 A_eq=np.ones(shape=(1, len(c)), dtype=np.float64), 
                 b_eq=np.array(AMOUNT_TO_INVEST)
            )

formatted_result = {'Total to Invest': AMOUNT_TO_INVEST - result.x[-1], 'New Balance': -1 * result.fun}

for i in range(len(variables)):
    if result.x[i] != 0:
        formatted_result[data['Name'][variables[i]]] = result.x[i]

print(formatted_result)
