import schedule
import time
import datetime as dt
import logging
import pandas as pd
import numpy as np
import pytz
import time
import sqlite3
import sqlalchemy

version = int(time.time())
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("Log initiated ")


db_data_path = r'/Users/pankajti/dev/git/wqu/capstone/data/db/capstone.db'
con = sqlite3.connect(db_data_path)
dbEngine = sqlalchemy.create_engine(f'sqlite:///{db_data_path}')

class OrbSignal():
    def __init__(self, market_data, open_interval = 35):
        self.market_data_close = market_data.pivot_table(index='timestamp', columns='ticker', values='Close').fillna(
            method='ffill')
        self.min_df = self.market_data_close[:open_interval].min().dropna()
        self.min_df.name='min_val'
        self.max_df = self.market_data_close[:open_interval].max().dropna()
        self.max_df.name='max_val'


    def get_signals(self, minute_candle):
        timestamp = minute_candle.index.max()
        ticker_prices=minute_candle.loc[timestamp][['ticker', 'Close']].set_index('ticker')
        data = ticker_prices.join(self.min_df).join(self.max_df)
        data['buy']=data.apply(lambda x : 1 if x['Close']>x['max_val'] else 0, axis =1)
        data['sell']=data.apply(lambda x : 1 if x['Close']<x['min_val'] else 0, axis =1)
        data['side'] = data.buy+-1*data.sell
        data=data[data.side!=0]
        data['trade_time']=timestamp
        ret_signals = data.reset_index()[['trade_time', 'ticker', 'side', 'Close']]
        ret_signals.columns = ['trade_time', 'ticker', 'side', 'price']
        return ret_signals


        print(data)

def get_signals(market_data):
    print(market_data.shape)

def main():
    md= pd.read_sql("select * from market_data where date = '2024-03-27'", dbEngine)
    orb_signal= OrbSignal(md)
    orb_signal.get_signals(minute_candle=md)

if __name__ == '__main__':
    main()