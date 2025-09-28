import sys
import os
from dotenv import load_dotenv
import pytest

# Load environment variables from .env file
load_dotenv()

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.filings import FilingsTool

SECAPI_KEY = os.environ.get("SECAPI_KEY", None)

@pytest.mark.skipif(SECAPI_KEY is None, reason="SECAPI_KEY not set in environment")
def test_fetch_filings_returns_list():
    tool = FilingsTool(api_key=SECAPI_KEY)
    filings = tool.fetch_filings("AAPL", filing_type="10-K", limit=2)
    assert isinstance(filings, list)
    # If filings are returned, check expected keys
    if filings:
        assert "formType" in filings[0]
        assert "filedAt" in filings[0]
        assert "linkToFilingDetails" in filings[0]