import requests
import pandas as pd
import logging
import datetime as dt
import os
from ikbr.paper_trading_app.utils.utils import convert_float
logging.basicConfig(  encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UniverseSelector():
    def __init__(self,root_dir=None):
        self.root_dir = r'/Users/shritiwari/PycharmProjects/finance/ikbr/paper_trading_app/data' if root_dir is None else root_dir
        self.url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true"
        self.headers = {"Accept-Language": "en-US,en;q=0.9",
                   "Accept-Encoding": "gzip, deflate, br",
                   "User-Agent": "Java-http-client/"}

    def get_universe_file_path(self, date_no_comma):
        file_name = f'univ_{date_no_comma}.csv'
        file_path = os.path.join(self.root_dir, 'universe', file_name)
        return file_path

    def check_universe_file_for_date(self, file_path):
        file_present = os.path.exists(file_path)
        return file_present

    def get_universe_based_on_volume(self, count=50, date = None ):
        nasqaq_symbol = self.read_universe(date)
        nasqaq_symbol_top_symbols = nasqaq_symbol.sort_values('volume')[:count]
        return nasqaq_symbol_top_symbols

    def get_universe_based_on_market_cap(self, count=50, date = None ):
        nasqaq_symbol = self.read_universe(date)
        nasqaq_symbol_top_symbols = nasqaq_symbol.sort_values('marketCap', ascending=False)[:count]
        return nasqaq_symbol_top_symbols

    def read_universe(self, date=None):
        if date is None:
            date = dt.datetime.now().strftime('%Y-%m-%d')
        date_no_comma = date.replace("-", "")
        univ_file_path = self.get_universe_file_path(date_no_comma)
        logger.info("starting to select universe")
        if self.check_universe_file_for_date(univ_file_path):
            logger.info(f"file present , reading data from : {univ_file_path}")
            nasqaq_symbol = pd.read_csv(univ_file_path)
        else:
            logger.info(f"file not present , reading data from url : {self.url}")
            response = requests.get(self.url, headers=self.headers)
            json = response.json()
            nasqaq_symbol = pd.DataFrame(json['data']['rows'])
        nasqaq_symbol['volume'] = nasqaq_symbol['volume'].astype(int)
        nasqaq_symbol['marketCap'] = nasqaq_symbol['marketCap'].apply(lambda x: convert_float(x))
        nasqaq_symbol.to_csv(univ_file_path, index=False)
        return nasqaq_symbol