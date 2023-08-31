import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

import threading
import time

class NewsDemo(EClient, EWrapper):

    def __init__(self):
        EClient.__init__(self,self)
        self.all_positions =[]


    def historicalNews(self, requestId:int, time:str, providerCode:str, articleId:str, headline:str):
        print(requestId, providerCode, articleId,)
        print(headline)

    def newsArticle(self, requestId:int, articleType:int, articleText:str):
        print(articleText)


app = NewsDemo()
app.connect('127.0.0.1', 7497, 123)
#app.nextorderId = None
time.sleep(5)
app.reqHistoricalNews(10003, 8314, "BRFG", "", "", 10, [])
app.reqNewsArticle(10002, "BRFG", "BRFG$12d0a5d4", [])
app.run()