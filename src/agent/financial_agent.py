# src/agent/financial_agent.py

"""
FinancialAgent
--------------
Agent responsible for analyzing stock prices and fundamentals
for renewable energy companies.
Uses yfinance for data, splits logic into price analysis vs. fundamentals.
"""

import yfinance as yf


class FinancialAgent:
    def __init__(self, name="FinancialAgent"):
        self.name = name
        self.memory = []

    def analyze_prices(self, ticker: str) -> dict:
        """Check short-term trend and latest price."""
        data = yf.Ticker(ticker).history(period="1mo")
        if data.empty:
            return {"trend": "N/A", "latest_price": "N/A"}

        start_price = data["Close"].iloc[0]
        end_price = data["Close"].iloc[-1]
        trend = "Up" if end_price > start_price else "Down"

        return {"trend": trend, "latest_price": float(end_price)}

    def analyze_fundamentals(self, ticker: str) -> dict:
        """Grab basic fundamentals."""
        stock = yf.Ticker(ticker)
        info = stock.info  # dict with lots of fields

        return {
            "sector": info.get("sector", "N/A"),
            "marketCap": info.get("marketCap", "N/A"),
            "trailingPE": info.get("trailingPE", "N/A"),
        }

    def reflect(self, output: dict) -> dict:
        """Self-reflection: flag incomplete results."""
        if "trend" not in output.get("prices", {}):
            output["reflection"] = "⚠️ Missing trend data."
        if output.get("fundamentals", {}).get("sector") == "N/A":
            output["reflection"] = "⚠️ Fundamentals incomplete."
        return output

    def run(self, ticker: str) -> dict:
        """Main pipeline for the agent."""
        prices = self.analyze_prices(ticker)
        fundamentals = self.analyze_fundamentals(ticker)

        output = {
            "prices": prices,
            "fundamentals": fundamentals,
        }

        self.memory.append(output)
        return self.reflect(output)


# Quick test
if __name__ == "__main__":
    agent = FinancialAgent()
    print(agent.run("TSLA"))  # Tesla (as renewable-ish test case)
