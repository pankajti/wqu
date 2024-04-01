import pandas as pd

def breakout_signal(candle_data, thresold ):
    close_hist = pd.concat([candle_data.Close.shift(i).rename(f'Close_{i}') for i in range(0, 6)], axis=1)
    close_hist_inc = pd.concat(
        [(close_hist.iloc[:, i] < close_hist.iloc[:, i - 1]).rename(f'Close_{i}_cmp') for i in range(1, 6)], axis=1)
    close_hist_dec = pd.concat(
        [(close_hist.iloc[:, i] > close_hist.iloc[:, i - 1]).rename(f'Close_{i}_cmp') for i in range(1, 6)], axis=1)
    close_hist['change'] = ((close_hist['Close_0'] - close_hist['Close_5']))
    close_hist['change_perc'] = 100 * (close_hist['change'] / close_hist['Close_5'])
    buy_breakout = close_hist[(close_hist_inc.sum(axis=1) == 5) & (close_hist['change_perc']>thresold)].assign(transactio_type='buy')
    sell_breakout = close_hist[(close_hist_dec.sum(axis=1) == 5)& (close_hist['change_perc']>thresold)].assign(transactio_type='sell')

    return pd.concat([buy_breakout,sell_breakout])


def main():
    minute_data_path = r'../data/minute_data.csv'
    ticker = 'RELIANCE.NS'
    all_transactions = []
    date = '2024-03-28'

    minute_data = pd.read_csv(minute_data_path, index_col=0)
    minute_data['date'] = list(map(lambda x: x.strftime('%Y-%m-%d'), pd.to_datetime(minute_data.index)))
    tickers = minute_data.ticker.unique()
    for ticker in tickers:
        rel_data = minute_data[minute_data.ticker == ticker]
        candle_data =rel_data[rel_data.date==date]
        transaction = breakout_signal(candle_data,5)
        transaction['ticker'] = ticker
        all_transactions.append(transaction)
        print(f'running for {ticker} {len(transaction)}')

    print(pd.concat(all_transactions))


if __name__ == '__main__':
    main()