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
        df = yf.download(ticker, start=start.isoformat(), end=end.isoformat(), progress=False, auto_adjust=True)
        df = df.reset_index()
        
        # Fix multi-level columns issue - flatten column names
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if col[1] == '' else col[0] for col in df.columns.values]
        
        return df

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
                    # Use correct attribute names from fast_info
                    price = finfo.get("lastPrice")
                    prev_close = finfo.get("previousClose") or finfo.get("regularMarketPreviousClose")
                else:
                    # Fallback to info dict
                    info = getattr(y, "info", {}) or {}
                    price = info.get("regularMarketPrice") or info.get("currentPrice")
                    prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
                
                pct = None
                if price is not None and prev_close not in (None, 0):
                    pct = (price - prev_close) / prev_close * 100.0
                rows.append({"ticker": t, "price": price, "prev_close": prev_close, "pct_change": pct})
            except Exception as e:
                print(f"Error fetching data for {t}: {e}")
                rows.append({"ticker": t, "price": None, "prev_close": None, "pct_change": None})
        return pd.DataFrame(rows)
