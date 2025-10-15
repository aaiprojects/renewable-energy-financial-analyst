"""
📊 generate_dashboard.py
------------------------
Backend utilities for the Executive Summary Pro+ Dashboard.
"""

from __future__ import annotations
import json
import glob
import os
import re
from pathlib import Path
import pandas as pd

print("💡 Running src/dashboard/generate_dashboard.py")

# ==============================================================
# 📁 Run-Loading Helpers
# ==============================================================

TICKER_RE = re.compile(r"executive_summary_([A-Z0-9\-]+)\.json$", re.I)

def _load_run_dir_jsons(run_dir: Path | str | None = ".") -> dict[str, dict]:
    """Load all executive_summary_*.json files from a directory."""
    data: dict[str, dict] = {}
    if run_dir is None:
        return data
    path = Path(run_dir)
    if not path.exists():
        return data

    for fp in path.glob("executive_summary_*.json"):
        m = TICKER_RE.search(fp.name)
        if not m:
            continue
        ticker = m.group(1).upper()
        try:
            with fp.open("r", encoding="utf-8") as f:
                data[ticker] = json.load(f)
        except Exception as e:
            print(f"[warn] Failed to read {fp}: {e}")
    return data


def get_latest_archive_dir(archive_root: Path = Path("archive")) -> Path | None:
    """Return the most recent archive directory or None."""
    if not archive_root.exists():
        return None
    dirs = [d for d in archive_root.iterdir() if d.is_dir()]
    if not dirs:
        return None
    dirs.sort(key=lambda p: p.name, reverse=True)
    return dirs[0]


def load_current_and_previous_runs() -> tuple[dict, dict, Path | None]:
    """Return (current_run_dict, previous_run_dict, previous_dir)."""
    current = _load_run_dir_jsons(Path("."))
    prev_dir = get_latest_archive_dir()
    previous = _load_run_dir_jsons(prev_dir) if prev_dir else {}
    return current, previous, prev_dir


# ==============================================================
# 📈 Delta Computation
# ==============================================================

def compute_confidence_deltas(current: dict, previous: dict) -> pd.DataFrame:
    """Build a comparison DataFrame for Streamlit display."""
    rows = []
    for ticker, cur_data in current.items():
        cur_conf = float(cur_data.get("confidence", {}).get("overall", 0))
        prev_conf = float(previous.get(ticker, {}).get("confidence", {}).get("overall", 0))
        delta = round(cur_conf - prev_conf, 2)
        direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        outlook = cur_data.get("market_outlook", "Neutral")
        agents = cur_data.get("agents", {})
        interp = extract_interpretation(agents)
        rows.append({
            "Ticker": ticker,
            "Outlook": outlook,
            "Confidence": round(cur_conf * 100, 1),
            "Delta": round(delta * 100, 1),
            "Direction": direction,
            "Interpretation": interp or "—"
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["Ticker", "Outlook", "Confidence", "Delta", "Direction", "Interpretation"])
    return df.sort_values("Ticker")


# ==============================================================
# 🧠 Text Helpers
# ==============================================================

def extract_interpretation(agents: dict) -> str:
    """Return a short interpretation paragraph from agent summaries."""
    if not agents:
        return ""
    pattern = re.compile(r"(?i)interpretation[:\-]?\s*(.+)")
    for name, payload in agents.items():
        text = payload.get("summary", "")
        if not text:
            continue
        m = pattern.search(text)
        if m:
            out = m.group(1).strip()
            out = re.split(r"\n\s*\n|[\r\n]{2,}", out)[0].strip()
            return (out[:400] + "…") if len(out) > 400 else out
    first = next(iter(agents.values()), {}).get("summary", "")
    return " ".join(first.split(".")[:2]).strip() if first else ""


# ==============================================================
# 🧮 Manual Test
# ==============================================================

if __name__ == "__main__":
    current, previous, prev_dir = load_current_and_previous_runs()
    print(f"Loaded {len(current)} current summaries, {len(previous)} previous from {prev_dir}")
    df = compute_confidence_deltas(current, previous)
    print(df.head())

