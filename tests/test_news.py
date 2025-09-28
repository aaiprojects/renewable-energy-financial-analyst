import sys
import os
from dotenv import load_dotenv
import pytest

# Load environment variables from .env file
load_dotenv()

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.news import NewsTool

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", None)

@pytest.mark.skipif(NEWSAPI_KEY is None, reason="NEWSAPI_KEY not set in environment")
def test_fetch_news_returns_list():
    tool = NewsTool(api_key=NEWSAPI_KEY)
    articles = tool.fetch_news("AAPL", days=3)
    assert isinstance(articles, list)
    # If articles are returned, check expected keys
    if articles:
        assert "title" in articles[0]
        assert "description" in articles[0]
        assert "url" in articles[0]

def test_fetch_sector_news_returns_static_list():
    tool = NewsTool(api_key=NEWSAPI_KEY)
    sector_news = tool.fetch_sector_news()
    assert isinstance(sector_news, list)
    assert len(sector_news) > 0
    assert "title" in sector_news[0]
    assert "url" in sector_news[0]
    assert "tag" in sector_news[0]