import sys
import os 
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from src.tools.prices import PricesTool
import pandas as pd

class TestPricesTool(unittest.TestCase):
    def setUp(self):
        self.tool = PricesTool()

    def test_fetch_history_returns_dataframe_or_none(self):
        # Should return a DataFrame or None if yfinance is not installed
        result = self.tool.fetch_history("AAPL", days=5)
        self.assertTrue(isinstance(result, pd.DataFrame) or result is None)

    def test_batch_quotes_returns_dataframe_or_none(self):
        # Should return a DataFrame or None if yfinance is not installed
        result = self.tool.batch_quotes(["AAPL", "MSFT"])
        self.assertTrue(isinstance(result, pd.DataFrame) or result is None)

    def test_batch_quotes_dataframe_columns(self):
        result = self.tool.batch_quotes(["AAPL"])
        if isinstance(result, pd.DataFrame):
            self.assertIn("ticker", result.columns)
            self.assertIn("price", result.columns)
            self.assertIn("prev_close", result.columns)
            self.assertIn("pct_change", result.columns)

if __name__ == "__main__":
    unittest.main()
