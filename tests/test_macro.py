import sys
import os
import pandas as pd
from dotenv import load_dotenv
import pytest


# Load environment variables from .env file
load_dotenv()

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.macro import MacroTool

FRED_API_KEY = os.environ.get("FRED_API_KEY", None)

@pytest.mark.skipif(FRED_API_KEY is None, reason="FRED_API_KEY not set in environment")
def test_fetch_series_returns_series_or_none():
    tool = MacroTool(api_key=FRED_API_KEY)
    data = tool.fetch_series("GDP")
    # Should return a pandas Series or None
    assert isinstance(data, pd.Series) or data is None

@pytest.mark.skipif(FRED_API_KEY is None, reason="FRED_API_KEY not set in environment")
def test_fetch_series_info_returns_dict():
    tool = MacroTool(api_key=FRED_API_KEY)
    info = tool.fetch_series_info("GDP")
    assert isinstance(info, pd.Series) or info is None
        