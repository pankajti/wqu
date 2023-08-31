import time
import requests
import pandas as pd
import logging
import yfinance as yf
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(  encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_float(s):
    try:
        f=float(s)
    except:
        f=0
    return f



def get_universe():
    logger.info("starting to select universe")
    url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true"
    headers = {"Accept-Language": "en-US,en;q=0.9",
               "Accept-Encoding": "gzip, deflate, br",
               "User-Agent": "Java-http-client/"}
    response = requests.get(url, headers=headers)
    json = response.json()
    nasqaq_symbol = pd.DataFrame(json['data']['rows'])
    nasqaq_symbol['volume'] = nasqaq_symbol['volume'].astype(int)
    nasqaq_symbol['market_cap'] = nasqaq_symbol['marketCap'].apply(lambda x:convert_float(x))

    return nasqaq_symbol

def get_market_data(universe):
    logger.info("loading marke data")
    data = yf.Tickers(universe.symbol[:20].tolist()).history(period='1mo', interval='1d')
    return data


def place_order():
    logger.info("placing orders")
def main():
    universe = get_universe()
    get_market_data(universe)
    logger.info(" generating signals  ")
    logger.info("finding tradable instruments ")
    logger.info("allocating positions")
    logger.info(" loading existing positions ")
    logger.info("generating trade list ")
    logger.info(" executing trades")
    logger.info(" get order details ")

    while True :
        logger.info("monitoring positions ")
        time.sleep(5)

if __name__ == '__main__':
    main()