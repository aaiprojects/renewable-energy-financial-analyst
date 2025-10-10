from typing import List, Dict
from newsapi import NewsApiClient
import datetime as dt

class NewsTool:
    """
    Tool for fetching news articles using the NewsAPI.

    Note:
        NewsAPI free tier limits: 100 requests/day, 1000/month, 1 request/second.
        Exceeding these limits will result in errors or empty results.
        Articles have a 24 hour delay.
    """
    def __init__(self, api_key: str = ""):
        """
        Initialize the NewsTool with a NewsAPI key.

        Args:
            api_key (str): Your NewsAPI key. If not provided, the client will not be initialized.
        """
        self.api_key = api_key
        self.client = NewsApiClient(api_key=self.api_key) if api_key else None

    def fetch_news(self, ticker: str, days: int = 30) -> List[Dict]:
        """
        Fetch recent news articles related to a specific ticker symbol.

        Args:
            ticker (str): The ticker symbol or keyword to search for.
            days (int): Number of days in the past to search for news.

        Returns:
            List[Dict]: A list of dictionaries containing news article details.
        """        
        if not self.client:
            return []
        end = dt.date.today()
        start = end - dt.timedelta(days=days)
        query = ticker
        try:
            articles = self.client.get_everything(
                q=query,
                from_param=start.isoformat(),
                to=end.isoformat(),
                language='en',
                sort_by='relevancy',
                page_size=10
            )
        except Exception as e:
            if "rateLimited" in str(e) or "429" in str(e):
                return [{
                    "title": "Rate limit exceeded",
                    "description": "NewsAPI free tier rate limit exceeded. Please try again later.",
                    "url": ""
                }]
            return []
        results = []
        for a in articles.get("articles", []):
            results.append({
                "title": a["title"],
                "description": a["description"],
                "url": a["url"]
            })
        return results

    def fetch_sector_news(self, subsector: str | None = None, region: str | None = None, days: int = 7) -> List[Dict]:
        """
        Fetch recent sector-wide renewable energy news articles.

        Args:
            subsector (str, optional): Subsector keyword, e.g., "solar", "wind", "storage".
            region (str, optional): Region or country keyword, e.g., "US", "Europe".
            days (int): Number of days in the past to search for news.

        Returns:
            List[Dict]: A list of dictionaries containing news article details.
        """
        if not self.client:
            return []
        end = dt.date.today()
        start = end - dt.timedelta(days=days)
        # Build query string
        query_terms = ["renewable energy"]
        if subsector:
            query_terms.append(subsector)
        if region:
            query_terms.append(region)
        query = " AND ".join(query_terms)
        try:
            articles = self.client.get_everything(
                q=query,
                from_param=start.isoformat(),
                to=end.isoformat(),
                language='en',
                sort_by='relevancy',
                page_size=10
            )
        except Exception as e:
            if "rateLimited" in str(e) or "429" in str(e):
                return [{
                    "title": "Rate limit exceeded",
                    "description": "NewsAPI free tier rate limit exceeded. Please try again later.",
                    "url": ""
                }]
            return []
        results = []
        for a in articles.get("articles", []):
            results.append({
                "title": a["title"],
                "description": a["description"],
                "url": a["url"]
            })
        return results
