import schedule
import time
import datetime as dt
import logging
import pandas as pd
import numpy as np
import pytz

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("Log initiated ")


side_map = {'buy':1, 'sell':-1, 'hold':0}
rev_side_map = {v:k for k, v in side_map.items()}

trade_interval = 60
market_close_time = '15:00:00'
def read_market_data(univers,fromtime, to_time):
    logger.info("started reading market data")
    minute_data_path = r'../data/minute_data.csv'
    minute_data = pd.read_csv(minute_data_path, index_col=0)
    minute_data = minute_data[minute_data.ticker.isin(univers)]
    minute_data['ts'] = list(pd.to_datetime(minute_data.reset_index()['index']).apply(lambda x: x.strftime('%Y%m%d%H%M')))
    ret_min_data = minute_data[(minute_data.ts<to_time)&(minute_data.ts>=fromtime)]
    ret_min_data['date'] = list(map(lambda x: x.strftime('%Y-%m-%d'), pd.to_datetime(ret_min_data.index)))
    return ret_min_data

def load_universe( num_recs=10000):
    logger.info("started loading universe ")
    tickers_path = '/Users/pankajti/dev/git/wqu/capstone/module4/MCAP31122023_0.xlsx'
    tickers_data = pd.read_excel(tickers_path, nrows=2189)
    yahoo_symbs = tickers_data.Symbol + '.NS'
    yahoo_symbs = yahoo_symbs.dropna().tolist()[:num_recs]
    return yahoo_symbs


def get_signals(market_data):
    thresold=5
    logger.info("started loading signals ")

    ticker_groups = market_data.groupby('ticker')
    all_transactions=[]
    for ticker , candle_data in ticker_groups:
        close_hist = pd.concat([candle_data.Close.shift(i).rename(f'Close_{i}') for i in range(0, 6)], axis=1)
        close_hist_inc = pd.concat(
            [(close_hist.iloc[:, i] < close_hist.iloc[:, i - 1]).rename(f'Close_{i}_cmp') for i in range(1, 6)], axis=1)
        close_hist_dec = pd.concat(
            [(close_hist.iloc[:, i] > close_hist.iloc[:, i - 1]).rename(f'Close_{i}_cmp') for i in range(1, 6)], axis=1)
        close_hist['change'] = ((close_hist['Close_0'] - close_hist['Close_5']))
        close_hist['change_perc'] = 100 * (close_hist['change'] / close_hist['Close_5'])
        buy_breakout = close_hist[(close_hist_inc.sum(axis=1) == 5) & (close_hist['change_perc']>thresold)].assign(transactio_type='buy')
        sell_breakout = close_hist[(close_hist_dec.sum(axis=1) == 5)& (close_hist['change_perc']>thresold)].assign(transactio_type='sell')
        transaction = pd.concat([buy_breakout,sell_breakout])
        transaction['ticker'] = ticker
        all_transactions.append(transaction.drop_duplicates(['ticker'], keep='last'))

    return pd.concat(all_transactions)

def get_positions(signals , candle_data):
    logger.info("started loading universe ")
    positions = signals[['ticker', 'transactio_type', 'Close_0']].reset_index()
    positions.columns =['trade_time','ticker', 'side', 'price']
    positions['quantity']=1
    return positions

def get_current_inventory(trade_date):
    logger.info("started loading existing inventory")

    inventory_path = r'/Users/pankajti/dev/git/wqu/capstone/data/inventory.csv'
    inventory = pd.read_csv(inventory_path)
    return inventory

def calculate_model_inventory(actual_inventory,positions):
    logger.info("calculate model inventory from currency amount positions ")
    model_inventory = positions.merge(actual_inventory,how='left',on='ticker').fillna(0)
    model_inventory['quantity'] = ((model_inventory.side_x.apply(lambda x:side_map[x] if type(x)==str else x) * model_inventory.quantity_x)
                             -(model_inventory.side_y.apply(lambda x:side_map[x] if type(x)==str else x) * model_inventory.quantity_y))
    model_inventory['side']=model_inventory['side_x']
    return model_inventory

## Not implemented in the proposal phase
def apply_stop_loss(trades,model_inventory,candle_data):
    logger.info("Applying stop loss on the  losing trades")
    return trades

## Not implemented in the proposal phase
def apply_take_profit(trades,model_inventory,candle_data):
    logger.info("Applying take profit on the  profitable trades")
    return trades


def calculate_trades(model_inventory, candle_data):
    logger.info("calculating trade list based on the model and actual inventory")
    trades = model_inventory[['trade_time','ticker','side','price','quantity']]
    trades = apply_stop_loss(trades,model_inventory,candle_data)
    trades = apply_take_profit(trades,model_inventory,candle_data)
    trades=trades[trades.quantity!=0]
    existing_trades = pd.read_csv(r'/Users/pankajti/dev/git/wqu/capstone/data/trades.csv')
    all_trades= pd.concat([existing_trades,trades])
    all_trades.to_csv(r'/Users/pankajti/dev/git/wqu/capstone/data/trades.csv',index=False)
    return trades

def update_inventory(trade_list, actual_inventory):
    logger.info("updating inventory based on the new trades and existing inventory assuming no slippage")

    final_inventory = trade_list.merge(actual_inventory, how='outer', on='ticker').fillna(0)
    final_inventory['trade_side'] = final_inventory.side_x.apply(
        lambda x: side_map[x] if type(x) == str else x)
    final_inventory['position_side']  = final_inventory.side_y.apply(
        lambda x: side_map[x] if type(x) == str else x)

    final_inventory['quantity'] = (( final_inventory.trade_side* final_inventory.quantity_x)
                                   + (final_inventory.position_side* final_inventory.quantity_y))

    final_inventory['avg_price'] = (( final_inventory.trade_side* final_inventory.quantity_x*final_inventory.price)
                                   + (final_inventory.position_side* final_inventory.quantity_y*final_inventory.avg_price))/final_inventory.quantity

    final_inventory = final_inventory[['ticker','quantity','avg_price']]
    final_inventory['side'] = np.where(final_inventory.quantity>0,1,-1)
    final_inventory['side']=final_inventory['side'].apply(lambda x:rev_side_map[x])
    final_inventory=final_inventory[final_inventory.quantity!=0]
    final_inventory.to_csv('/Users/pankajti/dev/git/wqu/capstone/data/inventory.csv', index=False)

    return final_inventory

def close_positions(current_open_positions,candle_data ):
    logger.info(f"Creating trades for open positions {len(current_open_positions)}")
    new_positions = current_open_positions.copy()
    market_data = candle_data[candle_data.ticker.isin(current_open_positions.ticker)].sort_index().drop_duplicates(
        'ticker', keep='last')
    positions_to_close = market_data.reset_index()[['Close', 'index', 'ticker']].merge(current_open_positions)
    positions_to_close= positions_to_close.rename({'Close': 'price', 'index': 'trade_time'}, axis=1)

    positions_to_close['side'] = np.where(positions_to_close.side=='buy','sell','buy')
    trade_list = calculate_trades(model_inventory=positions_to_close, candle_data=candle_data)
    update_inventory(trade_list, current_open_positions)


def close_intraday_positions(trade_date,candle_data):
    logger.info("closing intraday positions ")
    current_open_positions = get_current_inventory(trade_date)
    if len(current_open_positions)==0:
        logger.warning("No positions to close  ")
        return
    close_positions(current_open_positions,candle_data)



def intraday_trading_job(current_time):
    #current_time = dt.datetime.now(tz=pytz.timezone('Asia/Singapore'))
    trade_date = current_time.strftime('%Y-%m-%d')
    current_time_str = current_time.strftime('%H:%M:%S')

    logger.info("started intraday trading ")
    universe = load_universe(num_recs=10000)
    fromtime = current_time - dt.timedelta(minutes=10)
    candle_data = read_market_data(universe,fromtime.strftime('%Y%m%d%H%M'),current_time.strftime('%Y%m%d%H%M'),)
    logger.info(f"total candle data read {candle_data.shape}")
    if current_time_str> market_close_time:
        close_intraday_positions(trade_date,candle_data)
        return

    signals = get_signals(candle_data)
    print(f"total signals {signals}")
    positions = get_positions(signals,candle_data)
    actual_inventory = get_current_inventory(trade_date)
    model_inventory = calculate_model_inventory(actual_inventory,positions)
    trade_list = calculate_trades(model_inventory, candle_data)
    update_inventory(trade_list, actual_inventory)
    logger.info(f" Trades for {current_time} is completed ")


def clear_setup():
    inventory = pd.DataFrame(columns=['ticker', 'quantity', 'avg_price', 'side'])
    trades = pd.DataFrame(columns=['trade_time','ticker','side','quantity','price'])
    trades.to_csv(r'/Users/pankajti/dev/git/wqu/capstone/data/trades.csv',index=False)
    inventory.to_csv('/Users/pankajti/dev/git/wqu/capstone/data/inventory.csv', index=False)

    logger.info("files cleared")




def backtest(run_date):
    clear_setup()
    year = run_date.year
    month = run_date.month
    day = run_date.day
    tzinfo=pytz.timezone('Asia/Kolkata')
    start_time = dt.datetime(year,month,day,9,15,0  )
    curr_time = start_time
    while curr_time<=dt.datetime(year,month,day,15,30,0):
        print(f"running for {curr_time}")
        curr_time=curr_time+dt.timedelta(minutes=5)
        intraday_trading_job(curr_time)


def main():
    #run_scheduler()
    #intraday_trading_job()
    run_date = dt.date(2024,3,28)
    backtest(run_date)


def run_scheduler():
    schedule.every(trade_interval).seconds.do(intraday_trading_job)
    while True:
        schedule.run_pending()
        time.sleep(trade_interval)

if __name__ == '__main__':
    main()
