import os.path

import pandas as pd
import numpy as np
import pytz
import sqlite3
import sqlalchemy
import matplotlib.pyplot as plt
import plotly.express as px
import json

#Brokerage = .03 Ignore for present analysis

# https://zerodha.com/charges/#tab-equities

STT = 0.025/100
TC= .00322/100
GST= TC*.18

total_charges = STT + TC+GST


def main():
    data_output_dir = r'/Users/pankajti/dev/git/wqu/capstone/data/trading_output'
    db_data_path = r'/Users/pankajti/dev/git/wqu/capstone/data/db/capstone.db'
    con = sqlite3.connect(db_data_path)
    dbEngine = sqlalchemy.create_engine(f'sqlite:///{db_data_path}')
    versions = pd.read_sql("select * from version_info vi where version_no  >= 1715023716 ", dbEngine)
    versions=versions.set_index('version_no')
    for version, run_info in versions.iterrows():
        run_info_dict  = json.loads(run_info[0].replace("'", '"'))

        trades = pd.read_sql(f"select * from trades where strategy ='opening_range_breakout' and version = {version} ",
                             dbEngine)
        trades['tdate'] = trades.trade_time.str[:10]
        trades.to_csv(os.path.join(data_output_dir, "trades.csv"))
        trades_data = trades[['tdate', 'ticker', 'side', 'quantity', 'price']]
        trades_data['price'] = trades_data.price.astype(float)
        trades_data['side'] = trades_data.side.apply(lambda x: '-1' if x == 'sell' else x)
        trades_data = trades_data.pivot_table(index=['tdate', 'ticker'], columns=['side'], values=['price'])
        trades_data = trades_data.T.reset_index().T.reset_index()[2:].rename({0: 'buy', 1: 'sell'}, axis=1).dropna()
        trades_data['ret'] = (trades_data.sell - trades_data.buy) / trades_data.buy
        trades_data['ret_perc'] = 100 * ((trades_data.sell - trades_data.buy) / trades_data.buy)
        trades_data['tc'] = total_charges * (trades_data.buy + trades_data.sell)
        trades_data['ret_perc_ac'] = 100 * ((trades_data.sell - trades_data.buy - trades_data.tc) / trades_data.buy)
        trades_data.to_csv(os.path.join(data_output_dir, "trades_data.csv"))


        daily_perfoemance = trades_data.groupby('tdate').sum()[['buy', 'sell', 'tc']]
        daily_perfoemance['per_ret_bc'] = 100 * ((daily_perfoemance.sell - daily_perfoemance.buy) / daily_perfoemance.buy)
        daily_perfoemance['per_ret_ac'] = 100 * ((daily_perfoemance.sell - daily_perfoemance.buy - daily_perfoemance.tc) / daily_perfoemance.buy)
        daily_perfoemance['hit_ratio'] = trades_data.groupby('tdate').ret_perc_ac.apply(lambda col: sum(col>0)/len(col))
        cum_ret_bc = (1 + daily_perfoemance.per_ret_ac / 100).cumprod()
        cum_ret_bc = (1 + daily_perfoemance.per_ret_bc).cumprod()
        sharpe_ratio = daily_perfoemance.per_ret_ac.mean() / daily_perfoemance.per_ret_ac.std()
        h_ratio =  sum(trades_data.per_ret_ac>0)/len(trades_data.per_ret_ac)
        print(f" Sharpe ratio::  {sharpe_ratio}")

if __name__ == '__main__':
    main()