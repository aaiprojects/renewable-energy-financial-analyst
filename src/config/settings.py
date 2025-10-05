import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in src directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def _bool_env(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1","true","yes","y","on")

@dataclass(frozen=True)
class Settings:
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    alphavantage_key: str = os.getenv("ALPHAVANTAGE_KEY", "")
    fred_api_key: str = os.getenv("FRED_API_KEY", "")
    sec_user_agent: str = os.getenv("SEC_USER_AGENT", "Your Name your-email@example.com")
    sec_api_key: str = os.getenv("SECAPI_KEY", "")
    default_lookback_days: int = int(os.getenv("DEFAULT_LOOKBACK_DAYS", "30"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enforce_renewables: bool = _bool_env("ENFORCE_RENEWABLES", False)
