STREAMLIT

import streamlit as st
import json
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Asset Failure Dashboard", layout="wide")
st.title("🔧 Asset Failure Prediction Dashboard")

uploaded_file = st.file_uploader("📁 Upload Summary JSON", type=["json"])

if uploaded_file:
    data = json.load(uploaded_file)

    # Extract data
    summary = data["overall_dashboard_summary"]
    asset_df = pd.DataFrame(data["asset_level_summaries"])
    failure_df = pd.DataFrame(list(summary["most_common_failures_last_month"].items()), columns=["Failure Type", "Count"])
    critical_assets = pd.DataFrame(summary["critical_assets"])
    top_asset_id = summary.get("most_problematic_asset_id", "N/A")
    top_asset_type = critical_assets[critical_assets["asset_id"] == top_asset_id]["asset_type"].values[0]

    st.markdown("### 📈 Executive Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Issues Logged", summary["total_issues"])
    col2.metric("Most Problematic Asset", f"{top_asset_id} ({top_asset_type})")
    col3.metric("Common Failures (last month)", ", ".join(failure_df["Failure Type"].head(2)))

    with st.expander("📌 Suggestions"):
        for suggestion in summary["any_suggestions"]:
            st.markdown(f"- {suggestion}")

    st.markdown("---")
    st.markdown("### 🔎 Failure Type Breakdown")
    fig = px.bar(failure_df, x="Failure Type", y="Count", color="Failure Type", title="Most Common Failures Last Month")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧱 Critical Assets Overview")

    # Add calculated timeline if missing
    if "avg_predicted_failure_timeline_months" not in critical_assets.columns:
        critical_assets["avg_predicted_failure_timeline_months"] = (
            critical_assets.get("avg_downtime_hours", 0) * 0.1 +
            critical_assets.get("avg_temperature", 0) * 0.05
        )

    st.dataframe(critical_assets[["asset_id", "asset_type", "issues_logged", "avg_predicted_failure_timeline_months"]])

    st.markdown("### ⏱️ Predicted Failure Timeline (Months)")
    fig2 = px.bar(
        critical_assets,
        x="asset_id",
        y="avg_predicted_failure_timeline_months",
        color="asset_type",
        title="Avg Predicted Failure Timeline per Asset"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔬 Asset-Level Summaries")
    selected_asset = st.selectbox("Select an Asset to View Details", asset_df["asset_id"].unique())
    details = asset_df[asset_df["asset_id"] == selected_asset].iloc[0]
    st.info(f"**Problem:** {details['problem']}\n\n**Recommended Solution:** {details['solution']}")

    st.markdown("---")
    st.markdown("### 📜 Final Executive Text Summary")
    st.write(data["final_text_summary"])
