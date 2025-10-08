from ibapi.client import *
from ibapi.wrapper import *
import xml
import xmltodict

port = 7497
host ='127.0.0.1'
class DemoScanner(EClient,EWrapper):

    def __init__(self):
        EClient.__init__(self,self)

    def nextValidId(self, orderId:int):
        self.reqScannerParameters()

    def scannerParameters(self, xml:str):
        print("started")
        d = xmltodict.parse(xml)
        print("done")




def main():
    app = DemoScanner()
    app.connect(host=host,port=port, clientId=1001)
    app.run()

if __name__ == '__main__':
    main()