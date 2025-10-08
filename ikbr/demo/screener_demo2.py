import time

from ibapi.wrapper import *
from ibapi.client import *
from ibapi.tag_value import *


class DemoScanner2(EClient,EWrapper):

    def __init__(self):
        EClient.__init__(self,self)


    def nextValidId(self, orderId:int):
        scanSub = ScannerSubscription()
        scanSub.instrument = "STK"

        scanSub.locationCode = "STK.US.MAJOR"

        scanSub.scanCode = "HOT_BY_VOLUME"

        scan_options = []
        filter_options = [
            TagValue("volumeAbove", "10000"),
            TagValue("priceAbove","1"),
            TagValue("marketCapBelow1e6","1000")
        ]
        self.reqScannerSubscription(orderId, scanSub,scan_options,filter_options)

    def scannerData(self, reqId:int, rank:int, contractDetails:ContractDetails,
                     distance:str, benchmark:str, projection:str, legsStr:str):

        print(contractDetails)

    def scannerDataEnd(self, reqId:int):
        print(f"subscription end {reqId}")
        self.cancelScannerSubscription(reqId)
        self.disconnect()







def main():
    app = DemoScanner2()
    app.connect(host='127.0.0.1', port=7497, clientId=1003)
    app.run()
    time.sleep(3)
    app.disconnect()

if __name__ == '__main__':
    main()