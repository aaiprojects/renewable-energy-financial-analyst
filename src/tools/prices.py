from typing import Any, Dict
import pandas as pd
import datetime as dt
try:
    import yfinance as yf
except Exception:
    yf = None

class PricesTool:
    def fetch_history(self, ticker: str, days: int = 30) -> pd.DataFrame | None:
        if yf is None:
            return None
        end = dt.date.today()
        start = end - dt.timedelta(days=days + 2)
        df = yf.download(ticker, start=start.isoformat(), end=end.isoformat(), progress=False)
        return df.reset_index()

    def batch_quotes(self, tickers: list[str]) -> pd.DataFrame | None:
        if yf is None:
            return None
        rows = []
        for t in tickers:
            try:
                y = yf.Ticker(t)
                finfo = getattr(y, "fast_info", None)
                price = None
                prev_close = None
                if finfo:
                    price = finfo.get("last_price")
                    prev_close = finfo.get("previous_close")
                else:
                    info = getattr(y, "info", {}) or {}
                    price = info.get("regularMarketPrice")
                    prev_close = info.get("regularMarketPreviousClose")
                pct = None
                if price is not None and prev_close not in (None, 0):
                    pct = (price - prev_close) / prev_close * 100.0
                rows.append({"ticker": t, "price": price, "prev_close": prev_close, "pct_change": pct})
            except Exception:
                rows.append({"ticker": t, "price": None, "prev_close": None, "pct_change": None})
        return pd.DataFrame(rows)
