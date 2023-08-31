from ibapi.client import *
from ibapi.wrapper import *
import pandas_datareader

pandas_datareader.nasdaq_trader.get_nasdaq_symbols()


import time

class TestApp(EClient, EWrapper):

    def __init__(self):
        EClient.__init__(self,self)

    def contractDetails(self, reqId:int, contractDetails:ContractDetails):
        print(f"contact details {contractDetails}")

    def contractDetailsEnd(self, reqId:int):
        print("end")
        self.disconnect()


def main():
    contract = Contract()
    contract.symbol="AAPL"
    contract.secType="STK"
    app = TestApp()
    app.connect("127.0.0.1", 7497, 1000)
    time.sleep(3)

    app.reqContractDetails(1,contract)
    app.run()
    print("End")

if __name__ == '__main__':
    main()
