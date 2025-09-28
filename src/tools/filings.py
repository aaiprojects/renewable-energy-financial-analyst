# sec-api.io has limit 100 credits (requests) per month on free tier
# Alternative option is https://www.sec.gov/search-filings/edgar-application-programming-interfaces

from typing import List, Dict, Optional

try:
    from sec_api import QueryApi
except ImportError:
    QueryApi = None

class FilingsTool:
    """
    Tool for fetching SEC filings metadata and text using sec-api.io.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the FilingsTool with a sec-api.io API key.

        Args:
            api_key (str, optional): Your sec-api.io API key.
        """
        self.api_key = api_key
        self.query_api = QueryApi(api_key=api_key) if (api_key and QueryApi) else None

    def fetch_filings(self, ticker: str, filing_type: str = "10-K", limit: int = 5) -> List[Dict]:
        """
        Fetch recent SEC filings metadata for a given ticker and filing type.

        Args:
            ticker (str): The stock ticker symbol.
            filing_type (str): The SEC filing type (e.g., "10-K", "10-Q").
            limit (int): Number of filings to fetch.

        Returns:
            List[Dict]: List of filings metadata dictionaries.
        """
        if not self.query_api:
            # sec-api not available or no API key provided
            return []
        query = {
            "query": {
                "query_string": {
                    "query": f"ticker:{ticker} AND formType:{filing_type}"
                }
            },
            "from": "0",
            "size": str(limit),
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        response = self.query_api.get_filings(query)
        return response.get("filings", [])
