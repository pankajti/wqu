import time

from ikbr.broker_connector import EClient,EWrapper


class MarketDataDemo(EClient, EWrapper):

    def __init__(self):
        EClient.__init__(self,self)


    def historicalData(self, reqId: int, bar):
        print(reqId,bar)
from ibapi.contract import Contract

def create_stocks_contract(symbol, exchange = 'SMART', currency= 'USD'):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'STK'
    contract.exchange = exchange
    contract.currency=currency
    return contract

import datetime as dt
queryTime = (dt.datetime.today() - dt.timedelta(days=180)).strftime("%Y%m%d-%H:%M:%S")

app = MarketDataDemo()
app.connect('127.0.0.1', 7497, 123)
time.sleep(5)
contract = create_stocks_contract('AA', exchange ='SMART')
app.reqHistoricalData(1,contract, queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])
time.sleep(5)
app.run()
