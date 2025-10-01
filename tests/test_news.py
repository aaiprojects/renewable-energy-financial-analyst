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

def test_fetch_sector_news_returns_list():
    tool = NewsTool(api_key=NEWSAPI_KEY)
    sector_news = tool.fetch_sector_news(subsector="solar", region="US", days=3)
    assert isinstance(sector_news, list)
    if sector_news:
        assert "title" in sector_news[0]
        assert "description" in sector_news[0]
        assert "url" in sector_news[0]

def test_fetch_news_empty_on_invalid_key():
    tool = NewsTool(api_key="INVALID_KEY")
    news = tool.fetch_news("TSLA", days=7)
    assert news == []

def test_fetch_sector_news_empty_on_invalid_key():
    tool = NewsTool(api_key="INVALID_KEY")
    news = tool.fetch_sector_news(subsector="solar", region="US", days=7)
    assert news == []