import logging, os
def setup_logging(level: str | None = None):
    level = level or os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    return logging.getLogger("agentic-ai")
