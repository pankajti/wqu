import logging
import pandas as pd


logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("Log initiated ")

def get_signals(market_data):
    try:

        thresold=38
        num_of_candles_to_check=10
        logger.info("started loading signals ")
        ticker_groups = market_data.groupby('ticker')
        all_transactions=[]
        for ticker , candle_data in ticker_groups:
            close_hist = pd.concat([candle_data.Close.shift(i).rename(f'Close_{i}') for i in range(0, num_of_candles_to_check+1)], axis=1)
            close_hist_inc = pd.concat(
                [(close_hist.iloc[:, i] < close_hist.iloc[:, i - 1]).rename(f'Close_{i}_cmp') for i in
                 range(1, num_of_candles_to_check+1)], axis=1)
            close_hist_dec = pd.concat(
                [(close_hist.iloc[:, i] > close_hist.iloc[:, i - 1]).rename(f'Close_{i}_cmp') for i in
                 range(1, num_of_candles_to_check+1)], axis=1)
            close_hist['change'] = ((close_hist['Close_0'] - close_hist[f'Close_{num_of_candles_to_check}']))
            close_hist['change_perc'] = 100 * (close_hist['change'] / close_hist[f'Close_{num_of_candles_to_check}'])
            buy_breakout = close_hist[(close_hist_inc.sum(axis=1) == num_of_candles_to_check) & (close_hist['change_perc']>thresold)].assign(transactio_type='buy')
            sell_breakout = close_hist[(close_hist_dec.sum(axis=1) == num_of_candles_to_check)& (close_hist['change_perc']>thresold)].assign(transactio_type='sell')
            transaction = pd.concat([buy_breakout,sell_breakout])
            transaction['ticker'] = ticker
            all_transactions.append(transaction.drop_duplicates(['ticker'], keep='last'))

        signals = pd.concat(all_transactions)
        ret_signals = signals[['ticker', 'transactio_type', 'Close_0']].reset_index()
        ret_signals.columns = ['trade_time', 'ticker', 'side', 'price']
    except Exception as e:
        logger.info("error ")

    return ret_signals

def main():
    md=[]
    get_signals(market_data=md)

if __name__ == '__main__':
    main()