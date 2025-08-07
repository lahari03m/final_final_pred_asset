import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import io

# ---------------------------
# 1. Page Setup + Theme Toggle
# ---------------------------
st.set_page_config(page_title="Asset Failure Dashboard", layout="wide", page_icon="🔧")
mode = st.radio("🌓 Choose Theme Mode", ["Light", "Dark"], horizontal=True)

if mode == "Dark":
    st.markdown("""
        <style>
        .stApp {
            background-color: #111111;
            color: #f0f0f0;
        }
        .css-1cpxqw2, .css-ffhzg2 {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("🔧 Asset Failure Prediction Dashboard")

# ---------------------------
# 2. MongoDB Setup
# ---------------------------
client = MongoClient("mongodb://localhost:27017")  # Change if needed
db = client["asset_dashboard"]
collection = db["summaries"]

# ---------------------------
# 3. Upload + Save JSON File
# ---------------------------
uploaded_file = st.file_uploader("📁 Upload Summary JSON", type=["json"])
if uploaded_file:
    file_contents = uploaded_file.read().decode("utf-8")
    data = json.loads(file_contents)
    data["filename"] = uploaded_file.name

    # Save to MongoDB if not exists
    if not collection.find_one({"filename": uploaded_file.name}):
        collection.insert_one(data)
        st.success(f"✅ Saved summary to MongoDB as `{uploaded_file.name}`")

    # Extract sections
    summary = data["overall_dashboard_summary"]
    asset_df = pd.DataFrame(data["asset_level_summaries"])
    failure_df = pd.DataFrame(
        list(summary["most_common_failures_last_month"].items()),
        columns=["Failure Type", "Count"]
    )
    critical_assets = pd.DataFrame(summary["critical_assets"])
    top_asset_id = summary.get("most_problematic_asset_id", "N/A")
    top_asset_type = critical_assets[critical_assets["asset_id"] == top_asset_id]["asset_type"].values[0]

    # ---------------------------
    # 4. Sidebar Filters
    # ---------------------------
    st.sidebar.header("🔍 Filter Options")
    asset_types = critical_assets["asset_type"].unique().tolist()
    selected_types = st.sidebar.multiselect("Filter by Asset Type", asset_types, default=asset_types)

    filtered_assets = critical_assets[critical_assets["asset_type"].isin(selected_types)]

    # Compute timeline if missing
    if "avg_predicted_failure_timeline_months" not in filtered_assets.columns:
        filtered_assets["avg_predicted_failure_timeline_months"] = (
            filtered_assets.get("avg_downtime_hours", 0) * 0.1 +
            filtered_assets.get("avg_temperature", 0) * 0.05
        )

    # ---------------------------
    # 5. Executive Summary
    # ---------------------------
    st.markdown("## 📈 Executive Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Total Issues Logged", summary["total_issues"])
    col2.metric("🚨 Most Problematic Asset", f"{top_asset_id} ({top_asset_type})")
    col3.metric("⚠️ Top Failures", ", ".join(failure_df["Failure Type"].head(2)))

    with st.expander("💡 System Recommendations"):
        for suggestion in summary["any_suggestions"]:
            st.markdown(f"- {suggestion}")

    with st.expander("📝 Final Executive Text Summary"):
        st.write(data["final_text_summary"])

    st.markdown("---")

    # ---------------------------
    # 6. Failure Breakdown
    # ---------------------------
    st.subheader("🔎 Failure Type Breakdown")
    fig1 = px.bar(
        failure_df, x="Failure Type", y="Count", color="Failure Type",
        title="Most Common Failures (Last Month)"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------
    # 7. Critical Assets Overview
    # ---------------------------
    st.subheader("🧱 Critical Assets Overview")
    st.dataframe(
        filtered_assets[["asset_id", "asset_type", "issues_logged", "avg_predicted_failure_timeline_months"]],
        use_container_width=True, hide_index=True
    )

    st.subheader("⏱️ Predicted Failure Timeline (in Months)")
    fig2 = px.bar(
        filtered_assets, x="asset_id", y="avg_predicted_failure_timeline_months", color="asset_type",
        title="Avg Predicted Failure Timeline per Asset"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ---------------------------
    # 8. Asset-Level Details
    # ---------------------------
    st.subheader("🔬 Explore Asset-Level Details")
    selected_asset = st.selectbox("📌 Select an Asset", asset_df["asset_id"].unique())
    details = asset_df[asset_df["asset_id"] == selected_asset].iloc[0]

    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:15px;border-radius:10px">
        <b>🛠️ Problem:</b> {details['problem']}<br><br>
        <b>✅ Recommended Solution:</b> {details['solution']}
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------
    # 9. Download Buttons
    # ---------------------------
    st.markdown("---")
    st.subheader("📥 Export Data")

    csv_data = filtered_assets.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Filtered Assets (CSV)", csv_data, "filtered_assets.csv", "text/csv")

    json_out = json.dumps(data, indent=2)
    st.download_button("⬇️ Download Full Summary (JSON)", json_out, "full_summary.json", "application/json")
