import requests
from typing import List, Dict, Optional, Union
import time

EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
EDGAR_TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"
USER_AGENT = "Aresh Tajvar atajvar@sandiego.edu"  # Modify if user changes

class FilingsTool:
    """
    Tool for fetching SEC filings metadata using the official SEC EDGAR API.
    """

    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or USER_AGENT
        self._ticker_cik_map = None

    def _get_ticker_cik_map(self) -> Dict[str, str]:
        if self._ticker_cik_map is not None:
            return self._ticker_cik_map
        headers = {"User-Agent": self.user_agent}
        resp = requests.get(EDGAR_TICKER_CIK_URL, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        # The file is a dict of {index: {cik_str, ticker, title}}
        self._ticker_cik_map = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in data.values()}
        return self._ticker_cik_map

    def _get_cik(self, ticker: str) -> Optional[str]:
        ticker = ticker.upper()
        mapping = self._get_ticker_cik_map()
        return mapping.get(ticker)

    def fetch_filings(self, ticker: str, filing_type: Union[str, List[str]] = "10-K", limit: int = 5) -> List[Dict]:
        """
        Fetch recent SEC filings metadata for a given ticker and filing type(s).

        Args:
            ticker (str): The stock ticker symbol.
            filing_type (Union[str, List[str]]): The SEC filing type(s) (e.g., "10-K", "10-Q").
            limit (int): Number of filings to fetch.

        Returns:
            List[Dict]: List of filings metadata dictionaries.
        """
        cik = self._get_cik(ticker)
        if not cik:
            return []
        headers = {"User-Agent": self.user_agent}
        url = EDGAR_SUBMISSIONS_URL.format(cik=cik)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return []
        data = resp.json()
        filings = data.get("filings", {}).get("recent", {})
        # Normalize filing_type to a set for lookup
        if isinstance(filing_type, str):
            filing_type = {filing_type}
        else:
            filing_type = set(filing_type)
        results = []
        for i, form in enumerate(filings.get("form", [])):
            if form not in filing_type:
                continue
            filing = {
                "form": form,
                "filedAt": filings.get("filingDate", [])[i],
                "accessionNumber": filings.get("accessionNumber", [])[i],
                "primaryDocument": filings.get("primaryDocument", [])[i],
                "reportUrl": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{filings.get('accessionNumber', [])[i].replace('-', '')}/{filings.get('primaryDocument', [])[i]}"
            }
            results.append(filing)
            if len(results) >= limit:
                break
        # Be polite to SEC servers
        time.sleep(0.2)
        return results