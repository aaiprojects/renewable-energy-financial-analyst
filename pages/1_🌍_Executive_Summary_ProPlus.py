import streamlit as st
import pandas as pd
import glob
import os
import altair as alt
import json
import streamlit.components.v1 as components
from datetime import datetime
from src.dashboard.generate_dashboard import load_current_and_previous_runs, compute_confidence_deltas

# ==============================================================
# 🌍 Page Config & Branding Header
# ==============================================================
st.set_page_config(page_title="Renewable Energy Financial Analyst | Executive Summary Pro+", layout="wide")

st.markdown("""
<style>
@keyframes glowPulse {
  0% { text-shadow: 0 0 4px #00d4ff, 0 0 10px #00d4ff, 0 0 20px #00d4ff; }
  100% { text-shadow: 0 0 2px #00d4ff, 0 0 6px #00d4ff, 0 0 12px #00d4ff; }
}
.main-title {
  font-size: 2.7rem;
  color: #00d4ff;
  text-align: center;
  animation: glowPulse 2s ease-in-out infinite alternate;
  margin-top: 40px;
  letter-spacing: 1px;
}
.subtitle {
  text-align: center;
  color: #b0b0b0;
  font-size: 1rem;
  margin-top: -10px;
}
[data-testid="stSidebar"] {
    background-color: #111418;
    border-right: 1px solid rgba(0, 212, 255, 0.2);
}
</style>

<h1 class="main-title">Renewable Energy Financial Analyst</h1>
<p class="subtitle">Executive Summary Pro+ | Multi-Agent Market Intelligence Dashboard ⚙️</p>
""", unsafe_allow_html=True)

st.divider()

# ==============================================================
# 🧭 Sidebar Filters
# ==============================================================
with st.sidebar:
    st.header("Filters")
    ticker_search = st.text_input("🔍 Search Ticker")
    outlook_filter = st.selectbox("📈 Market Outlook", ["All", "Positive", "Negative", "Neutral"])
    view_mode = st.radio("🪟 View Mode", ["Cards", "Table"])
    st.markdown("---")
    st.caption("💡 Tip: Use multi-word search (e.g., ENPH SEDG) to view multiple tickers.")


# ==============================================================
# 🗂️ Load Run Summaries (direct from archive)
# ==============================================================
try:
    files = glob.glob("archive/*/executive_summary_*.json")
    records = []
    for f in files:
        try:
            data = json.load(open(f))
            conf = data.get("confidence", {})
            if isinstance(conf, dict):
                conf_val = conf.get("overall")
            else:
                conf_val = conf

            records.append({
                "Ticker": os.path.basename(f).split("_")[-1].split(".")[0],
                "Confidence": conf_val,
                "Outlook": data.get("market_outlook"),
                "Run Timestamp": os.path.basename(os.path.dirname(f))
            })
        except Exception as e:
            st.warning(f"Error parsing {f}: {e}")

    df = pd.DataFrame(records)
    if not df.empty and df["Confidence"].max() <= 1:
        df["Confidence"] = df["Confidence"] * 100

    # normalize confidence
    def extract_confidence(entry, agents=None):
        try:
            if isinstance(entry, (float, int)):
                return entry
            if isinstance(entry, dict) and "overall" in entry:
                return entry["overall"]
            if agents and isinstance(agents, dict):
                confs, weights = [], []
                for a in agents.values():
                    confs.append(a.get("confidence", 0))
                    weights.append(a.get("weight", 1))
                if confs:
                    return round(sum(c * w for c, w in zip(confs, weights)) / sum(weights), 3)
            return None
        except Exception:
            return None

    if "Confidence" in df.columns:
        df["Confidence"] = df["Confidence"].apply(extract_confidence)

    if not df.empty:
        df.sort_values(["Ticker", "Run Timestamp"], inplace=True)
        df["Delta"] = df.groupby("Ticker")["Confidence"].diff().fillna(0)
        df["Direction"] = df["Delta"].apply(lambda x: "↑" if x > 0 else ("↓" if x < 0 else "→"))
    else:
        st.warning("⚠️ No data found in archive folders.")

    df["Run Timestamp"] = pd.to_datetime(df["Run Timestamp"], format="%Y%m%d_%H%M", errors="coerce")
    df = df.dropna(subset=["Run Timestamp", "Confidence"])

except Exception as e:
    st.error(f"Error loading summaries: {e}")
    st.stop()


# ==============================================================
# 🧠 Run Health Summary
# ==============================================================
try:
    num_up = sum(df["Delta"] > 0)
    num_down = sum(df["Delta"] < 0)
    num_flat = sum(df["Delta"] == 0)
    avg_delta = df["Delta"].mean()

    st.markdown("<h3>🧠 Run Health Summary</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("↑ Improved", int(num_up))
    c2.metric("↓ Declined", int(num_down))
    c3.metric("→ No Change", int(num_flat))
    c4.metric("Avg Δ Confidence", f"{avg_delta:.2f}%")

    latest_ts = df["Run Timestamp"].max()
    st.markdown(
        f"<div style='font-size:12px;color:gray;margin-top:-10px;'>⏱️ Last updated: <b>{latest_ts.strftime('%Y-%m-%d %H:%M')}</b></div>",
        unsafe_allow_html=True,
    )
    st.divider()
except Exception as e:
    st.warning(f"⚠️ Unable to compute run health summary: {e}")


# ==============================================================
# 📈 Confidence Trend Over Time
# ==============================================================
st.markdown("### 📈 Confidence Trend Over Time")
try:
    df_plot = (
        df.dropna(subset=["Confidence", "Run Timestamp"])
        .query("Confidence > 0")
        .sort_values(["Ticker", "Run Timestamp"])
    )

    base = alt.Chart(df_plot).encode(
        x=alt.X("Run Timestamp:T", title="Run Timestamp"),
        y=alt.Y("Confidence:Q", title="Confidence (%)", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("Ticker:N", legend=alt.Legend(title="Ticker")),
        tooltip=[
            alt.Tooltip("Ticker:N"),
            alt.Tooltip("Run Timestamp:T"),
            alt.Tooltip("Confidence:Q", format=".2f"),
            alt.Tooltip("Delta:Q", title="Δ Confidence", format="+.2f"),
        ],
    )

    gradient = base.mark_area(interpolate="monotone", opacity=0.25)
    line = base.mark_line(interpolate="monotone", strokeWidth=3)
    points = base.mark_point(filled=True, size=80, opacity=0.8)

    st.altair_chart(
        (gradient + line + points)
        .interactive()
        .configure_view(strokeWidth=0)
        .properties(height=320),
        use_container_width=True
    )
except Exception as e:
    st.warning(f"⚠️ Could not render trend chart: {e}")


# ==============================================================
# 📊 Confidence Δ Across Runs
# ==============================================================
st.markdown("### 📊 Confidence Δ Across Runs")
try:
    delta_chart = (
        alt.Chart(df_plot)
        .mark_bar(opacity=0.8)
        .encode(
            x=alt.X("Run Timestamp:T", title="Run Timestamp"),
            y=alt.Y("Delta:Q", title="Δ Confidence (%)"),
            color=alt.Color("Ticker:N", legend=None),
            tooltip=[
                alt.Tooltip("Ticker:N"),
                alt.Tooltip("Run Timestamp:T"),
                alt.Tooltip("Delta:Q", format="+.2f"),
            ],
        )
        .properties(height=200)
    )
    st.altair_chart(delta_chart.configure_view(strokeWidth=0), use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ Could not render delta chart: {e}")


# ==============================================================
# 🧾 Latest Confidence Snapshot
# ==============================================================
st.markdown("### 🧾 Latest Confidence Snapshot")
try:
    latest_df = df_plot.sort_values("Run Timestamp").groupby("Ticker").tail(1)
    cols = st.columns(len(latest_df))
    for i, row in enumerate(latest_df.itertuples()):
        delta_arrow = "🟩↑" if row.Delta > 0 else "🟥↓" if row.Delta < 0 else "⬜→"
        cols[i].markdown(
            f"""
            <div style='background-color:#1E1E1E;padding:15px;border-radius:12px;
                        box-shadow:0 0 8px rgba(0,0,0,0.3);text-align:center;'>
                <h4 style='margin-bottom:4px;color:#fff;'>{row.Ticker}</h4>
                <p style='margin:0;font-size:18px;color:#00b4d8;'><b>{row.Confidence:.1f}%</b></p>
                <p style='margin:0;font-size:14px;color:gray;'>Δ {row.Delta:.2f}% {delta_arrow}</p>
                <p style='margin-top:2px;font-size:12px;color:#777;'>Outlook: {row.Outlook or '—'}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
except Exception as e:
    st.warning(f"⚠️ Could not render snapshot cards: {e}")


# ==============================================================
# 🔄 Footer + Export
# ==============================================================
last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
components.html(f"""
<style>
.refresh-badge {{
  position: fixed;
  top: 12px;
  right: 22px;
  background: linear-gradient(90deg, #0099f7, #00d4ff);
  color: white;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-family: 'Inter', sans-serif;
  box-shadow: 0 0 10px rgba(0,0,0,0.4);
  z-index: 9999;
}}
</style>
<div class="refresh-badge">🔄 Refreshed: {last_refresh}</div>
""", height=0)

if not df.empty:
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Download Full Run History (CSV)",
        data=csv_data,
        file_name=f"executive_summary_run_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
        help="Export all run metrics with deltas and timestamps"
    )
