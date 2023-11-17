import pandas_datareader as pdr
import pandas as pd
pd.DataFrame().dropna()
symbol=''

ff_reader = pdr.famafrench.FamaFrenchReader(symbol)