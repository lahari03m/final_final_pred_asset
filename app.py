import streamlit as st
import json
import pandas as pd

# Load the output JSON
uploaded_file = st.file_uploader("📁 Upload Summary JSON", type=["json"])
if uploaded_file:
    data = json.load(uploaded_file)

    summary_data = data["overall_dashboard_summary"]
    failures = summary_data["most_common_failures_last_month"]

    failure_counts_df = pd.DataFrame(list(failures.items()), columns=["Failure Mode", "Count"])
    top_failures_text = ', '.join(f"{row['Failure Mode']} ({row['Count']})" for _, row in failure_counts_df.iterrows())

    top_asset_id = summary_data.get("most_problematic_asset_id", "N/A")
    critical_assets_df = pd.DataFrame(summary_data["critical_assets"])
    most_problematic_type = critical_assets_df[critical_assets_df["asset_id"] == top_asset_id]["asset_type"].values
    most_problematic_type = most_problematic_type[0] if len(most_problematic_type) > 0 else "Unknown"

    usage_forecast_df = critical_assets_df[["asset_id", "issues_logged"]].sort_values(by="issues_logged", ascending=False)
    frequent_usage_assets = usage_forecast_df.head(3).to_dict("records")

    critical_assets_df["avg_predicted_failure_timeline_months"] = (
        critical_assets_df["avg_downtime_hours"] * 0.1 + critical_assets_df.get("avg_temperature", 0) * 0.05
    )
    timeline_avg = round(critical_assets_df["avg_predicted_failure_timeline_months"].mean(), 2)

    highest_usage_asset = usage_forecast_df.iloc[0]["asset_id"]

    kpi_summary = (
        f"**Asset Failure Summary:** A total of **{summary_data['total_issues']}** issues were logged across "
        f"**{len(critical_assets_df)} critical assets**. The most problematic asset is **{top_asset_id}** "
        f"(Type: **{most_problematic_type}**). Common failure types last month include: {top_failures_text}. "
        f"The average predicted failure timeline across asset groups is approximately **{timeline_avg} months**, "
        f"based on downtime and sensor readings. Assets with highest usage frequency include: "
        f"{', '.join(str(a['asset_id']) for a in frequent_usage_assets)}. The asset with the highest usage is "
        f"**{highest_usage_asset}**."
    )

    st.header("📊 Executive KPI Summary")
    st.markdown(kpi_summary)

    st.subheader("📍 Suggestions")
    for s in summary_data["any_suggestions"]:
        st.markdown(f"- {s}")

    st.subheader("🔎 Asset-Level Insights")
    asset_df = pd.DataFrame(data["asset_level_summaries"])
    st.dataframe(asset_df)

    st.subheader("🧾 Final Summary Report")
    st.write(data["final_text_summary"])
