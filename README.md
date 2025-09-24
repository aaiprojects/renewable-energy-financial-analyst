# Renewable Energy Financial Analyst — Investment Research (Renewables)
Created: 2025-09-21 23:51

**Strict build:** This project uses **LangGraph + CrewAI + LangChain** (no Python orchestrator fallback).  
The Streamlit app runs the LangGraph orchestrator which invokes CrewAI specialists.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# set an LLM key for CrewAI/LangChain tools if required by your setup, e.g.:
export OPENAI_API_KEY=sk-...

streamlit run app.py
```

## Project Structure
```
src/
  agent/           # Orchestrators, Router, Evaluator, Optimizer, Memory, CrewAI crew
  tools/           # API wrappers (yfinance, NewsAPI/Kaggle stub, FRED stub, EDGAR stub), LC tools
  pipelines/       # Prompt chain (placeholders to expand)
  extractors/      # Entity/KPI extractors
  summarizers/     # News summarization helpers
  analysts/        # Market & Earnings agents (local utilities if needed)
  config/          # Settings, watchlist, logging
data/raw           # Raw artifacts
data/processed     # Processed artifacts
mem                # Cross-run learnings
docs               # Diagrams and architecture notes
```

## Requirements
- Python 3.10+ recommended
- Internet access for yfinance and news endpoints
- **LangGraph**, **CrewAI**, **LangChain** installed via `requirements.txt`

## Notes
- This repo intentionally **omits notebooks**. Use `scripts/` or Streamlit for demos.
- No orchestrator fallback is provided—LangGraph + CrewAI must be installed to run the app.
