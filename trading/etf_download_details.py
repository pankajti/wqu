import time
import numpy as np
import torch
import requests
import pandas as pd
import yfinance as yf
from multiprocessing import Pool
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
data_files_path = r'/Users/shritiwari/dev/git/finance/data'

etf_url = "https://api.nasdaq.com/api/screener/etf?tableonly=true&limit=25&offset=0&download=true"
headers = {"Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate, br",
           "User-Agent": "Java-http-client/"}
def main():
    etf_tickers = prepare_batch()
    #download_data( (etf_tickers,0, 3))
    pool = Pool(7)
    step=10
    l=len(etf_tickers)
    logger.info(f" total file to download {l}")
    if l< step:
        download_data((etf_tickers, 0, 7))
    arg= [ (etf_tickers,p[0],p[1]) for p in zip(range(0, l, step), range(step, l, step))]
    pool.map(download_data, arg)


def prepare_batch():
    etf_response = requests.get(etf_url, headers=headers)
    et_json = etf_response.json()
    et_df = pd.DataFrame(et_json['data']['data']['rows'])
    # etf_tickers = yf.Tickers(list(et_df.symbol))
    files = os.listdir(data_files_path)
    df = pd.concat([pd.read_csv(os.path.join(data_files_path, p)) for p in files if p.endswith(".csv")])
    etf_tickers = list(set(et_df.symbol) - set(df.symbol))
    logger.info(f"total symbols {len(set(et_df))} already downloaded {len(df)} remaining {len(etf_tickers)}")

    return etf_tickers


import requests
from bs4 import  BeautifulSoup
def download_data(args):
    etf_tickers , start, end =args
    etf_details = []
    logger.info(f"start :{ start}")
    success = False
    for k in  etf_tickers[start:end]:
        attempt_count =0
        # while not success and attempt_count<5:
        #     success = attempt_download(etf_details, k)
        #     status_str= f"success after {attempt_count} attempts for {k} {len(etf_details)}" if   success else f" failure for {k} after 10 attempts "
        #     logger.debug(status_str )
        try:  # <span class="Fl(end)">4.94%</span>
            url = r'https://finance.yahoo.com/quote/{}/profile?p={}'.format(k, k)
            print(url)
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text)
            keys = [i.text for i in soup.find(class_='Mb(25px)').find_all(class_='Fl(start)')]
            vals = [i.text for i in soup.find(class_='Mb(25px)').find_all(class_='Fl(end)')]
            res_dict = dict(zip(keys, vals))
            res_dict['symbol'] = k
            etf_details.append(res_dict)
            print("read for ", k, len(etf_details))
        except Exception as e:
            print("error for ", k, len(etf_details), str(e))
            time.sleep(60)
            print("restarting again after sleep")

    if len(etf_details)>0:
        df = pd.DataFrame(etf_details)
        df.to_csv(f"./data/{k}.csv")
    else:
        logger.info(f"no records for {k}" )
    logger.info("done for {},{}".format(start, k))


def attempt_download(etf_details, k):
    try:  # <span class="Fl(end)">4.94%</span>
        url = r'https://finance.yahoo.com/quote/{}/profile?p={}'.format(k, k)
        print(url)
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text)
        keys = [i.text for i in soup.find(class_='Mb(25px)').find_all(class_='Fl(start)')]
        vals = [i.text for i in soup.find(class_='Mb(25px)').find_all(class_='Fl(end)')]
        res_dict = dict(zip(keys, vals))
        res_dict['symbol'] = k
        etf_details.append(res_dict)
        print("read for ", k, len(etf_details))
    except Exception as e:
        print("error for ", k, len(etf_details), str(e))
        time.sleep(60)
        print("restarting again after sleep")
        return False

    logging.info(f" successfully downloaded for {k}")

    return True


if __name__ == '__main__':
    main()