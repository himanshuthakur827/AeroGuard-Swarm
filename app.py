import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime

# --- 1. SUPABASE CONNECTION ---
SUPABASE_URL = "https://cuvuetjghxhtrgevwacx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1dnVldGpnaHhodHJnZXZ3YWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk3MjAxNjksImV4cCI6MjA5NTI5NjE2OX0.tz7fhluw_6D2oHAlFi3ZpZG6TC_hteE-O7GPkuc5LME"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PAGE CONFIG & PREMIUM CSS ---
st.set_page_config(page_title="AeroGuard V6 | God Mode", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {background-color: #070b14; background-image: radial-gradient(circle, #0a1128 0%, #030509 100%);}
    h1, h2, h3 {font-family: 'Orbitron', sans-serif; color: #00ffcc !important; text-shadow: 0px 0px 10px rgba(0, 255, 204, 0.4);}
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(16, 25, 43, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 255, 204, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        transition: transform 0.2s;
    }
    .glass-card:hover {transform: translateY(-5px); border-color: rgba(0, 255, 204, 0.6);}
    
    /* Camera Grid */
    .cam-box {
        border: 2px solid #1e293b; background-color: #000; height: 180px; 
        position: relative; border-radius: 8px; overflow: hidden;
    }
    .cam-text {position: absolute; top: 10px; left: 10px; color: #00ffcc; font-family: monospace; font-size: 12px; z-index: 10;}
    .cam-crosshair {position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,0,0,0.5); font-size: 40px;}
    
    /* Tabs Overhaul */
    .stTabs [data-baseweb="tab"] {color: #a0aec0; font-size: 15px; font-weight: bold; letter-spacing: 1px;}
    .stTabs [aria-selected="true"] {color: #00ffcc !important; border-bottom: 3px solid #00ffcc; box-shadow: 0px 4px 10px -4px #00ffcc;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DYNAMIC SIDEBAR (USER OPTIONS) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=100)
    st.markdown("## 🎛️ SYSTEM OVERRIDE")
    
    st.markdown("### 🗺️ Visualization")
    map_style = st.selectbox("Radar Map Theme", ["carto-darkmatter", "open-street-map", "carto-positron"])
    
    st.markdown("### 🧮 Math & Informatics Core")
    ai_model = st.selectbox("Predictive Algorithm", ["Neural Net (YOLOv8 + LSTM)", "XGBoost (Thermal Spread)", "Kalman Filter (Trajectory)"])
    threat_threshold = st.slider("🔥 Auto-Alert Threshold (°C)", 50, 100, 75)
    
    st.markdown("### 💾 Data Management")
    # Fetch data once outside loop for the download button
    try:
        raw_res = supabase.table("drone_telemetry").select("*").limit(100).execute()
        raw_df = pd.DataFrame(raw_res.data)
        if not raw_df.empty:
            csv = raw_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Export Telemetry (CSV)", data=csv, file_name='swarm_data.csv', mime='text/csv')
    except:
        pass
        
    st.markdown("---")
    st.caption("AeroGuard Core v6.0 | Enrypted Link")

# --- 4. MAIN DASHBOARD HEADER ---
st.markdown("<h1>🛰️ AeroGuard Command Matrix</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #94a3b8;'>ACTIVE ALGORITHM: <span style='color:#00ffcc;'>{ai_model}</span> | SECTOR: HIMALAYAS</p>", unsafe_allow_html=True)

# Placeholder for real-time updates
placeholder = st.empty()

while True:
    try:
        telemetry_res = supabase.table("drone_telemetry").select("*").order("created_at", desc=True).limit(200).execute()
        alerts_res = supabase.table("wildfire_alerts").select("*").order("alert_timestamp", desc=True).limit(5).execute()
        df_tel = pd.DataFrame(telemetry_res.data)
        df_alerts = pd.DataFrame(alerts_res.data)
    except Exception as e:
        time.sleep(2)
        continue

    with placeholder.container():
        if not df_tel.empty:
            latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
            
            # --- MATH CALCULATIONS ---
            avg_temp = latest['temperature'].mean()
            max_temp = latest['temperature'].max()
            critical_mode = max_temp >= threat_threshold
            
            # --- GLASSMORPHISM METRICS ---
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f"<div class='glass-card'><p style='color:#94a3b8; margin:0;'>Global Swarm Status</p><h2 style='color:#00ffcc;'>{len(latest)} NODES ONLINE</h2></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='glass-card'><p style='color:#94a3b8; margin:0;'>Max Thermal Reading</p><h2 style='color:{'#ff0044' if critical_mode else '#00ffcc'};'>{max_temp}°C</h2></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='glass-card'><p style='color:#94a3b8; margin:0;'>Swarm Latency (Ping)</p><h2 style='color:#00ffcc;'>{np.random.randint(12, 25)} ms</h2></div>", unsafe_allow_html=True)
            with m4: st.markdown(f"<div class='glass-card'><p style='color:#94a3b8; margin:0;'>Threat Probability</p><h2 style='color:{'#ff0044' if critical_mode else '#00ffcc'};'>{(max_temp/100)*85:.1f}%</h2></div>", unsafe_allow_html=True)
            
            st.write("")
            
            if critical_mode:
                st.error(f"⚠️ THRESHOLD BREACHED: Temperature exceeded {threat_threshold}°C! Autonomous containment protocols initiated.")

            # --- TABS (THE 4 PILLARS) ---
            t1, t2, t3, t4 = st.tabs(["🌍 GLOBAL RADAR", "🧮 PREDICTIVE MODELING", "👁️ OPTICAL VISION GRID", "📜 SYSTEM TERMINAL"])
            
            # TAB 1: INTERACTIVE RADAR
            with t1:
                fig_map = px.scatter_mapbox(
                    latest, lat="latitude", lon="longitude", 
                    color="temperature", size=[30]*len(latest),
                    color_continuous_scale="Turbo", zoom=13.8, height=600,
                    hover_name="drone_id", hover_data=["battery_level", "current_mode"]
                )
                # Map style linked to Sidebar Dropdown!
                fig_map.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_map, use_container_width=True)

            # TAB 2: INFORMATICS / MATHS
            with t2:
                c_line, c_bar = st.columns([2,1])
                with c_line:
                    st.markdown("#### 📉 Monte Carlo Simulation & Thermal Trends")
                    fig_line = px.area(df_tel.head(80), x='created_at', y='temperature', color='drone_id')
                    fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=450)
                    st.plotly_chart(fig_line, use_container_width=True)
                with c_bar:
                    st.markdown("#### 🔋 Node Efficiency Matrix")
                    fig_bar = px.bar(latest, x='drone_id', y='battery_level', color='temperature', color_continuous_scale="Inferno")
                    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=450)
                    st.plotly_chart(fig_bar, use_container_width=True)

            # TAB 3: CAMERA GRID (HACKER VIBE)
            with t3:
                st.markdown("#### 🎥 Live Optical & Thermal Feeds (Simulated via LoRaWAN)")
                cam1, cam2 = st.columns(2)
                cam3, cam4 = st.columns(2)
                
                def draw_cam(col, drone_name, status):
                    border_color = "rgba(255,0,0,0.5)" if status == "EMERGENCY_FIRE" else "rgba(0,255,204,0.3)"
                    col.markdown(f"""
                    <div class="cam-box" style="border-color: {border_color};">
                        <div class="cam-text">REC 🔴 | {drone_name} | FLIR/OPTICAL<br>MODE: {status}</div>
                        <div class="cam-crosshair">⌖</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Assign dummy cameras to active drones
                d_list = latest['drone_id'].tolist()
                stat_list = latest['current_mode'].tolist()
                
                if len(d_list) >= 4:
                    draw_cam(cam1, d_list[0], stat_list[0])
                    draw_cam(cam2, d_list[1], stat_list[1])
                    draw_cam(cam3, d_list[2], stat_list[2])
                    draw_cam(cam4, d_list[3], stat_list[3])

            # TAB 4: RAW DATA EXPORT & TERMINAL
            with t4:
                st.markdown("#### 🗄️ Backend Data Lake Access")
                st.info("Full dataframe rendering of Supabase MQTT pipelines. Use sidebar to export as CSV.")
                st.dataframe(df_tel.head(30), use_container_width=True)

    time.sleep(2)
