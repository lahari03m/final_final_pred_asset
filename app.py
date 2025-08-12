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

    # DataFrames
    summary = data["overall_dashboard_summary"]
    asset_df = pd.DataFrame(data["asset_level_summaries"])
    failure_df = pd.DataFrame(list(summary["most_common_failures_last_month"].items()),
                              columns=["Failure Type", "Count"])
    critical_assets = pd.DataFrame(summary["critical_assets"])
    
    # Identify top asset
    top_asset_id = summary.get("most_problematic_asset_id", "N/A")
    top_asset_type = critical_assets.loc[critical_assets["asset_id"] == top_asset_id, "asset_type"].values[0]

    # ===== 0️⃣ Final Executive Summary (Top Section) =====
    st.markdown("## 📜 Final Executive Text Summary")
    st.write(data["final_text_summary"])
    st.markdown("---")

    # ===== 🔍 Sidebar Filters =====
    st.sidebar.header("Filter Options")
    asset_types = critical_assets["asset_type"].unique()
    selected_types = st.sidebar.multiselect("Filter by Asset Type", asset_types, default=asset_types)
    filtered_assets = critical_assets[critical_assets["asset_type"].isin(selected_types)]

    # ===== 1️⃣ Summarization of Asset Failures =====
    st.markdown("### 1️⃣ Asset Failure Overview")
    fig_failures = px.bar(failure_df, x="Failure Type", y="Count", color="Failure Type",
                          title="Most Common Failures Last Month")
    st.plotly_chart(fig_failures, use_container_width=True)

    # ===== 2️⃣ Identification of Most Problematic Asset =====
    st.markdown("### 2️⃣ Most Problematic Asset")
    st.metric("Most Problematic Asset", f"{top_asset_id} ({top_asset_type})")
    st.dataframe(filtered_assets[filtered_assets["asset_id"] == top_asset_id],
                 use_container_width=True, hide_index=True)

    # ===== 3️⃣ Frequent Asset Usage & Forecast =====
    st.markdown("### 3️⃣ Frequent Asset Usage & Forecast")
    usage_df = pd.DataFrame(summary["asset_usage_trends"])
    fig_usage = px.line(usage_df, x="month", y="usage_count", color="asset_id",
                        title="Asset Usage Over Time")
    st.plotly_chart(fig_usage, use_container_width=True)

    # ===== 4️⃣ Most Common Failures in Past Month =====
    st.markdown("### 4️⃣ Common Failures in the Past Month")
    st.table(failure_df)

    # ===== 5️⃣ Average Predicted Failure Timeline per Asset Group =====
    st.markdown("### 5️⃣ Predicted Failure Timeline by Asset Group")
    fig_timeline = px.bar(filtered_assets, x="asset_id", y="avg_predicted_failure_timeline_months",
                          color="asset_type", title="Avg Predicted Failure Timeline (Months)")
    st.plotly_chart(fig_timeline, use_container_width=True)

    # ===== 6️⃣ Assets with Highest Usage Frequency vs Peers =====
    st.markdown("### 6️⃣ Highest Usage Frequency Compared to Peers")
    usage_freq_df = pd.DataFrame(summary["highest_usage_vs_peers"])
    fig_usage_freq = px.bar(usage_freq_df, x="asset_id", y="usage_frequency",
                            color="asset_type", title="Highest Usage vs Peers")
    st.plotly_chart(fig_usage_freq, use_container_width=True)

    # ===== ℹ️ Asset-Level Drilldown =====
    st.markdown("---")
    st.markdown("### 🔬 Asset-Level Summaries")
    selected_asset = st.selectbox("Select an Asset", asset_df["asset_id"].unique())
    details = asset_df[asset_df["asset_id"] == selected_asset].iloc[0]
    st.info(f"**Problem:** {details['problem']}\n\n**Recommended Solution:** {details['solution']}")
