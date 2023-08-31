import unittest
from ikbr.paper_trading_app.universe.universe_selector import UniverseSelector

class UniverseSelectorTestCase(unittest.TestCase):
    us = UniverseSelector()
    def test_read_universe(self):
        univ = self.us.read_universe()
        self.assertIsNotNone(univ)

    def test_get_universe_based_on_volume_50(self):
        univ = self.us.get_universe_based_on_volume()
        self.assertEqual(len(univ),50)

    def test_get_universe_based_on_volume_100(self):
        univ = self.us.get_universe_based_on_volume(count=100)
        self.assertEqual(len(univ),100)

    def test_get_universe_based_on_market_cap_50(self):
        univ = self.us.get_universe_based_on_market_cap()
        self.assertEqual(len(univ),50)

    def test_get_universe_based_on_market_cap_100(self):
        univ = self.us.get_universe_based_on_market_cap(count=100)
        self.assertEqual(len(univ),100)


if __name__ == '__main__':
    unittest.main()
