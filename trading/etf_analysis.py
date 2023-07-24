import numpy as np
import torch
import requests
import pandas as pd
import yfinance as yf
from multiprocessing import Pool
import logging


def main():
    etf_url = "https://api.nasdaq.com/api/screener/etf?tableonly=true&limit=25&offset=0&download=true"
    headers = {"Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate, br",
               "User-Agent": "Java-http-client/"}
    etf_response = requests.get(etf_url, headers=headers)
    et_json = etf_response.json()
    et_df = pd.DataFrame(et_json['data']['data']['rows'])
    etf_tickers = yf.Tickers(list(et_df.symbol))
    download_data( (etf_tickers,0, 3))
    # pool = Pool(7)
    # step=10
    # l=len(et_df.symbol)
    # arg= [ (etf_tickers,p[0],p[1]) for p in zip(range(0, l, step), range(step, l, step))]
    # pool.map(download_data, arg)
url = r'https://finance.yahoo.com/quote/LOUP/holdings?p=LOUP'

def download_data(args):
    etf_tickers , start, end =args
    etf_details = []
    print("start :", start)
    for k, v in list(etf_tickers.tickers.items())[start:end]:
        try:
            aa = v.get_institutional_holders()
            etf_details.append(aa.set_index(0).T.assign(symbol=k))
            print("read for ", k, len(etf_details))
        except Exception as e:
            print("error for ", k, len(etf_details), str(e))
    if len(etf_details)>0:
        df = pd.concat(etf_details)
        #name= etf_tickers[0]+"_"+etf_tickers[-1]
        df.to_csv(f"./data/{k}.csv")
    else:
        print("no records for " )
    print("done for ",start, k)


if __name__ == '__main__':

    main()