import nsepy
import datetime as dt
import yfinance as yf
from talib import abstract
import matplotlib.pyplot as plt

data_groups = yf.download('AMRUTANJAN.BO',start='2024-03-25', interval ='1m').groupby(lambda x:x.strftime('%Y-%m-%d'))

for d in data_groups:
    print(d[1].Close.plot())
    df= d[1]
    df['close'] = df['Close']
    ma=abstract.SMA(df, timeperiod=25)
    plt.plot(ma)
    plt.show()
