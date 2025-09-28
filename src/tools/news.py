from typing import List, Dict
from newsapi import NewsApiClient
import datetime as dt

class NewsTool:
    """
    Tool for fetching news articles using the NewsAPI.
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
        articles = self.client.get_everything(
            q=query,
            from_param=start.isoformat(),
            to=end.isoformat(),
            language='en',
            sort_by='relevancy',
            page_size=10
        )
        results = []
        for a in articles.get("articles", []):
            results.append({
                "title": a["title"],
                "description": a["description"],
                "url": a["url"]
            })
        return results

    # TODO: Sector news
    def fetch_sector_news(self, subsector: str | None = None, region: str | None = None, days: int = 7):
        base = [
            {"title": "US expands solar tax credits under IRA", "url": "https://example.com/policy1", "tag": "policy"},
            {"title": "Wind installations rebound in EU", "url": "https://example.com/wind1", "tag": "market"},
            {"title": "Battery costs decline 8% YoY", "url": "https://example.com/storage1", "tag": "tech"},
        ]
        return base
