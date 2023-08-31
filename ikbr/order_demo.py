import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

import threading
import time

class OrderDemo(EClient, EWrapper):

    def __init__(self):
        EClient.__init__(self,self)
        self.all_positions =[]

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def position(self, account, contract, pos, avgCost):
        print("getting positions")
        index = str(account) + str(contract.symbol)
        self.all_positions.append( account, contract.symbol, pos, avgCost, contract.secType)


def FX_contract(symbol):
	contract = Contract()
	contract.symbol = symbol[:3]
	contract.secType = 'CASH'
	contract.exchange = 'IDEALPRO'
	contract.currency = symbol[3:]
	return contract


def run_loop(app):
    app.run()

def main():
    app = OrderDemo()
    app.connect('127.0.0.1', 7497, 123)
    app.nextorderId = None

    x = threading.Thread(target=run_loop, args=(app,))
    x.start()
    time.sleep(5)

    # Start the socket in a thread

    app.reqPositions()  # associated callback: position
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(3)
    current_positions = app.all_positions

    print(current_positions)

    # Create order object
    order = Order()
    order.action = 'BUY'
    order.totalQuantity = 1000
    order.orderType = 'LMT'
    order.lmtPrice = '1.10'
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    time.sleep(3)

    # Place order
    contract = FX_contract('EURUSD')
    app.placeOrder(app.nextorderId, contract, order)




if __name__ == '__main__':
    main()

