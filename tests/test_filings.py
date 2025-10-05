import sys
import os
from dotenv import load_dotenv
import pytest

# Load environment variables from .env file
load_dotenv()

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.filings import FilingsTool

def test_fetch_filings_returns_list():
    tool = FilingsTool()
    filings = tool.fetch_filings("AAPL", filing_type="10-K", limit=2)
    assert isinstance(filings, list)
    # If filings are returned, check expected keys
    if filings:
        assert "form" in filings[0]
        assert "filedAt" in filings[0]
        assert "accessionNumber" in filings[0]
        assert "primaryDocument" in filings[0]
        assert "reportUrl" in filings[0]

def test_invalid_ticker_returns_empty():
    tool = FilingsTool()
    filings = tool.fetch_filings("INVALIDTICKER", filing_type="10-K", limit=2)
    assert filings == []

def test_no_filings_of_type_returns_empty():
    tool = FilingsTool()
    # Assuming "AAPL" has no "S-1" filings recently
    filings = tool.fetch_filings("AAPL", filing_type="S-1", limit=2)
    assert filings == []

def test_limit_parameter():
    tool = FilingsTool()
    filings = tool.fetch_filings("AAPL", filing_type="10-K", limit=1)
    assert len(filings) <= 1