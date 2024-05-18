import schedule
import datetime as dt
import logging
import pandas as pd
import numpy as np
import pytz
import time
import sqlite3
import sqlalchemy
#from capstone.breakout_trading_system.signals.intraday.price_breakout import get_signals
from  capstone.breakout_trading_system.signals.intraday.open_range_breakout import OrbSignal
from itertools import combinations

# Configurations Externalize these

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.info("Log initiated ")
version = int(time.time())
strategy = 'opening_range_breakout'
write_to_db = True
side_map = {'buy': 1, 'sell': -1, 'hold': 0}
rev_side_map = {v: k for k, v in side_map.items()}
trade_interval = 60
market_close_time = '15:00:00'
db_data_path = r'/Users/pankajti/dev/git/wqu/capstone/data/db/capstone.db'
con = sqlite3.connect(db_data_path)
dbEngine = sqlalchemy.create_engine(f'sqlite:///{db_data_path}')
cache_initialized = False
market_data_dict = dict()
signal_generator = None
loaded_dates = sorted(list(pd.read_sql("select date from market_data", dbEngine)['date'].unique()))


class OrbTradingSystem:

    def __init__(self,stop_loss_limit = .05,take_profit_cap = .2,open_interval=35):
        self.stop_loss_limit=stop_loss_limit
        self.take_profit_cap=take_profit_cap
        self.open_interval=open_interval

    def read_market_data_from_file(self, univers, fromtime, to_time):
        LOGGER.info("started reading market data")
        minute_data_path = r'../data/minute_data.csv'
        minute_data = pd.read_csv(minute_data_path, index_col=0)
        minute_data = minute_data[minute_data.ticker.isin(univers)]
        minute_data['ts'] = list(
            pd.to_datetime(minute_data.reset_index()['index']).apply(lambda x: x.strftime('%Y%m%d%H%M')))
        ret_min_data = minute_data[(minute_data.ts < to_time) & (minute_data.ts >= fromtime)]
        ret_min_data['date'] = list(map(lambda x: x.strftime('%Y-%m-%d'), pd.to_datetime(ret_min_data.index)))
        return ret_min_data


    def read_market_data_from_db(self,univers, fromtime, to_time, tdate):
        global market_data_dict
        global cache_initialized
        global signal_generator
        if tdate not in market_data_dict.keys():
            market_data = self._read_market_data_from_db(tdate)
            cache_initialized = True
            market_data_dict.clear()
            market_data_dict[tdate] = market_data
            signal_generator = OrbSignal(market_data,self.open_interval)

        market_data = market_data_dict[tdate]
        LOGGER.info(f"market data present and initialized {market_data.shape}")

        minute_data = market_data[market_data.ticker.isin(univers)]
        minute_data['ts'] = list(
            pd.to_datetime(minute_data.reset_index()['timestamp']).apply(lambda x: x.strftime('%Y%m%d%H%M')))
        ret_min_data = minute_data[(minute_data.ts < to_time) & (minute_data.ts >= fromtime)]
        ret_min_data['date'] = list(map(lambda x: x.strftime('%Y-%m-%d'), pd.to_datetime(ret_min_data.index)))
        return ret_min_data

    def _read_market_data_from_db(self,tdate):
        LOGGER.info("started reading market data")

        minute_data = pd.read_sql("select * from market_data where date ='{}'".format(tdate), con=dbEngine,
                                  index_col='timestamp')

        return minute_data

    def load_universe(self,num_recs=10000):
        LOGGER.info("started loading universe ")
        tickers_path = '/Users/pankajti/dev/git/wqu/capstone/module4/MCAP31122023_0.xlsx'
        tickers_data = pd.read_excel(tickers_path, nrows=2189)
        yahoo_symbs = tickers_data.Symbol + '.NS'
        yahoo_symbs = yahoo_symbs.dropna().tolist()[:num_recs]
        return yahoo_symbs

    def create_positions(self,signals, candle_data):
        LOGGER.info("creating positions ")
        positions = signals[['trade_time', 'ticker', 'side', 'price']]
        positions['quantity'] = 1
        return positions

    def get_current_inventory(self,trade_date):
        LOGGER.info("started loading existing inventory")

        inventory_path = r'/Users/pankajti/dev/git/wqu/capstone/data/inventory.csv'
        inventory = pd.read_csv(inventory_path)
        return inventory

    def calculate_trade_quantity_no_short_selling(self,m_inv):
        side_x = m_inv['side_x']
        side_y = m_inv['side_y']

        side_x = side_map[side_x] if type(side_x) == str else side_x
        side_y = side_map[side_y] if type(side_y) == str else side_y

        ## if it is buy signal and we already have positions skip it
        if side_x == 1 and m_inv['quantity_y'] > 0:
            return 0
        ## if it is buy signal and we don't have positions buy it
        elif side_x == 1 and m_inv['quantity_y'] == 0:
            return 1
        ## if it is sell signal and we have positions sell it

        elif side_x == -1 and m_inv['quantity_y'] > 0:
            return 1
        ## if it is sell signal and we don't have positions don't do anything

        else:
            return 0

    def calculate_model_inventory(self,actual_inventory, positions):
        LOGGER.info("calculate model inventory from currency amount positions ")
        model_inventory = positions.merge(actual_inventory, how='left', on='ticker').fillna(0)
        model_inventory['quantity'] = model_inventory.apply(self.calculate_trade_quantity_no_short_selling, axis=1)
        # model_inventory['quantity'] = ((model_inventory.side_x.apply(lambda x:side_map[x] if type(x)==str else x) * model_inventory.quantity_x)
        #                          +(model_inventory.side_y.apply(lambda x:side_map[x] if type(x)==str else x) * model_inventory.quantity_y))
        model_inventory['side'] = model_inventory['side_x']
        return model_inventory

    def apply_stop_loss_and_take_profit(self,trades, actual_inventory, candle_data):
        most_recent = candle_data.sort_index(ascending=False).index[0]
        latest_candle_data = candle_data[(candle_data.reset_index()['timestamp'] == most_recent).tolist()]

        current_candle_on_actual_position = actual_inventory.merge(latest_candle_data)
        if len(current_candle_on_actual_position) > 0:
            filter_candles_sl = ((current_candle_on_actual_position.Close <
                                  current_candle_on_actual_position.avg_price * (1 - self.stop_loss_limit)) |
                                 (current_candle_on_actual_position.Close >
                                  current_candle_on_actual_position.avg_price * (1 + self.take_profit_cap)))
            stop_loss_pos = current_candle_on_actual_position[filter_candles_sl]
            stop_loss_pos = stop_loss_pos[['ticker', 'side', 'Close', 'quantity']]
            stop_loss_pos = stop_loss_pos.rename({'Close': 'price'}, axis=1)

            stop_loss_pos['trade_time'] = most_recent
            stop_loss_pos['side'] = 'sell'

            new_trades = pd.concat([trades, stop_loss_pos])
            print("Executed SL/TP ")
            return new_trades

        LOGGER.info("Applying stop loss on the  losing trades")
        return trades

    def calculate_trades(self,model_inventory, candle_data, actual_inventory=None):
        LOGGER.info("calculating trade list based on the model and actual inventory")
        trades = model_inventory[['trade_time', 'ticker', 'side', 'price', 'quantity']]
        if actual_inventory is not None:
            trades = self.apply_stop_loss_and_take_profit(trades, actual_inventory, candle_data)
        trades = trades[trades.quantity != 0]
        existing_trades = pd.read_csv(r'/Users/pankajti/dev/git/wqu/capstone/data/trades.csv')
        all_trades = pd.concat([existing_trades, trades])
        all_trades.to_csv(r'/Users/pankajti/dev/git/wqu/capstone/data/trades.csv', index=False)
        trades['strategy'] = strategy
        trades['creatime'] = dt.datetime.now()
        trades['version'] = version
        if write_to_db:
            trades.to_sql(con=dbEngine, name='trades', index=False, if_exists='append')

        return trades

    def update_inventory(self,trade_list, actual_inventory, trade_date=None):
        LOGGER.info("updating inventory based on the new trades and existing inventory assuming no slippage")

        final_inventory = trade_list.merge(actual_inventory, how='outer', on='ticker').fillna(0)
        final_inventory['trade_side'] = final_inventory.side_x.apply(
            lambda x: side_map[x] if type(x) == str else x)
        final_inventory['position_side'] = final_inventory.side_y.apply(
            lambda x: side_map[x] if type(x) == str else x)

        final_inventory['quantity'] = ((final_inventory.trade_side * final_inventory.quantity_x)
                                       + (final_inventory.position_side * final_inventory.quantity_y))

        quantity_breach = final_inventory[final_inventory['quantity'] > 1]
        if len(quantity_breach) > 0:
            LOGGER.error("Alert quantity breach!! ")

        final_inventory['avg_price'] = ((
                                                    final_inventory.trade_side * final_inventory.quantity_x * final_inventory.price)
                                        + (
                                                    final_inventory.position_side * final_inventory.quantity_y * final_inventory.avg_price)) / final_inventory.quantity

        final_inventory = final_inventory[['ticker', 'quantity', 'avg_price']]
        final_inventory['side'] = np.where(final_inventory.quantity > 0, 1, -1)
        final_inventory['side'] = final_inventory['side'].apply(lambda x: rev_side_map[x])
        final_inventory = final_inventory[final_inventory.quantity != 0]
        final_inventory.to_csv('/Users/pankajti/dev/git/wqu/capstone/data/inventory.csv', index=False)
        final_inventory['tdate'] = trade_date
        final_inventory['strategy'] = 'price_breakout'
        final_inventory['creatime'] = dt.datetime.now()

        # final_inventory.to_sql(con=dbEngine, name='inventories', index=False, if_exists='append')

        return final_inventory

    def close_positions(self,current_open_positions, candle_data, actual_inventory):
        LOGGER.info(f"Creating trades for open positions {len(current_open_positions)}")
        new_positions = current_open_positions.copy()
        market_data = candle_data[candle_data.ticker.isin(current_open_positions.ticker)].sort_index().drop_duplicates(
            'ticker', keep='last')
        positions_to_close = market_data.reset_index()[['Close', 'timestamp', 'ticker']].merge(current_open_positions)
        positions_to_close = positions_to_close.rename({'Close': 'price', 'timestamp': 'trade_time'}, axis=1)

        positions_to_close['side'] = np.where(positions_to_close.side == 'buy', 'sell', 'buy')
        trade_list = self.calculate_trades(model_inventory=positions_to_close, actual_inventory=actual_inventory,
                                      candle_data=candle_data)
        self.update_inventory(trade_list, current_open_positions, trade_date=None)

    def close_intraday_positions(self,trade_date, candle_data):
        LOGGER.info("closing intraday positions ")
        current_open_positions = self.get_current_inventory(trade_date)
        if len(current_open_positions) == 0:
            LOGGER.warning("No positions to close  ")
            return
        self.close_positions(current_open_positions, candle_data, actual_inventory=None)


    def intraday_trading_job(self,current_time):
        # current_time = dt.datetime.now(tz=pytz.timezone('Asia/Singapore'))
        trade_date = current_time.strftime('%Y-%m-%d')
        current_time_str = current_time.strftime('%H:%M:%S')

        LOGGER.info("started intraday trading ")
        universe = self.load_universe(num_recs=10000)
        fromtime = current_time - dt.timedelta(minutes=10)
        # candle_data = read_market_data_from_file(universe, fromtime.strftime('%Y%m%d%H%M'), current_time.strftime('%Y%m%d%H%M'), )
        candle_data = self.read_market_data_from_db(universe, fromtime.strftime('%Y%m%d%H%M'),
                                               current_time.strftime('%Y%m%d%H%M'), tdate=trade_date)

        LOGGER.info(f"total candle data read {candle_data.shape}")
        if current_time_str > market_close_time:
            self.close_intraday_positions(trade_date, candle_data)
            return

        signals = signal_generator.get_signals(candle_data)
        if len(signals) == 0:
            LOGGER.info(f"no signals found for {current_time} waiting for next iterations")
            return
        print(f"total signals {len(signals)}")
        positions = self.create_positions(signals, candle_data)
        actual_inventory = self.get_current_inventory(trade_date)
        model_inventory = self.calculate_model_inventory(actual_inventory, positions)
        trade_list = self.calculate_trades(model_inventory, candle_data, actual_inventory)
        self.update_inventory(trade_list, actual_inventory, trade_date)
        LOGGER.info(f" Trades for {current_time} is completed ")

    def clear_setup(self):
        inventory = pd.DataFrame(columns=['ticker', 'quantity', 'avg_price', 'side'])
        trades = pd.DataFrame(columns=['trade_time', 'ticker', 'side', 'quantity', 'price'])
        trades.to_csv(r'/Users/pankajti/dev/git/wqu/capstone/data/trades.csv', index=False)
        inventory.to_csv('/Users/pankajti/dev/git/wqu/capstone/data/inventory.csv', index=False)

        LOGGER.info("files cleared")

    def backtest(self,run_date):
        year = run_date.year
        month = run_date.month
        day = run_date.day
        tzinfo = pytz.timezone('Asia/Kolkata')
        start_time = dt.datetime(year, month, day, 9, 50, 0)
        curr_time = start_time
        while curr_time <= dt.datetime(year, month, day, 15, 30, 0):
            print(f"running for {curr_time}")
            curr_time = curr_time + dt.timedelta(minutes=5)
            self.intraday_trading_job(curr_time)



def main():
    global version

    stop_loss_limit = .05
    take_profit_cap = .2
    open_interval = 35

    stop_loss_limits = np.linspace(0, .1, 5)
    take_profit_caps = np.linspace(.1, .3, 5)
    open_intervals = range(10, 70, 10)

    run_groups = [{'stop_loss_limit':stop_loss_limit, 'take_profit_cap':take_profit_cap, 'open_interval':open_interval}
                  for stop_loss_limit in stop_loss_limits for
                  take_profit_cap in take_profit_caps
                  for open_interval in open_intervals]

    print(run_groups)

    for run_group in run_groups:
        version = int(time.time())
        ts = OrbTradingSystem(stop_loss_limit,take_profit_cap,open_interval)
        ts = OrbTradingSystem(**run_group)
        #run_scheduler()
        #intraday_trading_job()
        ts.clear_setup()

        df = pd.DataFrame(data=[[version, str(run_group)]], columns=['version_no', 'run_details'])
        df.to_sql(con=dbEngine, name='version_info', index=False, if_exists='append')

        for d in loaded_dates[0:] :
            run_date = dt.datetime.strptime(d,'%Y-%m-%d')
            #run_date = dt.date(2024,3,26)
            ts.backtest(run_date)


def run_scheduler():
    stop_loss_limit = .05
    take_profit_cap = .2
    open_interval = 35
    ts = OrbTradingSystem(stop_loss_limit,take_profit_cap,open_interval)
    schedule.every(trade_interval).seconds.do(ts.intraday_trading_job)
    while True:
        schedule.run_pending()
        time.sleep(trade_interval)

if __name__ == '__main__':
    main()
