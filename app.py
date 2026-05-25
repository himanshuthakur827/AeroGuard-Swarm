%%writefile app.py
import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import time

# --- 1. SUPABASE CONNECTION ---
SUPABASE_URL = "https://cuvuetjghxhtrgevwacx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1dnVldGpnaHhodHJnZXZ3YWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk3MjAxNjksImV4cCI6MjA5NTI5NjE2OX0.tz7fhluw_6D2oHAlFi3ZpZG6TC_hteE-O7GPkuc5LME"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="AeroGuard Wildfire Swarm Dashboard", layout="wide")
st.title("🌲 AeroGuard Swarm - Live Wildfire Monitoring System")

# Placeholder for UI refresh loop
placeholder = st.empty()

while True:
    with placeholder.container():
        # --- 3. FETCH DATA FROM SUPABASE ---
        try:
            # Fetch latest telemetry data
            telemetry_res = supabase.table("drone_telemetry").select("*").order("created_at", desc=True).limit(50).execute()
            # Fetch latest emergency alerts
            alerts_res = supabase.table("wildfire_alerts").select("*").order("alert_timestamp", desc=True).limit(5).execute()

            df_telemetry = pd.DataFrame(telemetry_res.data)
            df_alerts = pd.DataFrame(alerts_res.data)
        except Exception as e:
            st.error(f"Could not connect to database: {e}")
            time.sleep(3)
            continue

        # --- 4. EMERGENCY ALERT ZONE ---
        if not df_alerts.empty:
            st.error(f"⚠️ CRITICAL ALERT: {df_alerts.iloc[0]['device_id']} detected FIRE! Peak Temp: {df_alerts.iloc[0]['peak_temperature']}°C")
        else:
            st.success("✅ All drones are secure. No fire detected.")

        # --- 5. LIVE MAP VISUALIZATION ---
        st.subheader("📍 Drones Live GPS Tracking Map")
        if not df_telemetry.empty:
            # Extract latest data per drone for map display
            latest_drones = df_telemetry.sort_values('created_at').groupby('drone_id').last().reset_index()

            fig = px.scatter_mapbox(
                latest_drones,
                lat="latitude",
                lon="longitude",
                hover_name="drone_id",
                hover_data=["temperature", "battery_level", "current_mode"],
                color="temperature",
                color_continuous_scale="Inferno",
                size=[15]*len(latest_drones),
                zoom=12,
                height=500
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True, key="wildfire_map_viz")

        # --- 6. DRONE HEALTH METRICS ---
        st.subheader("📊 Swarm Health Metrics")
        if not df_telemetry.empty:
            cols = st.columns(len(latest_drones))
            for i, row in enumerate(latest_drones.itertuples()):
                with cols[i]:
                    st.metric(
                        label=f"🤖 {row.drone_id}",
                        value=f"{row.temperature}°C",
                        delta=f"🔋 {row.battery_level}% Battery"
                    )
                    st.caption(f"Status: {row.current_mode}")

        # 3 second refresh delay
        time.sleep(3)
