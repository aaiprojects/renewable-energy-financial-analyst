# pages/2_📆_Run_History.py
import streamlit as st
import pandas as pd
import glob, os, json
from datetime import datetime
from src.dashboard.generate_dashboard import _load_run_dir_jsons

# ==============================================================
# 🧭 Page Config
# ==============================================================
st.set_page_config(
    page_title="Run History — Executive Summary Pro+",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📆 Run History Dashboard")
st.caption("Track confidence and outlook trends across archived runs.")

# ==============================================================
# 📂 Load all archived runs
# ==============================================================
archive_root = "archive"
if not os.path.isdir(archive_root):
    st.warning("⚠️ No archive directory found. Run at least one analysis with archiving enabled.")
    st.stop()

folders = sorted(
    [f for f in glob.glob(os.path.join(archive_root, "*")) if os.path.isdir(f)],
    reverse=False,
)

if not folders:
    st.warning("⚠️ No archived runs found yet.")
    st.stop()

records = []

for folder in folders:
    run_date = os.path.basename(folder)
    for file in glob.glob(os.path.join(folder, "executive_summary_*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # --- Extract ticker ---
            ticker = (
                data.get("ticker")
                or data.get("Ticker")
                or os.path.basename(file).split("_")[-1].split(".")[0].upper()
            )

            # --- Extract confidence (safe numeric) ---
            conf_data = data.get("confidence") or data.get("Confidence") or {}
            if isinstance(conf_data, dict):
                conf = conf_data.get("overall", 0)
            else:
                conf = conf_data if isinstance(conf_data, (int, float)) else 0

            # --- Extract outlook ---
            outlook = (
                data.get("market_outlook")
                or data.get("MarketOutlook")
                or "N/A"
            )

            records.append({
                "RunDate": run_date,
                "Ticker": ticker,
                "Confidence": round(float(conf) * 100, 2),
                "Outlook": outlook,
            })
        except Exception as e:
            st.warning(f"⚠️ Error reading {file}: {e}")

# --- Build DataFrame ---
df = pd.DataFrame(records)
if df.empty:
    st.warning("⚠️ No archived run data available.")
    st.stop()

df["RunDate"] = pd.to_datetime(df["RunDate"], format="%Y%m%d_%H%M", errors="coerce")

# --- Debug preview ---
st.write("✅ Sample loaded data", df.head())

# ==============================================================
# 📊 Compute Δ Confidence Between Consecutive Runs
# ==============================================================
df = df.sort_values(["Ticker", "RunDate"]).reset_index(drop=True)
df["Delta"] = 0.0
df["Direction"] = "→"

for ticker in df["Ticker"].unique():
    subset = df[df["Ticker"] == ticker].sort_values("RunDate")
    prev_val = None
    for idx, row in subset.iterrows():
        if prev_val is not None:
            delta = row["Confidence"] - prev_val
            df.loc[idx, "Delta"] = round(delta, 2)
            df.loc[idx, "Direction"] = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        prev_val = row["Confidence"]

st.write("📈 Δ Confidence computed", df.head())
# ==============================================================
# 🎛️ Interactive Filters
# ==============================================================
st.markdown("### 🎛️ Filter Settings")
tickers = sorted(df["Ticker"].unique())
sel_tickers = st.multiselect("🔍 Select Tickers", tickers, default=tickers[: min(5, len(tickers))])

if not sel_tickers:
    st.info("Select at least one ticker to view trends.")
    st.stop()

filtered = df[df["Ticker"].isin(sel_tickers)]

# ==============================================================
# 📈 Confidence Trend Over Time
# ==============================================================
st.markdown("### 📈 Confidence Trend Over Time")

try:
    import altair as alt

    chart_conf = (
        alt.Chart(filtered)
        .mark_line(point=alt.OverlayMarkDef(size=70, filled=True))
        .encode(
            x=alt.X("RunDate:T", title="Run Timestamp"),
            y=alt.Y("Confidence:Q", title="Confidence (%)"),
            color=alt.Color("Ticker:N", legend=alt.Legend(title="Ticker")),
            tooltip=["Ticker", "RunDate", "Confidence", "Outlook"],
        )
        .properties(height=400)
        .interactive()
    )

    st.altair_chart(chart_conf, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Chart rendering error: {e}")
    st.line_chart(filtered.pivot(index="RunDate", columns="Ticker", values="Confidence"))

# ==============================================================
# 📉 Confidence Δ Across Runs
# ==============================================================
st.markdown("### 📉 Confidence Δ Across Runs")

try:
    chart_delta = (
        alt.Chart(filtered)
        .mark_bar()
        .encode(
            x=alt.X("RunDate:T", title="Run"),
            y=alt.Y("Delta:Q", title="Δ Confidence (%)"),
            color=alt.Color("Ticker:N", legend=alt.Legend(title="Ticker")),
            tooltip=["Ticker", "RunDate", "Delta", "Direction"],
        )
        .properties(height=350)
        .interactive()
    )

    st.altair_chart(chart_delta, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Delta chart error: {e}")
    st.bar_chart(filtered.pivot(index="RunDate", columns="Ticker", values="Delta"))

# ==============================================================
# 📋 Raw Data + Export
# ==============================================================
st.markdown("### 📋 Raw Data")
st.dataframe(filtered.sort_values(["Ticker", "RunDate"]), use_container_width=True)

st.download_button(
    "⬇️ Export Run History (CSV)",
    filtered.to_csv(index=False).encode("utf-8"),
    "executive_summary_run_history.csv",
    "text/csv",
)

st.success("✅ Run History dashboard loaded successfully.")


