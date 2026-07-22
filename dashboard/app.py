import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Industrial Process Monitoring Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto refresh every second
st_autorefresh(
    interval=1000,
    key="dashboard_refresh"
)

# Dashboard Title
st.title("🏭 Industrial Process Monitoring Dashboard")

st.caption(
    "Real-time Industrial Process Monitoring using "
    "Python • Modbus TCP • SQLite • Streamlit"
)

st.divider()









# =====================================================
# DATABASE FUNCTIONS
# =====================================================

# Path to the SQLite historian database
DB_PATH = Path(__file__).parent.parent / "database" / "process_data.db"


@st.cache_data(ttl=1)
def load_data():
    """
    Load the most recent 100 records from the historian.
    The data is refreshed every second.
    """

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT *
        FROM modbus_data
        ORDER BY timestamp DESC
        LIMIT 100
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_latest_record(df):
    """
    Return the newest process record.
    """

    return df.iloc[-1]











# =====================================================
# LOAD HISTORIAN DATA
# =====================================================

# Load the latest historian records
df = load_data()

# Stop the dashboard if the database is empty
if df.empty:
    st.warning("⚠️ No process data available.")
    st.stop()

# Convert timestamp column to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort records so charts display from oldest → newest
df = df.sort_values("timestamp")

# Get the latest process values
latest = get_latest_record(df)

# Previous process values (for KPI delta)
if len(df) > 1:
    previous = df.iloc[-2]
else:
    previous = latest







# =====================================================
# PROCESS STATUS & ALARM LOGIC
# =====================================================

# -----------------------------
# PLC Connection Status
# -----------------------------

plc_status = "🟢 Connected"

# -----------------------------
# Process State
# -----------------------------

if latest["motor_speed"] > 0:
    process_state = "🟢 FILLING"
else:
    process_state = "🟠 DRAINING"

# -----------------------------
# Alarm Logic
# -----------------------------

high_level_alarm = latest["tank_level"] >= 90
high_temperature_alarm = latest["temperature"] >= 35

# -----------------------------
# Alarm Messages
# -----------------------------

if high_level_alarm:
    level_alarm_text = "🔴 HIGH TANK LEVEL"
else:
    level_alarm_text = "🟢 Tank Level Normal"

if high_temperature_alarm:
    temperature_alarm_text = "🔴 HIGH TEMPERATURE"
else:
    temperature_alarm_text = "🟢 Temperature Normal"

# -----------------------------
# Motor Status
# -----------------------------

if latest["motor_speed"] > 0:
    motor_status = "🟢 RUNNING"
else:
    motor_status = "⚪ STOPPED"

# -----------------------------
# KPI Deltas
# -----------------------------

tank_delta = latest["tank_level"] - previous["tank_level"]
temperature_delta = latest["temperature"] - previous["temperature"]
pressure_delta = latest["pressure"] - previous["pressure"]
flow_delta = latest["flow_rate"] - previous["flow_rate"]
motor_delta = latest["motor_speed"] - previous["motor_speed"]








# =====================================================
# DASHBOARD STATUS
# =====================================================

status_col1, status_col2 = st.columns(2)

with status_col1:
    st.success(f"PLC Status: {plc_status}")

with status_col2:
    if "FILLING" in process_state:
        st.success(f"Process State: {process_state}")
    else:
        st.warning(f"Process State: {process_state}")

st.divider()

# =====================================================
# LIVE PROCESS VALUES
# =====================================================

st.subheader("📊 Live Process Values")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    label="Tank Level",
    value=f"{latest['tank_level']} %",
    delta=f"{tank_delta:+} %"
)

col2.metric(
    label="Temperature",
    value=f"{latest['temperature']} °C",
    delta=f"{temperature_delta:+} °C"
)

col3.metric(
    label="Pressure",
    value=f"{latest['pressure']:.1f} bar",
    delta=f"{pressure_delta:+.1f} bar"
)

col4.metric(
    label="Flow Rate",
    value=f"{latest['flow_rate']} L/min",
    delta=f"{flow_delta:+} L/min"
)

col5.metric(
    label="Motor Speed",
    value=f"{latest['motor_speed']} RPM",
    delta=f"{motor_delta:+} RPM"
)

st.divider()

# =====================================================
# ALARM STATUS
# =====================================================

st.subheader("🚨 Alarm Status")

alarm_col1, alarm_col2, alarm_col3 = st.columns(3)

with alarm_col1:
    if high_level_alarm:
        st.error(level_alarm_text)
    else:
        st.success(level_alarm_text)

with alarm_col2:
    if high_temperature_alarm:
        st.error(temperature_alarm_text)
    else:
        st.success(temperature_alarm_text)

with alarm_col3:
    if latest["motor_speed"] > 0:
        st.success(motor_status)
    else:
        st.info(motor_status)

st.divider()













# =====================================================
# LIVE PROCESS TRENDS
# =====================================================

st.subheader("📈 Live Process Trends")

chart_col1, chart_col2 = st.columns(2)

# -----------------------------------------------------
# Tank Level Trend
# -----------------------------------------------------

with chart_col1:

    fig_tank = px.line(
        df,
        x="timestamp",
        y="tank_level",
        title="Tank Level",
        markers=True
    )

    fig_tank.update_layout(
        xaxis_title="Time",
        yaxis_title="Level (%)",
        height=350
    )

    st.plotly_chart(
        fig_tank,
        use_container_width=True
    )

# -----------------------------------------------------
# Temperature Trend
# -----------------------------------------------------

with chart_col2:

    fig_temp = px.line(
        df,
        x="timestamp",
        y="temperature",
        title="Temperature",
        markers=True
    )

    fig_temp.update_layout(
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        height=350
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )

st.divider()

# -----------------------------------------------------
# Pressure Trend
# -----------------------------------------------------

fig_pressure = px.line(
    df,
    x="timestamp",
    y="pressure",
    title="Pressure Trend",
    markers=True
)

fig_pressure.update_layout(
    xaxis_title="Time",
    yaxis_title="Pressure (bar)",
    height=350
)

st.plotly_chart(
    fig_pressure,
    use_container_width=True
)

st.divider()
























# =====================================================
# RECENT HISTORIAN DATA
# =====================================================

st.subheader("📋 Recent Historian Data")

history_df = (
    df.sort_values("timestamp", ascending=False)
      .head(10)
      .reset_index(drop=True)
)

st.dataframe(
    history_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# =====================================================
# EXPORT HISTORIAN DATA
# =====================================================

st.subheader("💾 Export Historian Data")

csv = history_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Recent Historian Data (CSV)",
    data=csv,
    file_name="historian_data.csv",
    mime="text/csv"
)