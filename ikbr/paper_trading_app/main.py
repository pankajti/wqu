from ikbr.paper_trading_app.utils.utils import convert_float
from universe.universe_selector import UniverseSelector
from data_reader.market_data_reader import MarketDataReader
import datetime as dt
DATE_FMT = '%Y-%m-%d'
def main():
    universe_selector = UniverseSelector()
    market_data_reader = MarketDataReader()
    trade_date = dt.datetime.now()
    trade_data_start_date = trade_date- dt.timedelta(2000)
    trade_date_comma= trade_date.strftime(DATE_FMT)
    trade_data_start_date_comma= trade_data_start_date.strftime(DATE_FMT)

    universe = universe_selector.get_universe_based_on_market_cap(25)
    universe_tickers = universe.symbol.to_list()
    market_data = market_data_reader.read_market_data(universe_tickers,trade_data_start_date_comma,trade_date_comma)

if __name__ == '__main__':
    main()