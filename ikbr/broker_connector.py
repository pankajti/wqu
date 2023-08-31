from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class BrokerConnector(EClient, EWrapper):

    def __init__(self):
        EClient.__init__(self,self)
        self.all_positions =[]
        self.open_orders =[]

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def position(self, account, contract, pos, avgCost):
        print("getting positions")
        index = str(account) + str(contract.symbol)
        self.all_positions.append( account, contract.symbol, pos, avgCost, contract.secType)

    def openOrder(self, orderId, contract, order, orderState):
        # Process and store the open order information
        #self.open_orders=[]
        self.open_orders.append({
            "OrderId": orderId,
            "Symbol": contract.symbol,
            "Quantity": order.totalQuantity,
            "Price": order.lmtPrice,
            "Status": orderState.status
        })

