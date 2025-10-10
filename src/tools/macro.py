from typing import Optional, Dict
try:
    from fredapi import Fred
except ImportError:
    Fred = None

class MacroTool:
    """
    Tool for fetching macroeconomic data from FRED (Federal Reserve Economic Data).
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the MacroTool with a FRED API key.

        Args:
            api_key (str, optional): Your FRED API key.
        """
        self.api_key = api_key
        self.client = Fred(api_key=api_key) if (api_key and Fred) else None

    def fetch_series(self, series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Fetch a time series from FRED.

        Args:
            series_id (str): The FRED series ID (e.g., 'GDP', 'UNRATE').
            start_date (str, optional): Start date in 'YYYY-MM-DD' format.
            end_date (str, optional): End date in 'YYYY-MM-DD' format.

        Returns:
            pandas.Series or None: The requested time series, or None if unavailable.
        """
        if not self.client:
            return None
        try:
            data = self.client.get_series(series_id, observation_start=start_date, observation_end=end_date)
            return data
        except Exception:
            return None

    def fetch_series_info(self, series_id: str) -> Dict:
        """
        Fetch metadata about a FRED series.

        Args:
            series_id (str): The FRED series ID.

        Returns:
            dict: Metadata about the series, or empty dict if unavailable.
        """
        if not self.client:
            return {}
        try:
            info = self.client.get_series_info(series_id)
            return info
        except Exception:
            return {}