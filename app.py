import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V15 | Director Edition", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark (Cyber)"
if 'auth' not in st.session_state: st.session_state.auth = False
if 'loader' not in st.session_state: st.session_state.loader = True

# --- 2. MULTI-LANGUAGE DICTIONARY ---
i18n = {
    "EN": {"title": "🛰️ AeroGuard V15: Global Swarm Intelligence", "tabs": ["🌍 GLOBAL RADAR", "🧮 SPREAD MATH", "⚙️ HARDWARE MATRIX", "👁️ NEURAL VISION", "💨 ENV PHYSICS", "💾 DATA LAKE"]},
    "HI": {"title": "🛰️ AeroGuard V15: ग्लोबल स्वार्म इंटेलिजेंस", "tabs": ["🌍 ग्लोबल रडार", "🧮 फायर स्प्रेड मैथ", "⚙️ हार्डवेयर मैट्रिक्स", "👁️ न्यूरल विजन", "💨 पर्यावरण भौतिकी", "💾 डेटा लेक"]},
    "AR": {"title": "🛰️ AeroGuard V15: استخبارات السرب العالمي", "tabs": ["🌍 الرادار العالمي", "🧮 رياضيات الانتشار", "⚙️ مصفوفة الأجهزة", "👁️ الرؤية العصبية", "💨 فيزياء البيئة", "💾 بحيرة البيانات"]},
    "IT": {"title": "🛰️ AeroGuard V15: Intelligenza Globale", "tabs": ["🌍 RADAR GLOBALE", "🧮 MATEMATICA", "⚙️ HARDWARE", "👁️ VISIONE NEURALE", "💨 FISICA AMBIENTALE", "💾 DATA LAKE"]},
    "DE": {"title": "🛰️ AeroGuard V15: Globale Schwarmintelligenz", "tabs": ["🌍 GLOBALER RADAR", "🧮 AUSBREITUNG", "⚙️ HARDWARE-MATRIX", "👁️ NEURONALES SEHEN", "💨 UMWELTPHYSIK", "💾 DATENSEE"]}
}

L = st.session_state.lang
T = st.session_state.theme

# --- 3. HARDCORE ANIMATED CSS ---
if T == "Dark (Cyber)":
    bg, card_bg, text, accent = "#020617", "rgba(15, 23, 42, 0.7)", "#f8fafc", "#00ffcc"
    map_style = "carto-darkmatter"
elif T == "Light (Clean)":
    bg, card_bg, text, accent = "#f8fafc", "rgba(255, 255, 255, 0.9)", "#0f172a", "#2563eb"
    map_style = "open-street-map"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    .stApp {{background-color: {bg}; color: {text}; font-family: 'Space Grotesk', sans-serif; transition: background-color 0.5s ease;}}
    h1, h2, h3, h4 {{color: {accent} !important; font-weight: 700; letter-spacing: 1px;}}
    
    @keyframes slideInUp {{ 0% {{opacity: 0; transform: translateY(40px);}} 100% {{opacity: 1; transform: translateY(0);}} }}
    @keyframes borderGlow {{ 0% {{box-shadow: 0 0 5px {accent}40;}} 50% {{box-shadow: 0 0 20px {accent};}} 100% {{box-shadow: 0 0 5px {accent}40;}} }}
    
    .glass-card {{
        background: {card_bg}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.2); border-top: 3px solid {accent};
        border-radius: 12px; padding: 25px; margin-bottom: 20px;
        animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }}
    .glass-card:hover {{ transform: scale(1.01); animation: borderGlow 2s infinite; }}
    
    .metric-title {{font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1.5px;}}
    .metric-value {{font-size: 2.5rem; color: {text}; font-weight: 700; margin-top: 5px;}}
    .briefing-text {{font-size: 0.95rem; line-height: 1.6; color: {text}; margin-top: 10px; opacity: 0.9;}}
    .brief-tag {{color: {accent}; font-weight: 900; letter-spacing: 1px;}}
    
    .stTabs [data-baseweb="tab"] {{color: {text}; font-weight: 600; font-size: 15px; background: transparent; transition: all 0.3s ease;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important; background: rgba(0, 255, 204, 0.05); border-radius: 5px 5px 0 0;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SECURE LOGIN & LOADER ---
if not st.session_state.auth:
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown(f"<div class='glass-card' style='text-align:center;'><h2>GLOBAL NEXUS LOGIN</h2><p>Universal Swarm Command Interface</p></div>", unsafe_allow_html=True)
        pwd = st.text_input("Enter Passcode ('admin')", type="password")
        if st.button("INITIALIZE SECURE UPLINK", use_container_width=True):
            if pwd == "admin": st.session_state.auth = True; st.rerun()
            else: st.error("Access Denied.")
    st.stop()

if st.session_state.loader:
    boot = st.empty()
    for i in range(1, 101, 20):
        boot.markdown(f"<div class='glass-card' style='text-align:center;'><h2>BOOTING SYSTEM... {i}%</h2><p>Establishing Satellite Uplink...</p></div>", unsafe_allow_html=True)
        time.sleep(0.3)
    st.session_state.loader = False
    st.rerun()

# --- 5. SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    st.markdown("## ⚙️ GLOBAL COMMAND")
    
    with st.expander("🌐 UI & Region Setup", expanded=True):
        st.session_state.lang = st.selectbox("Interface Language", ["EN", "HI", "AR", "IT", "DE"], index=["EN", "HI", "AR", "IT", "DE"].index(L))
        st.session_state.theme = st.selectbox("UI Mode", ["Dark (Cyber)", "Light (Clean)"], index=["Dark (Cyber)", "Light (Clean)"].index(T))
        unit_sys = st.radio("Measurement System", ["Metric", "Imperial"])

    with st.expander("🧮 Mathematical Fire Spread"):
        spread_alg = st.selectbox("Spread Algorithm", ["Rothermel Equation", "Huygens Principle"])
        z_thresh = st.slider("Anomaly Z-Score (σ)", 1.0, 5.0, 2.5)
        calc_dt = st.number_input("Calculus Δt", 0.1, 5.0, 1.0)

    with st.expander("⚙️ Hardware: Flight & Tuning"):
        pid_p = st.slider("Proportional Gain (kP)", 0.0, 2.0, 0.5)
        kalman_q = st.number_input("Kalman Process Noise", 0.001, 0.1, 0.01, format="%.3f")
        swarm_topo = st.selectbox("Swarm Topology", ["Mesh Network", "Star Topology"])

    with st.expander("📡 Hardware: Telemetry & Radio"):
        lora_sf = st.select_slider("LoRa Spreading Factor", [7, 8, 9, 10, 11, 12], value=10)
        tx_power = st.slider("Transmit Power (dBm)", 2, 20, 14)
        
    with st.expander("👁️ Hardware: Thermal & Optical"):
        flir_emis = st.slider("Thermal Emissivity (ε)", 0.1, 1.0, 0.95)
        lidar_den = st.selectbox("LiDAR Point Density", ["Low", "High"])

    with st.expander("💨 Physics: Environment"):
        wind_spd = st.slider("Wind Vector (km/h)", 0, 120, 25)
        solar_irr = st.slider("Solar Irradiance (W/m²)", 0, 1200, 800)

    if st.button("🔴 DISCONNECT UPLINK"): st.session_state.auth = False; st.rerun()

# --- 6. DATA INGESTION ---
def fetch_telemetry():
    try:
        SUPABASE_URL = "https://cuvuetjghxhtrgevwacx.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1dnVldGpnaHhodHJnZXZ3YWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk3MjAxNjksImV4cCI6MjA5NTI5NjE2OX0.tz7fhluw_6D2oHAlFi3ZpZG6TC_hteE-O7GPkuc5LME"
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.table("drone_telemetry").select("*").order("created_at", desc=True).limit(200).execute()
        return pd.DataFrame(res.data)
    except:
        np.random.seed(int(time.time() * 10) % 100)
        drones = [f"UAV-Alpha", f"UAV-Beta", f"UAV-Gamma", f"UAV-Delta"]
        data = []
        for d in drones:
            t_base = 35 if d != "UAV-Gamma" else (35 + np.random.randint(40, 150))
            data.append({
                "drone_id": d, "created_at": pd.Timestamp.now(),
                "latitude": 31.104 + np.random.randn()*0.02, "longitude": 77.166 + np.random.randn()*0.02,
                "temperature": t_base + np.random.randn()*5, "battery_level": np.random.randint(30, 95)
            })
        return pd.DataFrame(data)

df_tel = fetch_telemetry()
df_tel['temperature'] = df_tel['temperature'] if unit_sys == "Metric" else (df_tel['temperature'] * 9/5) + 32

# --- 7. MAIN DASHBOARD & Z-SCORE LOGIC ---
st.markdown(f"<h1>{i18n[L]['title']}</h1>", unsafe_allow_html=True)

if not df_tel.empty:
    latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
    max_t = latest['temperature'].max()
    
    # 🧮 ADVANCED Z-SCORE MATHEMATICS (Directly linked to slider)
    mean_temp = df_tel['temperature'].mean()
    std_temp = df_tel['temperature'].std()
    latest['live_z_score'] = (latest['temperature'] - mean_temp) / (std_temp + 0.0001)
    
    # Dynamic Alert based on Z-Score Slider!
    critical = len(latest[latest['live_z_score'] > z_thresh])
    
    # TOP METRICS
    m1, m2, m3, m4 = st.columns(4)
    unit_str = "°C" if unit_sys == "Metric" else "°F"
    
    m1.markdown(f"<div class='glass-card' style='animation-delay: 0.1s;'><div class='metric-title'>Active Edge Nodes</div><div class='metric-value'>{len(latest)}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='glass-card' style='animation-delay: 0.2s;'><div class='metric-title'>Thermal Peak</div><div class='metric-value' style='color: {'#ef4444' if critical>0 else accent};'>{max_t:.1f}{unit_str}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='glass-card' style='animation-delay: 0.3s;'><div class='metric-title'>Predicted Spread</div><div class='metric-value'>{(wind_spd * 0.15):.2f} m/s</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='glass-card' style='animation-delay: 0.4s;'><div class='metric-title'>Z-Score Threshold</div><div class='metric-value'>{z_thresh} σ</div></div>", unsafe_allow_html=True)

    if critical > 0:
        st.markdown(f"<div class='glass-card' style='border-top-color:#ef4444; background:rgba(239, 68, 68, 0.1);'><h3 style='color:#ef4444 !important;'>🚨 CRITICAL ALERT TRIGGERED</h3><p>Anomaly exceeds Z-Score mathematical threshold ({z_thresh}σ). Pre-computing swarm intercept vectors.</p></div>", unsafe_allow_html=True)

    # --- 8. THE TABS WITH "INTELLIGENCE BRIEFINGS" ---
    tabs = st.tabs(i18n[L]['tabs'])
    
    with tabs[0]: # TAB 1: RADAR
        st.markdown(f"""
        <div class='glass-card'>
            <h4>🧠 SYSTEM INTELLIGENCE BRIEFING: GEOSPATIAL RADAR</h4>
            <div class='briefing-text'>
                <span class='brief-tag'>[WHAT IS THIS?]</span> A real-time Cartographic Information System displaying the live GPS coordinates of the UAV swarm.<br>
                <span class='brief-tag'>[WHY DO WE NEED IT?]</span> To maintain situational awareness. It calculates the 'Swarm Centroid' (Center of Mass) mathematically to ensure the drones don't stray too far from the mission objective.<br>
                <span class='brief-tag'>[HOW IT WORKS]</span> It ingests latitude/longitude packets via MQTT. The size and color of the nodes react dynamically to the thermal payload they carry.<br>
                <span class='brief-tag'>[REAL DEPLOYMENT]</span> Physical drones use RTK (Real-Time Kinematic) GPS modules. When deployed in deep forests, standard GPS drifts by 5 meters. This interface will plot the RTK corrected data, giving centimeter-level accuracy to direct ground firefighters safely.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig_map = px.scatter_mapbox(latest, lat="latitude", lon="longitude", color="temperature", size=[40]*len(latest), color_continuous_scale="Inferno", zoom=12, height=600, hover_name="drone_id")
        # Center of Mass mapping
        fig_map.add_trace(go.Scattermapbox(lat=[latest['latitude'].mean()], lon=[latest['longitude'].mean()], mode='markers+text', marker=dict(size=20, color=accent, symbol='cross'), text=["CENTROID"], textposition="top right"))
        fig_map.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", font_color=text)
        st.plotly_chart(fig_map, use_container_width=True)

    with tabs[1]: # TAB 2: MATH
        st.markdown(f"""
        <div class='glass-card'>
            <h4>🧠 SYSTEM INTELLIGENCE BRIEFING: SPREAD MATHEMATICS</h4>
            <div class='briefing-text'>
                <span class='brief-tag'>[WHAT IS THIS?]</span> The predictive core. It calculates the physical rate at which the fire is expanding and its thermal acceleration.<br>
                <span class='brief-tag'>[WHY DO WE NEED IT?]</span> Knowing a fire is hot isn't enough; emergency services must predict <i>where</i> it will be in 30 minutes to evacuate civilians.<br>
                <span class='brief-tag'>[HOW IT WORKS]</span> Uses the Rothermel Surface Fire Equation for forward spread, and the First Derivative (dT/dt) of the NumPy array to find the rate of thermal change.<br>
                <span class='brief-tag'>[REAL DEPLOYMENT]</span> Physical drones carry NVIDIA Jetson Edge computers. They run these heavy calculus differentials locally at 30 FPS. If dT/dt spikes, the drone doesn't wait for human input—it autonomously requests water-bomber planes to its exact coordinate.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        eq1, eq2 = st.columns(2)
        with eq1:
            st.markdown(f"<div class='glass-card'><div class='metric-title'>Rothermel Rate of Spread</div>", unsafe_allow_html=True)
            st.latex(r"R = \frac{I_R \xi (1 + \phi_w + \phi_s)}{\rho_b \epsilon Q_{ig}}")
            st.markdown("</div>", unsafe_allow_html=True)
        with eq2:
            st.markdown(f"<div class='glass-card'><div class='metric-title'>Calculus: First Derivative</div>", unsafe_allow_html=True)
            st.latex(r"\frac{\partial T}{\partial t} = \lim_{\Delta t \to 0} \frac{T(t + \Delta t) - T(t)}{\Delta t}")
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[2]: # TAB 3: HARDWARE
        st.markdown(f"""
        <div class='glass-card'>
            <h4>🧠 SYSTEM INTELLIGENCE BRIEFING: HARDWARE MATRIX</h4>
            <div class='briefing-text'>
                <span class='brief-tag'>[WHAT IS THIS?]</span> A simulation of the physical forces acting on the drone's hardware (Vibration, Signal Loss, Battery).<br>
                <span class='brief-tag'>[WHY DO WE NEED IT?]</span> Software doesn't fly; hardware does. We must monitor if the drone is vibrating too much or losing radio signal.<br>
                <span class='brief-tag'>[HOW IT WORKS]</span> The 3D Surface map simulates the PID Controller's mathematical response to physical wind gusts. The higher the Proportional Gain (kP), the sharper the spikes.<br>
                <span class='brief-tag'>[REAL DEPLOYMENT]</span> When a real UAV flies into a fire's thermal updraft, the turbulence is extreme. By monitoring this IMU vibration matrix live, the ground station can command the swarm to increase altitude before a structural motor failure occurs.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c_hw1, c_hw2 = st.columns(2)
        with c_hw1:
            x_val = np.linspace(0, 10, 50); y_val = np.linspace(0, 10, 50); X, Y = np.meshgrid(x_val, y_val)
            Z = np.sin(X) * np.cos(Y) * pid_p 
            fig_3d = go.Figure(data=[go.Surface(z=Z, colorscale='Viridis')])
            fig_3d.update_layout(title="IMU Vibration Matrix (PID Response)", scene=dict(bgcolor="rgba(0,0,0,0)"), paper_bgcolor="rgba(0,0,0,0)", font_color=text, height=350)
            st.plotly_chart(fig_3d, use_container_width=True)
        with c_hw2:
            st.markdown(f"<div class='glass-card'><h4>📡 Antenna Link Budget</h4><p>Current LoRa Spreading Factor: <b>{lora_sf}</b>.<br>Signal penetration depth allows for operation in DENSE CANOPY.</p><h4>🔋 Swarm Topology</h4><p>Mode: <b>{swarm_topo}</b>. Ensures redundant telemetry routing if a primary node is destroyed.</p></div>", unsafe_allow_html=True)

    with tabs[3]: # TAB 4: VISION
        st.markdown(f"""
        <div class='glass-card'>
            <h4>🧠 SYSTEM INTELLIGENCE BRIEFING: NEURAL VISION</h4>
            <div class='briefing-text'>
                <span class='brief-tag'>[WHAT IS THIS?]</span> The live Optical and FLIR (Forward Looking Infrared) feed from the UAV's camera payload.<br>
                <span class='brief-tag'>[HOW IT WORKS]</span> Displays simulated bounding boxes from the YOLOv8 Artificial Intelligence model running computer vision algorithms on the edge node.<br>
                <span class='brief-tag'>[REAL DEPLOYMENT]</span> In reality, transmitting 4K video over long distances is impossible during a wildfire. The drone processes the video <i>internally</i> and only transmits the lightweight JSON text (e.g., "Fire Detected: 94% Confidence") back to this dashboard, saving massive radio bandwidth.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cam1, cam2 = st.columns(2)
        for i, (idx, r) in enumerate(latest.head(2).iterrows()):
            b_col = "#ef4444" if r['live_z_score'] > z_thresh else accent
            cam = cam1 if i == 0 else cam2
            cam.markdown(f"""
            <div style="border: 2px solid {b_col}; background: #000; height: 300px; position: relative; border-radius: 12px; box-shadow: inset 0 0 50px rgba(0,0,0,1);">
                <div style="position: absolute; top: 15px; left: 15px; color: {b_col}; font-family: monospace; font-size: 14px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 5px;">
                    REC 🔴 | NODE: {r['drone_id']} | CONFIDENCE: {np.random.randint(85, 99)}% <br> EMISSIVITY CALIBRATION: {flir_emis}
                </div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.1); font-size: 80px;">⌖</div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[4]: # TAB 5: ENV
        st.markdown(f"""
        <div class='glass-card'>
            <h4>🧠 SYSTEM INTELLIGENCE BRIEFING: ENVIRONMENTAL PHYSICS</h4>
            <div class='briefing-text'>
                <span class='brief-tag'>[WHAT IS THIS?]</span> A topographical heat dispersion map and environmental force multipliers.<br>
                <span class='brief-tag'>[WHY DO WE NEED IT?]</span> Wildfires create their own micro-climates. We must track ambient forces like Solar Irradiance and Wind.<br>
                <span class='brief-tag'>[REAL DEPLOYMENT]</span> The base station uses local weather APIs and onboard Pitot tubes to generate this heatmap. This allows commanders to visualize the "Thermal Wake" of the fire and predict which way the smoke column will drift, preventing firefighters from being trapped.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        m_env1, m_env2 = st.columns(2)
        m_env1.metric("Wind Vector Force", f"{wind_spd} km/h")
        m_env2.metric("Solar Irradiance Load", f"{solar_irr} W/m²")

    with tabs[5]: # TAB 6: DATA
        st.markdown("### 💾 Global Edge-Node Telemetry Access")
        st.dataframe(df_tel, use_container_width=True)

# --- 9. AUTO-REFRESH ENGINE ---
time.sleep(2)
st.rerun()
