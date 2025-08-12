import streamlit as st
import json
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Asset Failure Dashboard", layout="wide")
st.title("🔧 Asset Failure Prediction Dashboard")

# 📂 Upload JSON
uploaded_file = st.file_uploader("📁 Upload Summary JSON", type=["json"])

if uploaded_file:
    data = json.load(uploaded_file)

    # Safely get sections
    summary = data.get("overall_dashboard_summary", {})
    asset_df = pd.DataFrame(data.get("asset_level_summaries", []))
    failure_df = pd.DataFrame(
        list(summary.get("most_common_failures_last_month", {}).items()),
        columns=["Failure Type", "Count"]
    )
    critical_assets = pd.DataFrame(summary.get("critical_assets", []))

    # Identify top asset safely
    top_asset_id = summary.get("most_problematic_asset_id", "N/A")
    if not critical_assets.empty and "asset_type" in critical_assets.columns:
        match = critical_assets.loc[critical_assets["asset_id"] == top_asset_id, "asset_type"]
        top_asset_type = match.values[0] if not match.empty else "Unknown"
    else:
        top_asset_type = "Unknown"

    # ===== 0️⃣ Final Executive Summary (Top Section) =====
    st.markdown("## 📜 Final Executive Text Summary")
    st.write(data.get("final_text_summary", "No summary available."))
    st.markdown("---")

    # ===== 🔍 Sidebar Filters =====
    st.sidebar.header("Filter Options")
    if not critical_assets.empty and "asset_type" in critical_assets.columns:
        asset_types = critical_assets["asset_type"].unique()
        selected_types = st.sidebar.multiselect(
            "Filter by Asset Type", asset_types, default=asset_types
        )
        filtered_assets = critical_assets[critical_assets["asset_type"].isin(selected_types)]
    else:
        filtered_assets = pd.DataFrame()

    # ===== 1️⃣ Summarization of Asset Failures =====
    st.markdown("### 1️⃣ Asset Failure Overview")
    if not failure_df.empty:
        fig_failures = px.bar(failure_df, x="Failure Type", y="Count", color="Failure Type",
                              title="Most Common Failures Last Month")
        st.plotly_chart(fig_failures, use_container_width=True)
    else:
        st.info("No failure data available.")

    # ===== 2️⃣ Identification of Most Problematic Asset =====
    st.markdown("### 2️⃣ Most Problematic Asset")
    st.metric("Most Problematic Asset", f"{top_asset_id} ({top_asset_type})")
    if not filtered_assets.empty:
        st.dataframe(filtered_assets[filtered_assets["asset_id"] == top_asset_id],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No asset data available.")

    # ===== 3️⃣ Frequent Asset Usage & Forecast =====
    st.markdown("### 3️⃣ Frequent Asset Usage & Forecast")
    if "asset_usage_trends" in summary and summary["asset_usage_trends"]:
        usage_df = pd.DataFrame(summary["asset_usage_trends"])
        fig_usage = px.line(usage_df, x="month", y="usage_count", color="asset_id",
                            title="Asset Usage Over Time")
        st.plotly_chart(fig_usage, use_container_width=True)
    else:
        st.info("No usage trend data available.")

    # ===== 4️⃣ Most Common Failures in Past Month =====
    st.markdown("### 4️⃣ Common Failures in the Past Month")
    if not failure_df.empty:
        st.table(failure_df)
    else:
        st.info("No failure data for the past month.")

    # ===== 5️⃣ Average Predicted Failure Timeline per Asset Group =====
    st.markdown("### 5️⃣ Predicted Failure Timeline by Asset Group")
    if not filtered_assets.empty and "avg_predicted_failure_timeline_months" in filtered_assets.columns:
        fig_timeline = px.bar(filtered_assets, x="asset_id", y="avg_predicted_failure_timeline_months",
                              color="asset_type", title="Avg Predicted Failure Timeline (Months)")
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No predicted failure timeline data available.")

    # ===== 6️⃣ Assets with Highest Usage Frequency vs Peers =====
    st.markdown("### 6️⃣ Highest Usage Frequency Compared to Peers")
    if "highest_usage_vs_peers" in summary and summary["highest_usage_vs_peers"]:
        usage_freq_df = pd.DataFrame(summary["highest_usage_vs_peers"])
        fig_usage_freq = px.bar(usage_freq_df, x="asset_id", y="usage_frequency",
                                color="asset_type", title="Highest Usage vs Peers")
        st.plotly_chart(fig_usage_freq, use_container_width=True)
    else:
        st.info("No usage frequency comparison data available.")

    # ===== ℹ️ Asset-Level Drilldown =====
    st.markdown("---")
    st.markdown("### 🔬 Asset-Level Summaries")
    if not asset_df.empty and "asset_id" in asset_df.columns:
        selected_asset = st.selectbox("Select an Asset", asset_df["asset_id"].unique())
        details = asset_df[asset_df["asset_id"] == selected_asset].iloc[0]
        st.info(f"**Problem:** {details.get('problem', 'N/A')}\n\n**Recommended Solution:** {details.get('solution', 'N/A')}")
    else:
        st.info("No detailed asset-level summaries available.")
