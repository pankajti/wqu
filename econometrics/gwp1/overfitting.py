from sklearn.linear_model import LinearRegression
import numpy as np
from pandas_datareader.wb import WorldBankReader
import pandas_datareader.wb as w

w.download()
y = np.array([1,   4 , 8 , 17 , 24, 34])
x= range(1, len(y)+1)
X = np.array([[a] for a in x])
regrssion_lin = LinearRegression()
res_lin = regrssion_lin.fit(X, y)

