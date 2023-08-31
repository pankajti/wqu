import unittest
from ikbr.paper_trading_app.data_reader.market_data_reader import MarketDataReader

class UniverseSelectorTestCase(unittest.TestCase):
    mdr = MarketDataReader()
    def test_read_market_data_test(self):
        md = self.mdr.read_market_data(['AAPL','GOOG'],'2023-01-01','2023-08-08')
        self.assertIsNotNone(md)

if __name__ == '__main__':
    unittest.main()
