from ibapi.contract import Contract
from ibapi.order import *
import threading
import time
from ikbr.broker_connector import BrokerConnector

def create_fx_contract(symbol):
	contract = Contract()
	contract.symbol = symbol[:3]
	contract.secType = 'CASH'
	contract.exchange = 'IDEALPRO'
	contract.currency = symbol[3:]
	return contract


def create_order(action , total_quantity, order_type, limit_price, e_trade_only , firm_quote_only):
    order = Order()
    order.action = action
    order.totalQuantity = total_quantity
    order.orderType = order_type
    order.lmtPrice =  limit_price
    order.eTradeOnly = e_trade_only
    order.firmQuoteOnly = firm_quote_only
    return order

def create_stocks_contract(symbol, exchange = 'SMART', currency= 'USD'):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'STK'
    contract.exchange = exchange
    contract.currency=currency
    return contract

def run_loop(app):
    app.run()

def main():
    app = BrokerConnector()
    app.connect('127.0.0.1', 7497, 123)
    app.nextorderId = None

    x = threading.Thread(target=run_loop, args=(app,))
    x.start()
    time.sleep(5)

    app.reqPositions()  # associated callback: position
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(3)
    current_positions = app.all_positions
    print(current_positions)

    # Place order
    contract = create_stocks_contract('AA')

    action='Buy'
    total_quantity=20
    order_type='LMT'
    limit_price='1.10'
    e_trade_only=False
    firm_quote_only =  False
    order = create_order(action , total_quantity, order_type, limit_price, e_trade_only , firm_quote_only)
    app.placeOrder(app.nextorderId, contract, order)


if __name__ == '__main__':
    main()
