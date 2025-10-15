# view_dashboard.py — Executive Summary Pro Dashboard (Streamlit Full Pro)
# Run: streamlit run view_dashboard.py

from __future__ import annotations
import json, re, os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import altair as alt
import streamlit as st

# =========================
# ---- Styling / Theme ----
# =========================
st.set_page_config(page_title="Executive Summary Dashboard", layout="wide")

st.markdown(
    """
    <style>
      :root {
        --bg: #0f1117;
        --panel: #171a23;
        --muted: #98a2b3;
        --text: #e5e7eb;
        --green: #22c55e;
        --red: #ef4444;
        --yellow: #f59e0b;
        --card: #1c2130;
        --accent: #3b82f6;
      }
      .block-container {padding-top: 1.2rem; max-width: 1200px;}
      .pro-card {
        background: var(--card);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.22);
        transition: transform .12s ease, box-shadow .12s ease;
      }
      .pro-card:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0,0,0,0.28); }
      .kpi-label { font-size: 0.95rem; color: var(--muted); letter-spacing: .05em; }
      .kpi-value { font-size: 2rem; font-weight: 700; color: white; line-height: 1.1; }
      .pill {
        display:inline-flex; align-items:center; gap:.4rem;
        padding:.28rem .6rem; border-radius: 999px; font-weight:600; font-size:.85rem;
        background: rgba(255,255,255,.07); color: var(--text);
      }
      .pill.up { background: rgba(34,197,94,.16); color: var(--green); }
      .pill.down { background: rgba(239,68,68,.16); color: var(--red); }
      .pill.flat { background: rgba(148,163,184,.16); color: #9aa7b4; }
      .pill.out-bullish { background: rgba(34,197,94,.18); color: var(--green); }
      .pill.out-neutral { background: rgba(245,158,11,.2); color: var(--yellow); }
      .pill.out-bearish { background: rgba(239,68,68,.18); color: var(--red); }
      .muted { color: var(--muted); font-size: .9rem; }
      .info-dot {
        display:inline-block; width:18px; height:18px; line-height:18px; text-align:center;
        border-radius:50%; background: rgba(255,255,255,.08); color:#aab3c2;
        font-size:.8rem; cursor:default; margin-left:.4rem;
      }
      .tooltip { position:relative; display:inline-block; }
      .tooltip .tiptext {
        visibility:hidden; max-width: 520px; background:#0b0e14; color: #e5e7eb;
        text-align:left; border:1px solid rgba(255,255,255,.06);
        border-radius:10px; padding:10px 12px; position:absolute; z-index:9999;
        top: 125%; left: 0; box-shadow: 0 10px 24px rgba(0,0,0,.35);
      }
      .tooltip:hover .tiptext { visibility: visible; }
      .spark-wrap { margin-top:.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================
# ---- Data Loading ----
# ======================

TICKER_RE = re.compile(r"executive_summary_([A-Z]+)\.json$", re.I)
ARCHIVE_RE = re.compile(r"(\d{8})_(\d{4})")  # YYYYMMDD_HHMM

@st.cache_data(show_spinner=False)
def load_run(dirpath: Path) -> Dict[str, dict]:
    """Load all executive_summary_*.json in dirpath into {ticker: json}."""
    if not dirpath or not dirpath.exists():
        return {}
    out = {}
    for fp in dirpath.glob("executive_summary_*.json"):
        m = TICKER_RE.search(fp.name)
        if not m: 
            continue
        t = m.group(1).upper()
        try:
            out[t] = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return out

@st.cache_data(show_spinner=False)
def discover_archives(root: Path = Path("archive")) -> List[Path]:
    if not root.exists(): return []
    ds = [d for d in root.iterdir() if d.is_dir()]
    ds.sort(key=lambda p: p.name, reverse=True)
    return ds

@st.cache_data(show_spinner=False)
def parse_archive_ts(name: str) -> datetime | None:
    m = ARCHIVE_RE.search(name)
    if not m: return None
    ymd, hm = m.groups()
    try:
        return datetime.strptime(f"{ymd}_{hm}", "%Y%m%d_%H%M")
    except Exception:
        return None

def interpretation_from_agents(agents: dict) -> str:
    if not agents: return ""
    # preference order
    prio = ["Earnings", "Valuation", "Momentum"]
    ordered = list(agents.items())
    # move priority agents up
    ordered.sort(key=lambda kv: (0 if any(p.lower() in kv[0].lower() for p in prio) else 1, kv[0]))
    for _, payload in ordered:
        txt = (payload or {}).get("summary", "")
        if not txt: 
            continue
        # pull after "Interpretation:"
        m = re.search(r"(?i)interpretation:\s*(.+)", txt, flags=re.DOTALL)
        if m:
            snippet = m.group(1).strip()
            snippet = re.split(r"\n\s*\n|[\r\n]{2,}", snippet)[0].strip()
            return (snippet[:500] + "…") if len(snippet) > 500 else snippet
    return ""

# ==================================
# ---- Current + History Frames ----
# ==================================

@st.cache_data(show_spinner=False)
def build_frames() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[Tuple[datetime,float]]], List[Tuple[str,Path]]]:
    """Returns:
       - df_current: ticker, confidence, outlook, interpretation
       - df_latest_prev: same schema for latest archive (if exists)
       - history: {ticker: [(ts, conf), ...]} across archives + current
       - archives_list: [(label, path)]
    """
    cwd = Path(".")
    current = load_run(cwd)
    rows = []
    for t, d in current.items():
        conf = float((d.get("confidence", {}) or {}).get("overall", 0))
        outlook = d.get("market_outlook", "N/A")
        interp = interpretation_from_agents(d.get("agents", {}))
        rows.append({"ticker": t, "confidence": conf, "outlook": outlook, "interpretation": interp})
    df_current = pd.DataFrame(rows).sort_values("ticker")

    # archives
    archives = discover_archives()
    archives_list = [(p.name, p) for p in archives]
    history: Dict[str, List[Tuple[datetime, float]]] = {t: [] for t in df_current["ticker"].unique()}

    # fill history from archives
    for p in reversed(archives):  # oldest → newest
        ts = parse_archive_ts(p.name) or datetime.min
        run = load_run(p)
        for t in history.keys():
            conf = float((run.get(t, {}).get("confidence", {}) or {}).get("overall", 0)) if t in run else None
            if conf is not None:
                history[t].append((ts, conf))

    # include current (now)
    now = datetime.now()
    for t, d in current.items():
        conf = float((d.get("confidence", {}) or {}).get("overall", 0))
        history.setdefault(t, []).append((now, conf))

    # latest previous df (baseline = latest archive)
    if archives:
        latest_prev = load_run(archives[0])
        prev_rows = []
        for t in df_current["ticker"]:
            d = latest_prev.get(t, {})
            conf = float((d.get("confidence", {}) or {}).get("overall", 0)) if d else 0.0
            outlook = d.get("market_outlook", "N/A") if d else "N/A"
            interp = interpretation_from_agents(d.get("agents", {})) if d else ""
            prev_rows.append({"ticker": t, "confidence": conf, "outlook": outlook, "interpretation": interp})
        df_latest_prev = pd.DataFrame(prev_rows).sort_values("ticker")
    else:
        df_latest_prev = pd.DataFrame(columns=["ticker","confidence","outlook","interpretation"])

    return df_current, df_latest_prev, history, archives_list

def compute_deltas(df_now: pd.DataFrame, df_prev: pd.DataFrame) -> pd.DataFrame:
    prev_map = df_prev.set_index("ticker")["confidence"].to_dict() if not df_prev.empty else {}
    def _d(t, c):
        p = float(prev_map.get(t, 0))
        d = round(float(c) - p, 2)
        direction = "up" if d > 0 else "down" if d < 0 else "flat"
        arrow = "↑" if d > 0 else "↓" if d < 0 else "→"
        return d, direction, f"{arrow} {abs(d):.2f}"
    out = df_now.copy()
    triples = out.apply(lambda r: _d(r["ticker"], r["confidence"]), axis=1)
    out["delta"], out["direction"], out["delta_text"] = zip(*triples)
    return out

# ==============================
# ---- Sidebar: Controls UI ----
# ==============================

df_now, df_prev_latest, history, archives_list = build_frames()

with st.sidebar:
    st.header("Controls")
    # baseline archive selector
    if archives_list:
        label_to_path = {label: path for label, path in archives_list}
        default_label = archives_list[0][0]
        baseline_label = st.selectbox(
            "Compare against archive:",
            options=[lbl for lbl,_ in archives_list],
            index=0,
            help="Deltas are computed vs this archived run.",
        )
        # recompute prev df based on chosen baseline
        df_prev_choice = load_run(label_to_path[baseline_label])
        df_prev_choice = pd.DataFrame([
            {
                "ticker": t,
                "confidence": float((d.get("confidence", {}) or {}).get("overall", 0)),
                "outlook": d.get("market_outlook", "N/A"),
                "interpretation": interpretation_from_agents(d.get("agents", {})),
            }
            for t, d in df_prev_choice.items()
        ])
    else:
        st.info("No archives found in ./archive — deltas will show vs 0.0")
        df_prev_choice = df_prev_latest  # empty

    # search & outlook filter
    q = st.text_input("Search ticker…", "")
    outlook_filter = st.selectbox("Outlook", ["All","Bullish","Neutral","Bearish"], index=0)
    view_mode = st.radio("View", ["Cards","Table"], horizontal=True)

# recompute deltas for baseline
df = compute_deltas(df_now, df_prev_choice)

# apply filters
if q.strip():
    df = df[df["ticker"].str.contains(q.strip(), case=False, regex=False)]
if outlook_filter != "All":
    df = df[df["outlook"].str.contains(outlook_filter, case=False, regex=False)]

st.title("📈 Executive Summary Pro Dashboard")

# ==========================
# ---- Helper components ----
# ==========================

def outlook_class(outlook: str) -> str:
    if "Bullish" in outlook: return "out-bullish"
    if "Neutral" in outlook: return "out-neutral"
    return "out-bearish"

def render_sparkline(ticker: str):
    series = history.get(ticker, [])
    if not series:
        st.caption("—")
        return
    df_s = pd.DataFrame(series, columns=["ts","confidence"]).sort_values("ts")
    chart = (
        alt.Chart(df_s)
        .mark_line(point=False)
        .encode(
            x=alt.X("ts:T", axis=None),
            y=alt.Y("confidence:Q", axis=None, scale=alt.Scale(domain=[0,1])),
        )
        .properties(height=36)
    )
    st.altair_chart(chart, use_container_width=True)

def info_tooltip_html(text: str) -> str:
    safe = (text or "").replace('"', "&quot;")
    # tooltip via pure CSS (shows on hover)
    return f"""
    <span class="tooltip">
      <span class="info-dot">i</span>
      <span class="tiptext">{safe}</span>
    </span>
    """

# =======================
# ---- Main rendering ----
# =======================

if view_mode == "Cards":
    # 2-column responsive grid
    cols = st.columns(2)
    for i, row in enumerate(df.sort_values("ticker").itertuples(index=False)):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="pro-card">
                  <div class="kpi-label">{row.ticker} {info_tooltip_html(row.interpretation)}</div>
                  <div class="kpi-value">{row.confidence:.2f}</div>
                  <div style="display:flex; gap:.5rem; align-items:center; flex-wrap:wrap;">
                    <span class="pill {'up' if row.direction=='up' else 'down' if row.direction=='down' else 'flat'}">
                      {row.delta_text}
                    </span>
                    <span class="pill {outlook_class(row.outlook)}">{row.outlook}</span>
                  </div>
                  <div class="spark-wrap">
                    """,
                unsafe_allow_html=True,
            )
            render_sparkline(row.ticker)
            st.markdown("</div></div>", unsafe_allow_html=True)
else:
    # Table view
    table = df[["ticker","confidence","delta","delta_text","direction","outlook","interpretation"]].copy()
    table = table.rename(columns={
        "ticker":"Ticker",
        "confidence":"Confidence",
        "delta":"Δ (abs)",
        "delta_text":"Δ (display)",
        "direction":"Trend",
        "outlook":"Outlook",
        "interpretation":"Interpretation",
    })
    # style direction with emojis for readability
    table["Trend"] = table["Trend"].map({"up":"↑ up","down":"↓ down","flat":"→ flat"})
    st.dataframe(
        table.sort_values(["Ticker"]).reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

# ======================
# ---- CSV Download ----
# ======================
@st.cache_data(show_spinner=False)
def to_csv_bytes(df_: pd.DataFrame) -> bytes:
    return df_.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download CSV (current view)",
    data=to_csv_bytes(df),
    file_name="executive_summary_dashboard.csv",
    mime="text/csv",
    use_container_width=False,
    type="secondary",
)
