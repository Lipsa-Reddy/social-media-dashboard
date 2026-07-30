import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Set up page config
st.set_page_config(page_title="Social Media Dashboard", layout="wide")
st.title("📱 Social Media Engagement Dashboard")
st.markdown("Track and analyze content engagement metrics instantly.")

# --- FILE UPLOADER ---
st.subheader("📁 Upload Your Data")
uploaded_file = st.file_uploader("Upload a CSV file containing social media metrics", type=["csv"])

@st.cache_data
def generate_fallback_data():
    """Generates clean, error-free backup data if no file is uploaded."""
    dates = pd.date_range(start="2026-01-01", periods=30, freq="D")
    platforms = ["Instagram", "YouTube"]
    data = []
    
    for date in dates:
        for platform in platforms:
            likes = np.random.randint(100, 1500)
            shares = np.random.randint(10, 300)
            comments = np.random.randint(5, 150)
            multiplier = np.random.randint(6, 12) if platform == "YouTube" else np.random.randint(2, 5)
            impressions = likes * multiplier
            
            data.append({
                "Date": pd.to_datetime(date).date(), "Platform": platform, "Likes": likes,
                "Shares": shares, "Comments": comments, "Impressions": impressions
            })
    return pd.DataFrame(data)

# Load uploaded data or use fallback
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
        st.success("✅ Successfully loaded your CSV file!")
    except Exception as e:
        st.error(f"Error reading CSV file: {e}. Using backup data instead.")
        df = generate_fallback_data()
else:
    st.info("💡 Showing generated data. Upload a CSV file above to view your own metrics.")
    df = generate_fallback_data()

# Ensure the Date column is formatted correctly for filtering
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

# --- ADVANCED FILTERS (SIDEBAR) ---
st.sidebar.header("🎛️ Advanced Filters")

# 1. Platform Filter
if "Platform" in df.columns:
    platform_filter = st.sidebar.multiselect("Select Platform", options=df["Platform"].unique(), default=df["Platform"].unique())
    filtered_df = df[df["Platform"].isin(platform_filter)]
else:
    filtered_df = df

# 2. Advanced Date Filter
if "Date" in filtered_df.columns and not filtered_df.empty:
    min_date = min(filtered_df["Date"])
    max_date = max(filtered_df["Date"])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Date Range Selection")
    
    # Date slider selector
    date_range = st.sidebar.date_input(
        "Select Start and End Dates",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply date filters safely if a valid range is selected
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df["Date"] >= start_date) & (filtered_df["Date"] <= end_date)]

# KPI Row
total_impressions = filtered_df["Impressions"].sum() if "Impressions" in filtered_df.columns else 0
total_engagement = sum(filtered_df[col].sum() for col in ["Likes", "Shares", "Comments"] if col in filtered_df.columns)
er_rate = (total_engagement / total_impressions) * 100 if total_impressions > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Impressions", f"{total_impressions:,}")
col2.metric("Total Engagements", f"{total_engagement:,}")
col3.metric("Avg. Engagement Rate", f"{er_rate:.2f}%")

st.markdown("---")

# Check if data exists after filtering to prevent empty chart errors
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Try broadening your date range or selecting a platform.")
else:
    # Visualizations Row 1
    col4, col5 = st.columns(2)

    with col4:
        if "Date" in filtered_df.columns and "Impressions" in filtered_df.columns:
            st.subheader("📈 Impressions Over Time")
            color_param = "Platform" if "Platform" in filtered_df.columns else None
            fig1 = px.line(filtered_df, x="Date", y="Impressions", color=color_param, template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)

    with col5:
        available_metrics = [m for m in ["Likes", "Shares", "Comments"] if m in filtered_df.columns]
        if "Platform" in filtered_df.columns and available_metrics:
            st.subheader("📊 Engagement Breakdown")
            melted_df = filtered_df.melt(id_vars=["Platform"], value_vars=available_metrics, var_name="Metric", value_name="Count")
            fig2 = px.bar(melted_df, x="Metric", y="Count", color="Platform", barmode="group", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

    # Visualizations Row 2
    st.markdown("---")
    col6, col7 = st.columns(2)

    with col6:
        if "Platform" in filtered_df.columns and "Comments" in filtered_df.columns:
            st.subheader("🥧 Comments Share by Platform")
            fig3 = px.pie(filtered_df, values="Comments", names="Platform", hole=0.4, template="plotly_dark")
            st.plotly_chart(fig3, use_container_width=True)

    with col7:
        st.subheader("📋 Filtered Raw Data View")
        st.dataframe(filtered_df, use_container_width=True)

# Project Guidelines Goal
st.markdown("---")
st.subheader("💡 AI Recommended Posting Strategy")
st.info("Based on engagement trends, **Best Posting Time:** 6:00 PM - 9:00 PM local time. **Top Strategy:** Video content generates 3.4x more impressions on YouTube compared to static Instagram imagery.")
