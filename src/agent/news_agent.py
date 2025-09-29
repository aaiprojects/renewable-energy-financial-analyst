# src/agent/news_agent.py

"""
NewsAgent
----------
Agent responsible for ingesting financial news,
classifying sentiment, extracting renewable-specific themes,
and summarizing content for downstream analysis.
"""

from textblob import TextBlob
import re


class NewsAgent:
    def __init__(self, name="NewsAgent"):
        self.name = name
        self.memory = []  # simple log of past runs

    def preprocess(self, text: str) -> str:
        """Clean up whitespace and formatting."""
        return re.sub(r"\s+", " ", text.strip())

    def classify_sentiment(self, text: str) -> str:
        """Classify sentiment using polarity score."""
        analysis = TextBlob(text)
        return "Positive" if analysis.sentiment.polarity > 0 else "Negative"

    def extract_themes(self, text: str) -> list:
        """Look for renewable-specific keywords/themes."""
        keywords = ["solar", "wind", "EV", "climate", "carbon", "subsidy", "policy"]
        return [word for word in keywords if word.lower() in text.lower()]

    def summarize(self, text: str) -> str:
        """Basic summary (first 200 chars)."""
        return text[:200] + "..." if len(text) > 200 else text

    def reflect(self, output: dict) -> dict:
        """Self-reflection: flag if output looks incomplete."""
        if not output.get("summary"):
            output["reflection"] = "⚠️ Summary missing."
        if not output.get("themes"):
            output["reflection"] = "⚠️ No themes detected."
        return output

    def run(self, news_text: str) -> dict:
        """Main pipeline for the agent."""
        cleaned = self.preprocess(news_text)
        sentiment = self.classify_sentiment(cleaned)
        themes = self.extract_themes(cleaned)
        summary = self.summarize(cleaned)

        output = {
            "sentiment": sentiment,
            "themes": themes,
            "summary": summary,
        }

        self.memory.append(output)
        return self.reflect(output)
    
if __name__ == "__main__":
        agents = NewsAgent()
        text = "The government announced new subsidies for solar and wind energy this quarter."
        print(agents.run(text))

