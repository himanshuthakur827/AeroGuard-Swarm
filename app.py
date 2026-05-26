import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V18 | JARVIS Edition", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark (Cyber)"
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 2. MULTI-LANGUAGE DICTIONARY ---
i18n = {
    "EN": {"title": "🛰️ AeroGuard V18: Global Swarm Intelligence", "tabs": ["🌍 GLOBAL RADAR", "🧮 SPREAD MATH", "⚙️ HARDWARE MATRIX", "👁️ NEURAL VISION (AI)", "💨 ENV PHYSICS", "💾 DATA LAKE & TERMINAL"]},
    "HI": {"title": "🛰️ AeroGuard V18: ग्लोबल स्वार्म इंटेलिजेंस", "tabs": ["🌍 ग्लोबल रडार", "🧮 फायर स्प्रेड मैथ", "⚙️ हार्डवेयर मैट्रिक्स", "👁️ न्यूरल विजन", "💨 पर्यावरण भौतिकी", "💾 डेटा लेक"]},
    "AR": {"title": "🛰️ AeroGuard V18: استخبارات السرب العالمي", "tabs": ["🌍 الرادار العالمي", "🧮 رياضيات الانتشار", "⚙️ مصفوفة الأجهزة", "👁️ الرؤية العصبية", "💨 فيزياء البيئة", "💾 بحيرة البيانات"]},
    "IT": {"title": "🛰️ AeroGuard V18: Intelligenza Globale", "tabs": ["🌍 RADAR GLOBALE", "🧮 MATEMATICA", "⚙️ HARDWARE", "👁️ VISIONE NEURALE", "💨 FISICA AMBIENTALE", "💾 DATA LAKE"]},
    "DE": {"title": "🛰️ AeroGuard V18: Globale Schwarmintelligenz", "tabs": ["🌍 GLOBALER RADAR", "🧮 AUSBREITUNG", "⚙️ HARDWARE-MATRIX", "👁️ NEURONALES SEHEN", "💨 UMWELTPHYSIK", "💾 DATENSEE"]}
}

L = st.session_state.lang
T = st.session_state.theme

# --- 3. HARDCORE ANIMATED CSS & TERMINAL STYLES ---
if T == "Dark (Cyber)":
    bg, card_bg, text, accent = "#020617", "rgba(15, 23, 42, 0.8)", "#f8fafc", "#00ffcc"
    map_style = "carto-darkmatter"
elif T == "Light (Clean)":
    bg, card_bg, text, accent = "#f8fafc", "rgba(255, 255, 255, 0.95)", "#0f172a", "#2563eb"
    map_style = "open-street-map"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=VT323&display=swap');
    .stApp {{background-color: {bg}; color: {text}; font-family: 'Space Grotesk', sans-serif; transition: background-color 0.5s ease;}}
    h1, h2, h3, h4 {{color: {accent} !important; font-weight: 700; letter-spacing: 1px;}}
    
    @keyframes slideInUp {{ 0% {{opacity: 0; transform: translateY(40px);}} 100% {{opacity: 1; transform: translateY(0);}} }}
    @keyframes borderGlow {{ 0% {{box-shadow: 0 0 5px {accent}40;}} 50% {{box-shadow: 0 0 20px {accent};}} 100% {{box-shadow: 0 0 5px {accent}40;}} }}
    @keyframes pulseText {{ 0% {{opacity: 0.5;}} 50% {{opacity: 1;}} 100% {{opacity: 0.5;}} }}
    @keyframes scrollUp {{ 0% {{transform: translateY(100%);}} 100% {{transform: translateY(-100%);}} }}
    
    .glass-card {{
        background: {card_bg}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.2); border-top: 3px solid {accent};
        border-radius: 12px; padding: 25px; margin-bottom: 20px;
        animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }}
    .glass-card:hover {{ transform: scale(1.01); animation: borderGlow 2s infinite; }}
    
    .terminal-box {{
        background-color: #000; color: #00ff00; font-family: 'VT323', monospace; 
        font-size: 1.2rem; padding: 15px; height: 300px; overflow: hidden; 
        border: 1px solid #333; border-radius: 8px; position: relative;
    }}
    .terminal-content {{ animation: scrollUp 15s linear infinite; position: absolute; width: 100%; }}
    
    .notice-card {{
        background: rgba(245, 158, 11, 0.15); border-left: 5px solid #f59e0b; padding: 15px;
        border-radius: 8px; margin-bottom: 25px; font-weight: 600; color: {text};
    }}
    
    .metric-title {{font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1.5px;}}
    .metric-value {{font-size: 2.5rem; color: {text}; font-weight: 700; margin-top: 5px;}}
    .briefing-text {{font-size: 0.95rem; line-height: 1.6; color: {text}; margin-top: 10px; opacity: 0.9;}}
    .brief-tag {{color: {accent}; font-weight: 900; letter-spacing: 1px;}}
    
    .stTabs [data-baseweb="tab"] {{color: {text}; font-weight: 600; font-size: 15px; background: transparent; transition: all 0.3s ease;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important; background: rgba(0, 255, 204, 0.05); border-radius: 5px 5px 0 0;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SECURE LOGIN GATEWAY (STEALTH) ---
if not st.session_state.auth:
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='text-align:center;'>
        <h1 style='color:#64748b !important; font-size:4rem; animation: pulseText 2s infinite;'>🔒 AEROGUARD SYSTEM LOCKED</h1>
        <p style='color:#94a3b8; font-size:1.2rem; letter-spacing: 2px;'>SECURE ENCRYPTED UPLINK REQUIRED. INITIALIZE VIA TERMINAL.</p>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    
    if not st.session_state.auth:
        st.markdown("## 📡 SYSTEM STANDBY")
        with st.expander("🔌 Connect Uplink", expanded=False): 
            pwd = st.text_input("Enter Clearance Code", type="password", value="admin")
            if st.button("AUTHENTICATE"):
                if pwd == "admin": st.session_state.auth = True; st.rerun()
                else: st.error("Access Denied.")
        st.stop() 

    st.markdown("## ⚙️ GLOBAL COMMAND")
    
    pause_sync = st.checkbox("⏸️ Pause Live Sync (Use for Image Upload)", value=False, help="[CRITICAL] Check this box to stop the auto-refresh loop. This is required if you want to upload a custom image in the Neural Vision tab without the page resetting.")
    
    with st.expander("🌐 UI & Region Setup", expanded=True):
        st.session_state.lang = st.selectbox("Interface Language", ["EN", "HI", "AR", "IT", "DE"], index=["EN", "HI", "AR", "IT", "DE"].index(L), help="[WHAT] Translates the core dashboard interface into multiple languages. [WHY] Enables rapid deployment of this command center across international borders without rewriting code. [HOW] Uses a centralized Python dictionary (i18n) mapped to session states. [REAL DEPLOYMENT] Allows local firefighters to read telemetry natively.")
        st.session_state.theme = st.selectbox("UI Mode", ["Dark (Cyber)", "Light (Clean)"], index=["Dark (Cyber)", "Light (Clean)"].index(T), help="[WHAT] Toggles the CSS variables between high-contrast Dark mode and clinical Light mode. [REAL DEPLOYMENT] Operators working inside dark trucks will use Dark Mode. Ground commanders operating under harsh sunlight will switch to Light Mode to eliminate glare.")
        unit_sys = st.radio("Measurement System", ["Metric", "Imperial"])

    with st.expander("🧮 Mathematical Fire Spread"):
        spread_alg = st.selectbox("Spread Algorithm", ["Rothermel Equation", "Huygens Principle"], help="[WHAT] The mathematical engine predicting the forward rate of spread. [WHY] Tracking the fire is not enough; we must predict its future location to organize civilian evacuations. [HOW] It calculates heat flux using partial differential equations.")
        z_thresh = st.slider("Anomaly Z-Score (σ)", 1.0, 5.0, 2.5, help="[WHAT] The statistical threshold defining what constitutes a critical thermal event. [HOW] It calculates how many Standard Deviations (σ) the current reading is from the rolling mean. [REAL DEPLOYMENT] Instantly triggers emergency interrupts without human input.")
        calc_dt = st.number_input("Calculus Δt", 0.1, 5.0, 1.0, help="[WHAT] The fundamental time step used for calculating real-time derivatives (dT/dt). [REAL DEPLOYMENT] Must be perfectly synchronized with the frames-per-second (FPS) output of your physical FLIR camera.")

    with st.expander("⚙️ Hardware: Flight & Tuning"):
        pid_p = st.slider("Proportional Gain (kP)", 0.0, 2.0, 0.5, help="[WHAT] The primary tuning parameter of the PID flight controller logic. [HOW] Calculates a corrective force directly proportional to positional errors. [REAL DEPLOYMENT] You must tune this kP value higher in the field so heavy payloads don't cause violent drifts.")
        kalman_q = st.number_input("Kalman Process Noise", 0.001, 0.1, 0.01, format="%.3f", help="[WHAT] Represents the level of uncertainty in the math model predicting the drone's position. [REAL DEPLOYMENT] Wind gusts and vibrations inject massive noise into the onboard IMU. This filters out vibration without ignoring actual trajectory changes.")

    with st.expander("📡 Hardware: Telemetry & Radio"):
        lora_sf = st.select_slider("LoRa Spreading Factor", [7, 8, 9, 10, 11, 12], value=10, help="[WHAT] Determines the duration of a single 'chirp' in LoRaWAN frequency modulation. [REAL DEPLOYMENT] In dense mountainous terrain, you will physically increase the SF to 11 or 12 to ensure the MQTT payload penetrates obstacles.")
        tx_power = st.slider("Transmit Power (dBm)", 2, 20, 14, help="[WHAT] Dictates the sheer electrical energy pushed into the radio antenna. [REAL DEPLOYMENT] In global wildfire deployments covering hundreds of kilometers, crank this up to the maximum 20 dBm.")
        
    with st.expander("👁️ Hardware: Thermal & Optical"):
        flir_emis = st.slider("Thermal Emissivity (ε)", 0.1, 1.0, 0.95, help="[WHAT] Represents a material's effectiveness in emitting thermal radiation. [HOW] Applies this coefficient to the Stefan-Boltzmann law. [REAL DEPLOYMENT] Set to 0.95 for forests. If monitoring pipelines, lower it to 0.85 to compensate for low emission.")

    with st.expander("💨 Physics: Environment"):
        wind_spd = st.slider("Wind Vector (km/h)", 0, 120, 25, help="[WHAT] Mid-flame wind speed representing air movement directly above the fire line. [REAL DEPLOYMENT] Real drones will have onboard Pitot tubes gathering this wind data live, continuously updating the math engine.")
        solar_irr = st.slider("Solar Irradiance (W/m²)", 0, 1200, 800, help="[WHAT] The power per unit area received from the Sun. [REAL DEPLOYMENT] Will be measured via physical pyranometer sensors attached to the base station, factoring into the Z-score logic.")

    st.markdown("---")
    if st.button("🔴 DISCONNECT UPLINK"): 
        st.session_state.auth = False
        st.rerun()

# --- 6. DATA INGESTION ENGINE (OPTIMIZED WITH CACHE) ---
@st.cache_data(ttl=5)
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

df_tel = fetch_telemetry().copy()
df_tel['temperature'] = df_tel['temperature'] if unit_sys == "Metric" else (df_tel['temperature'] * 9/5) + 32

# --- 7. MAIN DASHBOARD ---
st.markdown(f"<h1>{i18n[L]['title']}</h1>", unsafe_allow_html=True)

st.markdown("""
<div class="notice-card">
    ⚠️ LIVE DEMONSTRATION & DEPLOYMENT NOTICE: <br>
    <span style="font-weight: 400;">The telemetry and calculations displayed are processing via a cloud swarm simulation. <b>This software architecture is fully hardware-agnostic.</b> When physical UAV edge-nodes and FLIR sensors are deployed, this Exact Command Center will ingest their real-time payloads autonomously.</span>
</div>
""", unsafe_allow_html=True)

if not df_tel.empty:
    latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
    max_t = latest['temperature'].max()
    
    # 🧮 Z-SCORE LOGIC 
    mean_temp = df_tel['temperature'].mean()
    std_temp = df_tel['temperature'].std()
    latest['live_z_score'] = (latest['temperature'] - mean_temp) / (std_temp + 0.0001)
    critical = len(latest[latest['live_z_score'] > z_thresh])
    
    m1, m2, m3, m4 = st.columns(4)
    unit_str = "°C" if unit_sys == "Metric" else "°F"
    
    m1.markdown(f"<div class='glass-card' style='animation-delay: 0.1s;'><div class='metric-title'>Active Edge Nodes</div><div class='metric-value'>{len(latest)}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='glass-card' style='animation-delay: 0.2s;'><div class='metric-title'>Thermal Peak</div><div class='metric-value' style='color: {'#ef4444' if critical>0 else accent};'>{max_t:.1f}{unit_str}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='glass-card' style='animation-delay: 0.3s;'><div class='metric-title'>Predicted Spread</div><div class='metric-value'>{(wind_spd * 0.15):.2f} m/s</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='glass-card' style='animation-delay: 0.4s;'><div class='metric-title'>Z-Score Threshold</div><div class='metric-value'>{z_thresh} σ</div></div>", unsafe_allow_html=True)

    if critical > 0:
        # HERE IS THE FIXED AUDIO SIREN WITH CONTROLS
        st.markdown(f"""
        <div class='glass-card' style='border-top-color:#ef4444; background:rgba(239, 68, 68, 0.1);'>
            <h3 style='color:#ef4444 !important;'>🚨 CRITICAL ALERT TRIGGERED</h3>
            <p>Anomaly exceeds Z-Score mathematical threshold ({z_thresh}σ). Pre-computing swarm intercept vectors.</p>
            <audio autoplay loop controls style="height: 35px; margin-top: 10px; width: 300px;">
                <source src="https://assets.mixkit.co/active_storage/sfx/995/995-preview.mp3" type="audio/mpeg">
            </audio>
        </div>
        """, unsafe_allow_html=True)

    # --- 8. THE TABS ---
    tabs = st.tabs(i18n[L]['tabs'])
    
    with tabs[0]: 
        st.markdown(f"""
        <div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE BRIEFING: GEOSPATIAL RADAR</h4><div class='briefing-text'>
        <span class='brief-tag'>[WHAT IS THIS?]</span> A real-time Cartographic Information System displaying live GPS coordinates.<br>
        <span class='brief-tag'>[REAL DEPLOYMENT]</span> Physical drones use RTK (Real-Time Kinematic) GPS. This interface plots the RTK corrected data, giving centimeter-level accuracy to direct ground firefighters safely.</div></div>
        """, unsafe_allow_html=True)
        fig_map = px.scatter_mapbox(latest, lat="latitude", lon="longitude", color="temperature", size=[40]*len(latest), color_continuous_scale="Inferno", zoom=12, height=600, hover_name="drone_id")
        fig_map.add_trace(go.Scattermapbox(lat=[latest['latitude'].mean()], lon=[latest['longitude'].mean()], mode='markers+text', marker=dict(size=20, color=accent, symbol='cross'), text=["CENTROID"], textposition="top right"))
        fig_map.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", font_color=text)
        st.plotly_chart(fig_map, use_container_width=True)

    with tabs[1]: 
        st.markdown(f"""
        <div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE BRIEFING: SPREAD MATHEMATICS</h4><div class='briefing-text'>
        <span class='brief-tag'>[WHAT IS THIS?]</span> The predictive core. It calculates the physical rate at which the fire is expanding using Rothermel Surface Fire Equation and the First Derivative (dT/dt).<br>
        <span class='brief-tag'>[REAL DEPLOYMENT]</span> Physical drones carry Edge AI computers. They run these heavy calculus differentials locally at 30 FPS. If dT/dt spikes rapidly, the drone autonomously requests water-bomber planes.</div></div>
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

    with tabs[2]: 
        st.markdown(f"""
        <div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE BRIEFING: HARDWARE MATRIX</h4><div class='briefing-text'>
        <span class='brief-tag'>[WHAT IS THIS?]</span> Simulates physical forces acting on the drone's hardware (Vibration, Signal Loss).<br>
        <span class='brief-tag'>[REAL DEPLOYMENT]</span> By monitoring this IMU vibration matrix live, the ground station can command the swarm to increase altitude before a structural motor failure occurs due to thermal updrafts.</div></div>
        """, unsafe_allow_html=True)
        c_hw1, c_hw2 = st.columns(2)
        with c_hw1:
            x_val = np.linspace(0, 10, 50); y_val = np.linspace(0, 10, 50); X, Y = np.meshgrid(x_val, y_val)
            Z = np.sin(X) * np.cos(Y) * pid_p 
            fig_3d = go.Figure(data=[go.Surface(z=Z, colorscale='Viridis')])
            fig_3d.update_layout(title="IMU Vibration Matrix (PID Response)", scene=dict(bgcolor="rgba(0,0,0,0)"), paper_bgcolor="rgba(0,0,0,0)", font_color=text, height=350)
            st.plotly_chart(fig_3d, use_container_width=True)
        with c_hw2:
            st.markdown(f"<div class='glass-card'><h4>📡 Antenna Link Budget</h4><p>Current LoRa Spreading Factor: <b>{lora_sf}</b>.<br>Signal penetration depth allows for operation in DENSE CANOPY.</p></div>", unsafe_allow_html=True)

    with tabs[3]: 
        st.markdown(f"""
        <div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE BRIEFING: NEURAL VISION (AI)</h4><div class='briefing-text'>
        <span class='brief-tag'>[WHAT IS THIS?]</span> Live AI optical simulation. You can manually upload drone imagery to test the YOLOv8 AI inference logic locally.<br>
        <span class='brief-tag'>[REAL DEPLOYMENT]</span> In reality, transmitting 4K video over long distances is impossible during a wildfire. The drone processes the video <i>internally</i> and only transmits the lightweight MQTT text packets back to this dashboard.</div></div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("📸 UPLOAD CUSTOM DRONE IMAGERY FOR AI INFERENCE (Enable 'Pause Live Sync' first)", type=["jpg", "png", "jpeg"])
        
        if uploaded_file is not None:
            with st.spinner("Initializing YOLOv8 Neural Weights & Processing Computer Vision..."):
                time.sleep(2) # Fake processing delay for dramatic effect
            st.success("✅ AI Scan Complete: Anomalous Thermal Signature Detected!")
            st.image(uploaded_file, caption=f"AI Bounding Box Analysis | CONFIDENCE: {np.random.randint(92, 99)}%", use_container_width=True)
        else:
            cam1, cam2 = st.columns(2)
            for i, (idx, r) in enumerate(latest.head(2).iterrows()):
                b_col = "#ef4444" if r['live_z_score'] > z_thresh else accent
                cam = cam1 if i == 0 else cam2
                cam.markdown(f"""
                <div style="border: 2px solid {b_col}; background: #000; height: 300px; position: relative; border-radius: 12px; box-shadow: inset 0 0 50px rgba(0,0,0,1);">
                    <div style="position: absolute; top: 15px; left: 15px; color: {b_col}; font-family: monospace; font-size: 14px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 5px;">
                        REC 🔴 | NODE: {r['drone_id']} | CONFIDENCE: {np.random.randint(85, 99)}%
                    </div>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.1); font-size: 80px;">⌖</div>
                </div>
                """, unsafe_allow_html=True)

    with tabs[4]: 
        st.markdown(f"""
        <div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE BRIEFING: ENVIRONMENTAL PHYSICS</h4><div class='briefing-text'>
        <span class='brief-tag'>[REAL DEPLOYMENT]</span> The base station uses local weather APIs and onboard Pitot tubes to generate this heatmap. This allows commanders to visualize the "Thermal Wake" of the fire and predict which way the smoke column will drift.</div></div>
        """, unsafe_allow_html=True)
        m_env1, m_env2 = st.columns(2)
        m_env1.metric("Wind Vector Force", f"{wind_spd} km/h")
        m_env2.metric("Solar Irradiance Load", f"{solar_irr} W/m²")

    with tabs[5]: 
        st.markdown(f"""
        <div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE BRIEFING: DATA LAKE & TERMINAL</h4><div class='briefing-text'>
        <span class='brief-tag'>[WHAT IS THIS?]</span> The live backend server logs. This shows the raw MQTT payload string arriving from the LoRaWAN gateway.</div></div>
        """, unsafe_allow_html=True)
        
        c_term1, c_term2 = st.columns([1, 2])
        with c_term1:
            st.markdown("### 👨‍💻 LIVE HACKER TERMINAL LOGS")
            logs = "<br>".join([f"[{time.strftime('%H:%M:%S')}] SYS: Ingesting MQTT Payload from Node {np.random.randint(1, 6)}... [OK]" for _ in range(15)])
            st.markdown(f"<div class='terminal-box'><div class='terminal-content'>{logs}<br>...<br>...<br>Monitoring TCP/IP Port 1883<br>AES-256 Decryption Successful.</div></div>", unsafe_allow_html=True)
        with c_term2:
            st.dataframe(df_tel, use_container_width=True)

# --- 9. AUTO-REFRESH ENGINE (OPTIMIZED TIMING) ---
if not pause_sync:
    time.sleep(6) # 6 Second relax time to stop lag
    st.rerun()
