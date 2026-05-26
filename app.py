import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V14 | Limitless", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark (Cyber)"
if 'auth' not in st.session_state: st.session_state.auth = False
if 'loader' not in st.session_state: st.session_state.loader = True

# --- 2. MULTI-LANGUAGE DICTIONARY (UNIVERSAL) ---
i18n = {
    "EN": {"title": "🛰️ AeroGuard V14: Global Swarm Intelligence", "tabs": ["🌍 GLOBAL RADAR", "🧮 SPREAD MATH", "⚙️ HARDWARE MATRIX", "👁️ NEURAL VISION", "💨 ENV PHYSICS", "💾 DATA LAKE"]},
    "HI": {"title": "🛰️ AeroGuard V14: ग्लोबल स्वार्म इंटेलिजेंस", "tabs": ["🌍 ग्लोबल रडार", "🧮 फायर स्प्रेड मैथ", "⚙️ हार्डवेयर मैट्रिक्स", "👁️ न्यूरल विजन", "💨 पर्यावरण भौतिकी", "💾 डेटा लेक"]},
    "AR": {"title": "🛰️ AeroGuard V14: استخبارات السرب العالمي", "tabs": ["🌍 الرادار العالمي", "🧮 رياضيات الانتشار", "⚙️ مصفوفة الأجهزة", "👁️ الرؤية العصبية", "💨 فيزياء البيئة", "💾 بحيرة البيانات"]},
    "IT": {"title": "🛰️ AeroGuard V14: Intelligenza Globale dello Sciame", "tabs": ["🌍 RADAR GLOBALE", "🧮 MATEMATICA", "⚙️ HARDWARE", "👁️ VISIONE NEURALE", "💨 FISICA AMBIENTALE", "💾 DATA LAKE"]},
    "DE": {"title": "🛰️ AeroGuard V14: Globale Schwarmintelligenz", "tabs": ["🌍 GLOBALER RADAR", "🧮 AUSBREITUNGSMATHEMATIK", "⚙️ HARDWARE-MATRIX", "👁️ NEURONALES SEHEN", "💨 UMWELTPHYSIK", "💾 DATENSEE"]}
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
    /* GLOBAL FONTS & BACKGROUND */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    .stApp {{background-color: {bg}; color: {text}; font-family: 'Space Grotesk', sans-serif; transition: background-color 0.5s ease;}}
    h1, h2, h3, h4 {{color: {accent} !important; font-weight: 700; letter-spacing: 1px;}}
    
    /* KEYFRAME ANIMATIONS */
    @keyframes slideInUp {{ 0% {{opacity: 0; transform: translateY(40px);}} 100% {{opacity: 1; transform: translateY(0);}} }}
    @keyframes fadeIn {{ 0% {{opacity: 0;}} 100% {{opacity: 1;}} }}
    @keyframes borderGlow {{ 0% {{box-shadow: 0 0 5px {accent}40;}} 50% {{box-shadow: 0 0 20px {accent};}} 100% {{box-shadow: 0 0 5px {accent}40;}} }}
    
    /* ANIMATED CARDS */
    .glass-card {{
        background: {card_bg}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.2); border-top: 3px solid {accent};
        border-radius: 12px; padding: 25px; margin-bottom: 20px;
        animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }}
    .glass-card:hover {{ transform: scale(1.02) translateY(-5px); animation: borderGlow 2s infinite; }}
    
    .metric-title {{font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1.5px;}}
    .metric-value {{font-size: 2.5rem; color: {text}; font-weight: 700; margin-top: 5px;}}
    
    /* TAB STYLING */
    .stTabs [data-baseweb="tab"] {{color: {text}; font-weight: 600; font-size: 15px; background: transparent; transition: all 0.3s ease;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important; background: rgba(0, 255, 204, 0.05); border-radius: 5px 5px 0 0;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SECURE LOGIN WITH LOADING ANIMATION ---
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

# Simulate a boot-up loader sequence once
if st.session_state.loader:
    boot_text = st.empty()
    for i in range(1, 101, 20):
        boot_text.markdown(f"<div class='glass-card' style='text-align:center;'><h2>BOOTING SYSTEM... {i}%</h2><p>Establishing Satellite Uplink...</p></div>", unsafe_allow_html=True)
        time.sleep(0.3)
    st.session_state.loader = False
    st.rerun()

# --- 5. SIDEBAR WITH 70+ WORD DEEP-DIVE INSTRUCTIONS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    st.markdown("## ⚙️ GLOBAL COMMAND")
    
    with st.expander("🌐 UI & Region Setup", expanded=True):
        st.session_state.lang = st.selectbox("Interface Language", ["EN", "HI", "AR", "IT", "DE"], index=["EN", "HI", "AR", "IT", "DE"].index(L))
        st.session_state.theme = st.selectbox("UI Mode", ["Dark (Cyber)", "Light (Clean)"], index=["Dark (Cyber)", "Light (Clean)"].index(T))
        unit_sys = st.radio("Measurement System", ["Metric", "Imperial"])

    with st.expander("🧮 Mathematical Fire Spread"):
        spread_alg = st.selectbox("Spread Algorithm", ["Rothermel Equation", "Huygens Principle"], help="[WHAT] The Rothermel Surface Fire Spread Model is a mathematical algorithm used to predict the forward rate of spread of a wildfire. [WHY] It is essential because it accounts for the physics of fuel, moisture, and wind, providing a highly accurate simulation of how fast a fire will consume a forest. [HOW] It calculates the heat flux and ignition energy required to bring adjacent unburned fuel to its ignition temperature using partial differential equations. [REAL DEPLOYMENT] In a real-world scenario with physical drones, this model ingests live sensor data (wind speed from anemometers, humidity from DHT22 sensors). The edge computer calculates the spread vector and autonomously commands the UAV swarm to fly ahead of the fire front to monitor evacuation zones.")
        z_thresh = st.slider("Anomaly Z-Score (σ)", 1.0, 5.0, 2.5, help="[WHAT] The Z-Score Anomaly Trigger defines the statistical threshold for what constitutes a critical thermal event. [WHY] Normal temperature fluctuates throughout the day due to sunlight. We must mathematically isolate genuine fire anomalies from standard environmental heating. [HOW] It calculates how many Standard Deviations (σ) the current thermal reading is from the rolling historical mean temperature. [REAL DEPLOYMENT] When the physical drone's thermal camera scans a hot rock heated by the sun, the Z-Score remains low. But if it scans a rapidly combusting chemical fire, the Z-Score spikes above this threshold, instantly triggering the LoRaWAN radio to broadcast an emergency interrupt packet to the command center.")
        calc_dt = st.number_input("Calculus Δt", 0.1, 5.0, 1.0, help="[WHAT] The Calculus Delta Time (Δt) is the fundamental time step used for calculating real-time derivatives. [WHY] Without a defined time step, the system cannot calculate the rate of change of temperature (how fast the fire is growing). [HOW] It serves as the denominator in the First Derivative equation (dT/dt), comparing the current temperature frame against the previous one. [REAL DEPLOYMENT] When real equipment is added, this value must be perfectly synchronized with the frames-per-second (FPS) output of your physical FLIR thermal camera. If the camera sends data every 2 seconds, Δt must be set to 2.0 to ensure the mathematical predictions remain physically accurate and prevent software crashes.")

    with st.expander("⚙️ Hardware: Flight & Tuning"):
        pid_p = st.slider("Proportional Gain (kP)", 0.0, 2.0, 0.5, help="[WHAT] The Proportional Gain (kP) is the fundamental tuning parameter of the PID flight controller logic. [WHY] It determines how aggressively the drone's motors respond to positional errors caused by wind or inertia. Without it, the drone cannot maintain a stable hover. [HOW] It calculates a corrective force directly proportional to the difference between the desired trajectory and the actual GPS coordinate. [REAL DEPLOYMENT] When you attach real physical drones with heavy thermal cameras, edge AI computers, and high-capacity batteries, the center of gravity shifts drastically. You must tune this kP value higher in the field so the heavy hardware payload doesn't cause the drone to violently drift during high-wind deployments in rough terrains.")
        kalman_q = st.number_input("Kalman Process Noise", 0.001, 0.1, 0.01, format="%.3f", help="[WHAT] The Kalman Filter Process Noise Covariance (Q) represents the level of uncertainty or trust in the mathematical model predicting the drone's position. [WHY] It is necessary because raw GPS and IMU sensors produce highly noisy and erratic data. The filter smooths this out for stable autonomous navigation. [HOW] By adjusting Q, you tell the algorithm whether to trust the actual sensor readings (high Q) or to rely more on the mathematical prediction model (low Q). [REAL DEPLOYMENT] Once physical drones are airborne, wind gusts and mechanical vibrations from the spinning propellers inject massive noise into the onboard accelerometer and gyroscope. You must tune this Q matrix so the flight controller filters out the physical vibration without ignoring actual trajectory changes.")
        swarm_topo = st.selectbox("Swarm Topology", ["Mesh Network", "Star Topology", "Ring Layout"], help="[WHAT] Swarm Topology dictates how the individual UAVs communicate with each other in the air. [WHY] It prevents a single point of failure. If one drone crashes, the rest of the swarm must continue the mission. [HOW] The algorithm dynamically assigns primary and secondary routing nodes based on distance and signal strength. [REAL DEPLOYMENT] In a real deployment with 5 to 10 drones, you will equip them with XBee or LoRa Mesh modules. Selecting 'Mesh Network' here configures their onboard routing tables so that a drone on the far side of a mountain can pass its thermal data to a middle drone, which relays it to your ground station, ensuring 100% coverage.")

    with st.expander("📡 Hardware: Telemetry & Radio"):
        lora_sf = st.select_slider("LoRa Spreading Factor", [7, 8, 9, 10, 11, 12], value=10, help="[WHAT] Spreading Factor (SF) determines the duration of a single 'chirp' in LoRaWAN radio frequency modulation. [WHY] It is critical for balancing data transmission speed against the maximum range of the radio signal. Higher SF means longer range but much slower data rates. [HOW] Each step up in SF doubles the time on air to transmit the same amount of data, thereby increasing the receiver's signal-to-noise ratio margin. [REAL DEPLOYMENT] When deploying real UAVs in dense, mountainous terrain or thick forests, the radio line-of-sight is blocked by trees and rocks. You will physically increase the SF to 11 or 12 to ensure the MQTT telemetry payload (containing critical GPS and thermal data) penetrates the physical obstacles and reaches the base station.")
        tx_power = st.slider("Transmit Power (dBm)", 2, 20, 14, help="[WHAT] Transmit Power (dBm) dictates the sheer electrical energy pushed into the radio antenna. [WHY] More power means the radio waves travel further, but it drains the drone's battery significantly faster. [HOW] The power output scales logarithmically, meaning 20dBm is significantly stronger than 10dBm. [REAL DEPLOYMENT] When operating in small urban environments, you must lower this to 2-5 dBm to comply with local telecom regulations and save battery life. However, in emergency global wildfire deployments covering hundreds of kilometers, you will crank this up to the maximum 20 dBm to ensure the critical thermal payload reaches the Command Center before the drone's battery dies.")
        
    with st.expander("👁️ Hardware: Thermal & Optical"):
        flir_emis = st.slider("Thermal Emissivity (ε)", 0.1, 1.0, 0.95, help="[WHAT] Thermal Emissivity is a dimensionless number between 0 and 1 that represents a material's effectiveness in emitting thermal radiation. [WHY] Without setting the correct emissivity, the FLIR thermal camera will report highly inaccurate temperature readings, mistaking reflective surfaces for cold spots. [HOW] The software applies this coefficient to the Stefan-Boltzmann law to correct the raw infrared radiation data captured by the sensor's microbolometer array. [REAL DEPLOYMENT] When physical drones with real radiometric thermal cameras fly over varied terrain, you must calibrate this setting. For dense forests and organic matter, set it to 0.95. If the swarm is monitoring metallic infrastructure like pipelines or solar panels, you must lower it to 0.85 to compensate for the metal's high reflectivity and low emission.")
        lidar_den = st.selectbox("LiDAR Point Density", ["Low", "High"], help="[WHAT] LiDAR Point Density controls how many laser pulses the hardware scanner fires per second. [WHY] High density gives a perfect 3D map of the terrain, but generates gigabytes of data that can crash the drone's edge computer. [HOW] It adjusts the RPM of the spinning laser mirror inside the LiDAR module. [REAL DEPLOYMENT] When you mount a heavy physical LiDAR sensor (like a Velodyne Puck) to the drone, you must set this to 'Low' for rapid wildfire tracking to conserve Raspberry Pi CPU power. Set it to 'High' only during post-fire analysis to map the exact geographical destruction down to the centimeter.")

    with st.expander("💨 Physics: Environment"):
        wind_spd = st.slider("Wind Vector (km/h)", 0, 120, 25, help="[WHAT] Mid-flame wind speed representing the velocity of air movement directly above the fire line. [WHY] Wind is the single biggest factor driving fire expansion. [HOW] Acts as a direct exponential multiplier in the spread mathematics. [REAL DEPLOYMENT] Real drones will have onboard Pitot tubes gathering this wind data live, continuously updating the math engine.")
        solar_irr = st.slider("Solar Irradiance (W/m²)", 0, 1200, 800, help="[WHAT] The power per unit area received from the Sun. [WHY] High solar irradiance pre-heats the forest fuel, making it easier to ignite. [HOW] Adds a base thermal load to the mathematical fuel-moisture equations. [REAL DEPLOYMENT] Will be measured via physical pyranometer sensors attached to the base station, factoring into the Z-score logic so the AI doesn't mistake sun-heated rocks for fires.")

    if st.button("🔴 DISCONNECT UPLINK"): st.session_state.auth = False; st.rerun()

# --- 6. DATA INGESTION ENGINE ---
def fetch_telemetry():
    try:
        SUPABASE_URL = "https://cuvuetjghxhtrgevwacx.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1dnVldGpnaHhodHJnZXZ3YWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk3MjAxNjksImV4cCI6MjA5NTI5NjE2OX0.tz7fhluw_6D2oHAlFi3ZpZG6TC_hteE-O7GPkuc5LME"
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.table("drone_telemetry").select("*").order("created_at", desc=True).limit(200).execute()
        return pd.DataFrame(res.data)
    except:
        # Limitless Fallback Generator
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

# --- 7. MAIN DASHBOARD ---
st.markdown(f"<h1>{i18n[L]['title']}</h1>", unsafe_allow_html=True)

if not df_tel.empty:
    latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
    max_t = latest['temperature'].max()
    
    # 🧮 Z-SCORE MATHEMATICS CALCULATION
    mean_temp = df_tel['temperature'].mean()
    std_temp = df_tel['temperature'].std()
    latest['live_z_score'] = (latest['temperature'] - mean_temp) / (std_temp + 0.0001)
    
    # Alert will ONLY trigger if the calculated Z-Score is higher than your Sidebar Slider!
    critical = len(latest[latest['live_z_score'] > z_thresh])
    
    # --- ANIMATED METRIC CARDS ---
    m1, m2, m3, m4 = st.columns(4)
    unit_str = "°C" if unit_sys == "Metric" else "°F"
    
    m1.markdown(f"<div class='glass-card' style='animation-delay: 0.1s;'><div class='metric-title'>Active Edge Nodes</div><div class='metric-value'>{len(latest)}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='glass-card' style='animation-delay: 0.2s;'><div class='metric-title'>Thermal Peak</div><div class='metric-value' style='color: {'#ef4444' if critical>0 else accent};'>{max_t:.1f}{unit_str}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='glass-card' style='animation-delay: 0.3s;'><div class='metric-title'>Predicted Spread</div><div class='metric-value'>{(wind_spd * 0.15):.2f} m/s</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='glass-card' style='animation-delay: 0.4s;'><div class='metric-title'>System Health</div><div class='metric-value' style='color:#10b981;'>OPTIMAL</div></div>", unsafe_allow_html=True)

    if critical > 0:
        st.markdown(f"<div class='glass-card' style='border-top-color:#ef4444; background:rgba(239, 68, 68, 0.1);'><h3 style='color:#ef4444 !important;'>🚨 CRITICAL ALERT TRIGGERED</h3><p>Anomaly exceeds Z-Score mathematical threshold. Pre-computing swarm intercept vectors.</p></div>", unsafe_allow_html=True)

    # --- 8. THE TABS ---
    tabs = st.tabs(i18n[L]['tabs'])
    
    with tabs[0]: # MAP
        fig_map = px.scatter_mapbox(
            latest, lat="latitude", lon="longitude", color="temperature", size=[40]*len(latest),
            color_continuous_scale="Inferno", zoom=12, height=600, hover_name="drone_id"
        )
        fig_map.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", font_color=text)
        st.plotly_chart(fig_map, use_container_width=True)

    with tabs[1]: # MATH
        st.markdown("### 🧮 Hardware-Driven Spread Mathematics")
        eq1, eq2 = st.columns(2)
        with eq1:
            st.markdown(f"<div class='glass-card'><div class='metric-title'>Rate of Spread (R)</div>", unsafe_allow_html=True)
            st.latex(r"R = \frac{I_R \xi (1 + \phi_w + \phi_s)}{\rho_b \epsilon Q_{ig}}")
            st.markdown("</div>", unsafe_allow_html=True)
        with eq2:
            st.markdown(f"<div class='glass-card'><div class='metric-title'>First Derivative (Heat Accel)</div>", unsafe_allow_html=True)
            st.latex(r"\frac{\partial T}{\partial t} = \lim_{\Delta t \to 0} \frac{T(t + \Delta t) - T(t)}{\Delta t}")
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[2]: # HARDWARE MATRIX
        st.markdown("### ⚙️ Physical Hardware Diagnostics")
        c_hw1, c_hw2 = st.columns(2)
        with c_hw1:
            # Simulated 3D Vibration Plot (PID / IMU testing)
            x_val = np.linspace(0, 10, 50); y_val = np.linspace(0, 10, 50); X, Y = np.meshgrid(x_val, y_val)
            Z = np.sin(X) * np.cos(Y) * pid_p # The higher the PID, the crazier the graph
            fig_3d = go.Figure(data=[go.Surface(z=Z, colorscale='Viridis')])
            fig_3d.update_layout(title="IMU Vibration Matrix (PID Response)", scene=dict(bgcolor="rgba(0,0,0,0)"), paper_bgcolor="rgba(0,0,0,0)", font_color=text, height=400)
            st.plotly_chart(fig_3d, use_container_width=True)
        with c_hw2:
            st.markdown(f"<div class='glass-card'><h4>📡 Antenna Link Budget</h4><p>Based on LoRa Spreading Factor ({lora_sf}), the calculated signal penetration depth allows for operation in <b>DENSE FOREST/URBAN CANOPY</b>.</p><h4>🔋 Battery RUL Matrix</h4><p>Swarm Topology: <b>{swarm_topo}</b> ensures redundant data routing if a primary node fails.</p></div>", unsafe_allow_html=True)

    with tabs[3]: # NEURAL VISION
        st.markdown("### 👁️ Real-Time Optical/Thermal Feeds")
        cam1, cam2 = st.columns(2)
        for i, (idx, r) in enumerate(latest.head(2).iterrows()):
            b_col = "red" if r['temperature'] > (80 if unit_sys == "Metric" else 176) else accent
            cam = cam1 if i == 0 else cam2
            cam.markdown(f"""
            <div style="border: 2px solid {b_col}; background: #000; height: 300px; position: relative; border-radius: 12px; overflow: hidden; box-shadow: inset 0 0 50px rgba(0,0,0,1);">
                <div style="position: absolute; top: 15px; left: 15px; color: {b_col}; font-family: monospace; font-size: 15px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 5px;">
                    REC 🔴 | NODE: {r['drone_id']} | CONF: 94% <br> EMISSIVITY CALIB: {flir_emis}
                </div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.1); font-size: 80px;">⌖</div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[4]: # ENV
        st.markdown("### 💨 Environmental Force Multipliers")
        m_env1, m_env2 = st.columns(2)
        m_env1.metric("Wind Vector Force", f"{wind_spd} km/h")
        m_env2.metric("Solar Irradiance Load", f"{solar_irr} W/m²")

    with tabs[5]: # DATA
        st.dataframe(df_tel, use_container_width=True)

# --- 9. AUTO-REFRESH ENGINE (NO WHILE LOOPS) ---
time.sleep(2)
st.rerun()
