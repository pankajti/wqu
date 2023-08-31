from ibapi.contract import Contract
from ibapi.order import *
import threading
import time
from ikbr.broker_connector import BrokerConnector


def run_loop(app):
    app.run()

def main():
    app = BrokerConnector()
    app.connect('127.0.0.1', 7497, 123)
    app.nextorderId = None

    x = threading.Thread(target=run_loop, args=(app,))
    x.start()
    time.sleep(5)
    orders = app.reqAllOpenOrders()
    time.sleep(5)
    print("open orders " , orders)

    for order in app.open_orders:
        print(order)
    for   i in range(20):
        app.cancelOrder(i)

    # Place order


if __name__ == '__main__':
    main()
