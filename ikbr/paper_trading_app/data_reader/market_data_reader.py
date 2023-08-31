import yfinance as yf

class MarketDataReader():
    def __init__(self):
        pass

    def read_market_data(self,instruments, start_date ,end_date, ):
        market_data_df = yf.Tickers(instruments).history()
        self.market_data= market_data_df
        return market_data_df

    def get_data_for(self,date, field):
        data = self.market_data[field].loc[date]
        return data