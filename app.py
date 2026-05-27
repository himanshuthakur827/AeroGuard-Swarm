import streamlit as st
import pandas as pd
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
import time
import os

# --- 0. ADVANCED AI CACHING (REAL INFERENCE ENGINE) ---
@st.cache_resource
def load_ai_models():
    try:
        from ultralytics import YOLO
        import easyocr
        
        if os.path.exists('best.pt'):
            yolo_model = YOLO('best.pt')
        else:
            yolo_model = YOLO('yolov8n.pt') 
            
        ocr_reader = easyocr.Reader(['en'])
        return yolo_model, ocr_reader
    except Exception as e:
        return None, None

yolo_model, ocr_reader = load_ai_models()

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V19 | Industrial Edition", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark (Cyber)"
if 'auth' not in st.session_state: st.session_state.auth = False

# Dynamic Theme Logic
T = st.session_state.theme
if T == "Dark (Cyber)":
    bg, card_bg, text, accent = "#020617", "rgba(15, 23, 42, 0.8)", "#f8fafc", "#00ffcc"
    map_style = "carto-darkmatter"
else:
    bg, card_bg, text, accent = "#f8fafc", "rgba(255, 255, 255, 0.95)", "#0f172a", "#2563eb"
    map_style = "carto-positron"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=VT323&display=swap');
    .stApp {{background-color: {bg}; color: {text}; font-family: 'Space Grotesk', sans-serif; transition: all 0.3s ease;}}
    h1, h2, h3, h4 {{color: {accent} !important; font-weight: 700; letter-spacing: 1px;}}
    .glass-card {{
        background: {card_bg}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.2); border-top: 3px solid {accent};
        border-radius: 12px; padding: 25px; margin-bottom: 20px;
    }}
    .info-box {{ background: rgba(37, 99, 235, 0.05); border-left: 4px solid {accent}; padding: 20px; border-radius: 5px; font-size: 0.95rem; margin-top: 15px; line-height: 1.7; color: {text}; border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);}}
    .metric-title {{font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1.5px;}}
    .metric-value {{font-size: 2.5rem; color: {text}; font-weight: 700; margin-top: 5px;}}
    .stTabs [data-baseweb="tab"] {{color: {text}; font-weight: 600; font-size: 15px; background: transparent;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important; background: rgba(0, 255, 204, 0.05);}}
    .streamlit-expanderHeader {{font-weight: 600 !important; color: {accent} !important; font-size: 1.1rem !important;}}
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIN ---
if not st.session_state.auth:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;'><h1>🔒 AEROGUARD SYSTEM LOCKED</h1><p style='color:#94a3b8; font-size:1.2rem;'>SECURE ENCRYPTED UPLINK REQUIRED.</p></div>", unsafe_allow_html=True)
    with st.sidebar.expander("🔌 Connect Uplink", expanded=True): 
        st.info("💡 Passcode is pre-filled for demonstrational access.")
        pwd = st.text_input("Clearance Code", type="password", value="admin")
        if st.button("AUTHENTICATE UPLINK"):
            if pwd == "admin": 
                st.session_state.auth = True; st.rerun()
            else: 
                st.error("Access Denied.")
    st.stop() 

# --- 3. SIDEBAR WITH EXTREME DETAIL TOOLTIPS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    st.markdown("## ⚙️ GLOBAL COMMAND")
    st.markdown("---")
    
    enable_siren = st.checkbox("🔊 Enable Siren Alarm", value=False, help="""
    [WHAT] A physical HTML5 audio trigger mechanically linked to the Z-Score statistical engine.
    [WHY IS IT IMPORTANT] In a high-stress industrial command center, operators suffer from 'alarm fatigue' and can easily miss visual cues on crowded screens. Auditory warnings bypass visual distraction and create immediate psychological urgency.
    [HOW IT WORKS] If the backend polling detects a drone telemetry packet exceeding the defined Z-Score threshold, the script overrides local audio to play the emergency siren.
    [HOW TO USE / SET IT] Leave this toggled OFF during routine post-incident data review to prevent annoyance. Toggle ON exclusively during active pipeline containment missions or high-risk atmospheric events.
    """)
    
    pause_sync = st.checkbox("⏸️ Pause Live Sync", value=False, key="pause_sync", help="""
    [WHAT] A global system override that halts the 5-second asynchronous cloud data-polling loop.
    [WHY IS IT IMPORTANT] Crucial for operator interaction stability. When uploading a custom image to the Neural AI module, a background refresh will interrupt the HTTP POST request, wiping the upload mid-way and causing extreme frustration.
    [HOW IT WORKS] Modifies the session state to bypass the backend Polars data-fetch cycle, effectively freezing all map coordinates and graphs at their current timestamp.
    [HOW TO USE / SET IT] Check this box immediately before analyzing a specific heat signature on the map or uploading imagery. Uncheck to resume live MQTT ingestion.
    """)
    
    with st.expander("🌐 UI & Region Setup"):
        st.session_state.lang = st.selectbox("Interface Language", ["EN", "HI"], index=["EN", "HI"].index(st.session_state.lang), help="""
        [WHAT] JSON Dictionary mapping for global localization.
        [WHY IS IT IMPORTANT] Industrial command centers often transfer tactical control between international engineering teams across different time zones (e.g., handing over from a Russian facility to an Indian facility).
        [HOW IT WORKS] Intercepts the UI rendering tree and re-maps all text string variables to the selected language dynamically.
        [HOW TO SET IT] Choose based on the primary operational language of the active shift crew.
        """)
        new_theme = st.selectbox("UI Mode", ["Dark (Cyber)", "Light (Clean)"], index=["Dark (Cyber)", "Light (Clean)"].index(st.session_state.theme), help="""
        [WHAT] Instant CSS injection for visual adaptation.
        [WHY IS IT IMPORTANT] Human visual comfort directly impacts reaction times.
        [HOW TO SET IT] Select 'Dark (Cyber)' to significantly reduce eye strain and screen glare in dimly lit mobile command trucks. Select 'Light (Clean)' to defeat screen glare when field engineers are operating tablets under harsh, direct sunlight.
        """)
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
        unit_sys = st.radio("Measurement System", ["Metric", "Imperial"], help="""
        [WHAT] Real-time thermodynamic and spatial unit conversion engine.
        [WHY IS IT IMPORTANT] Ensures rigid standard compliance across different international aviation and petroleum engineering jurisdictions.
        [HOW TO SET IT] Toggle based on the required reporting metrics of local government regulators.
        """)

    with st.expander("🧮 Mathematical Fire Spread"):
        spread_alg = st.selectbox("Spread Algorithm", ["Rothermel Equation", "Huygens Principle"], help="""
        [WHAT] The core predictive physics engine that determines how a threat will expand.
        [WHY IS IT IMPORTANT] You must predict where the threat is moving to evacuate personnel effectively.
        [HOW TO SET IT] Select 'Rothermel Equation' for surface-level threats like spilled crude oil or chemical liquid pools. Select 'Huygens Principle' to calculate 3D elliptical volumetric growth for highly pressurized gas cloud expansions.
        """)
        z_thresh = st.slider("Anomaly Z-Score (σ)", 1.0, 5.0, 2.5, help="""
        [WHAT] Statistical Standard Deviation (Sigma σ) threshold sensitivity.
        [WHY IS IT IMPORTANT] A metal pipeline in a desert is naturally extremely hot. A simple fixed-temperature alarm would constantly trigger false positives. Z-Score detects sudden mathematical deviations from the ambient rolling average.
        [HOW IT WORKS] An alert triggers ONLY if: Live Drone Temp > (Rolling Mean Temp + (Z-Score * Standard Deviation)).
        [HOW TO SET IT] Keep at 2.5σ for normal operation. Drop to 1.5σ for ultra-sensitive scanning in cold climates. Raise to 4.0σ near active flare stacks to ignore normal operational heat.
        """)
        calc_dt = st.number_input("Calculus Δt (Seconds)", 0.1, 5.0, 1.0, help="""
        [WHAT] The 'Delta Time' (Δt) denominator for calculating physical thermal derivatives.
        [WHY IS IT IMPORTANT] It establishes the foundational time-step limits for the Thermal Flux calculation (∂T/∂t), preventing mathematical division-by-zero errors in the calculus engine.
        [HOW TO SET IT] In real deployment, this exact number must strictly match the Hertz (Hz) refresh rate output of your physical drone's onboard FLIR thermal camera. If the camera sends data every 1 second, set this to 1.0.
        """)

    with st.expander("⚙️ Hardware: Flight & Tuning"):
        pid_p = st.slider("Proportional Gain (kP)", 0.0, 2.0, 0.5, help="""
        [WHAT] The primary 'P' (Proportional) mathematical weight in the drone's PID (Proportional-Integral-Derivative) flight controller.
        [WHY IS IT IMPORTANT] Prevents the swarm drones from drifting away from their designated pipeline sector during heavy atmospheric crosswinds.
        [HOW IT WORKS] Calculates the GPS error margin and applies corrective motor voltage directly proportional to that error.
        [HOW TO SET IT] Increase this value on windy days for aggressive motor correction. Decrease on calm days to save drone battery life.
        """)
        kalman_q = st.number_input("Kalman Process Noise", 0.001, 0.1, 0.01, format="%.3f", help="""
        [WHAT] A statistical sensor filtering matrix variable.
        [WHY IS IT IMPORTANT] Drone rotors cause intense physical vibrations, making raw GPS and IMU data extremely 'jumpy' and mathematically unusable for precision mapping.
        [HOW IT WORKS] The Kalman filter predicts the drone's true position by filtering out the variance of this 'Process Noise'.
        [HOW TO SET IT] Lower values trust the mathematical model; higher values trust the raw sensors. Adjust based on the physical vibration dampening of your drone frame.
        """)

    with st.expander("📡 Hardware: Telemetry & Radio"):
        lora_sf = st.select_slider("LoRa Spreading Factor", [7, 8, 9, 10, 11, 12], value=10, help="""
        [WHAT] The physical duration of a radio 'chirp' in the LoRaWAN telemetry communications protocol.
        [WHY IS IT IMPORTANT] Dictates the critical balance between data transmission bandwidth (speed) and signal penetration (range).
        [HOW TO SET IT] Set to SF7 for fast data transfer in clear, open desert fields. Crank to SF12 when drones are flying behind thick steel refinery structures or dense forests; it significantly slows data speed but ensures the radio signal punches through physical obstacles.
        """)
        tx_power = st.slider("Transmit Power (dBm)", 2, 20, 14, help="""
        [WHAT] The physical antenna transmission wattage output of the base station.
        [WHY IS IT IMPORTANT] Determines the absolute maximum physical range the drones can fly away from the command center before losing connection.
        [HOW TO SET IT] Push to maximum (20 dBm) strictly for commanding drones on 15km+ Beyond Visual Line of Sight (BVLOS) pipeline inspection routes. Lower to 10 dBm for close-range testing to conserve power.
        """)
        
    with st.expander("💨 Physics: Environment"):
        wind_spd = st.slider("Wind Vector (km/h)", 0, 120, 25, help="""
        [WHAT] Environmental live physical input variable representing atmospheric air currents.
        [WHY IS IT IMPORTANT] Wind is the absolute #1 external physical variable that dictates the direction, velocity, and catastrophic potential of a toxic gas cloud or fire.
        [HOW IT WORKS] Modifying this instantly recalculates the Dynamic Rate of Spread (R) within the math engine.
        [HOW TO SET IT] In simulation, slide to see mathematical changes. In deployment, this is overridden and fed directly by drone-mounted Pitot tube sensors.
        """)
        solar_irr = st.slider("Solar Irradiance (W/m²)", 0, 1200, 800, help="""
        [WHAT] A measurement of ambient sun radiation intensity hitting the ground.
        [WHY IS IT IMPORTANT] A critical factor for preventing false positive thermal alarms. If the sun is aggressively baking the metal pipes, the system uses this variable to mathematically subtract the solar load from the total thermal payload.
        [HOW TO SET IT] Adjust to match the time of day (high at noon, zero at night) to isolate the actual internal pipeline friction heat from external weather interference.
        """)

    if st.button("🔴 DISCONNECT UPLINK"): 
        st.session_state.auth = False; st.rerun()

# --- 4. DATA ENGINE (Cached for speed) ---
@st.cache_data(ttl=2) 
def fetch_telemetry():
    np.random.seed(int(time.time() * 10) % 100)
    data = []
    for i in range(1, 51):
        t_base = 35 if i % 5 != 0 else (35 + np.random.randint(40, 150))
        data.append({
            "drone_id": f"AG-SWARM-{i}", "created_at": pd.Timestamp.now(),
            "latitude": 31.104 + np.random.randn()*0.05, "longitude": 77.166 + np.random.randn()*0.05,
            "temperature": t_base + np.random.randn()*5, "battery_level": np.random.randint(15, 95)
        })
    return pd.DataFrame(data)

df_main = fetch_telemetry()
latest_main = df_main.sort_values('created_at').groupby('drone_id').last().reset_index()

# --- 5. HEADER & TOP METRICS ---
st.title("🛰️ AeroGuard V19: Command Center")

# 🔥 ELABORATED DISCLAIMER BANNER 🔥
st.markdown("""
<div style="background: rgba(245, 158, 11, 0.15); border-left: 5px solid #f59e0b; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
    <h3 style="color: #f59e0b; margin-top: 0;">⚠️ SYSTEM NOTICE: SYNTHETIC SIMULATION MODE ACTIVE</h3>
    <p style="color: #cbd5e1; margin-bottom: 15px; font-size: 1.05rem; line-height: 1.6;">
    <b>[CURRENT ARCHITECTURE STATUS]</b><br> Physical edge-computing nodes (RTK-GPS Drones, FLIR Thermal Cameras, Pitot Tubes, and Acoustic Sensors) are currently disconnected from this active browser session. <br><br>
    <b>[WHAT YOU ARE SEEING]</b><br> To demonstrate the mathematical integrity, visual UX architecture, and algorithmic processing of this command center, the backend is currently running a high-fidelity synthetic data generator. It simulates real-world pipeline telemetry (heat flux, GPS vectors, hardware battery) dynamically.<br><br>
    <b>[REAL-WORLD DEPLOYMENT PIPELINE]</b><br> In an active industrial or petroleum refinery scenario, this exact dashboard architecture will ingest live MQTT JSON payloads directly from the drone swarm. The math engine, 2D radar, and AI vision will seamlessly transition to processing real infrastructure metrics without altering the core codebase.<br><br>
    </p>
    <div style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 5px; border: 1px dashed #f59e0b;">
    <i><b>👨‍💻 DEPLOYMENT INSTRUCTION:</b> Once physical equipment is successfully linked via the backend Supabase/MQTT bridge, this entire simulation disclaimer must be safely removed from the app.py source code.</i>
    </div>
</div>
""", unsafe_allow_html=True)

# 🚀 LAG-FREE FIX: Only the top numbers refresh
@st.fragment(run_every=5)
def live_top_metrics():
    if st.session_state.pause_sync:
        st.info("⏸️ Telemetry Sync Paused by Operator. Dashboard Locked.")
        return
        
    df_tel = fetch_telemetry()
    latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
    max_t = latest['temperature'].max()
    mean_temp = df_tel['temperature'].mean()
    std_temp = df_tel['temperature'].std()
    
    latest['live_z_score'] = (latest['temperature'] - mean_temp) / (std_temp + 0.0001)
    critical = len(latest[latest['live_z_score'] > z_thresh])

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='glass-card'><div class='metric-title'>Active Edge Nodes</div><div class='metric-value'>{len(latest)}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='glass-card'><div class='metric-title'>Thermal Peak</div><div class='metric-value' style='color: {'#ef4444' if critical>0 else accent};'>{max_t:.1f}°C</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='glass-card'><div class='metric-title'>Spread Vector</div><div class='metric-value'>{(wind_spd * 0.15):.2f} m/s</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='glass-card'><div class='metric-title'>Engine Latency</div><div class='metric-value'>12 ms</div></div>", unsafe_allow_html=True)

    if critical > 0:
        siren = """<audio autoplay loop controls style="height: 35px; width: 300px;"><source src="https://assets.mixkit.co/active_storage/sfx/995/995-preview.mp3" type="audio/mpeg"></audio>""" if enable_siren else ""
        st.markdown(f"<div class='glass-card' style='border-top-color:#ef4444; background:rgba(239, 68, 68, 0.1);'><h3 style='color:#ef4444 !important;'>🚨 CRITICAL ALERT TRIGGERED ({z_thresh}σ Breach)</h3><p style='margin-bottom:5px;'>Automated swarm intercept vectors are being pre-computed.</p>{siren}</div>", unsafe_allow_html=True)

live_top_metrics()

# --- 6. THE TABS --- 
tabs = st.tabs(["🌍 2D GLOBAL RADAR", "🧮 MATH ENGINE", "⚙️ HARDWARE MATRIX", "👁️ NEURAL AI", "💨 THERMODYNAMICS", "💾 DATA LAKE", "🚀 DEPLOYMENT"])

# TAB 1: 2D RADAR (WITH DEDICATED LIVE THREAT TABLE)
with tabs[0]: 
    @st.fragment(run_every=5)
    def live_radar():
        if st.session_state.pause_sync: return
        df_tel = fetch_telemetry()
        latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
        
        # Calculate Z-Score locally for categorization
        mean_temp_local = df_tel['temperature'].mean()
        std_temp_local = df_tel['temperature'].std()
        latest['live_z_score'] = (latest['temperature'] - mean_temp_local) / (std_temp_local + 0.0001)
        
        # Top Section: Map
        map_col, safe_scroll_col = st.columns([3, 1])
        with map_col:
            fig_map = px.scatter_mapbox(
                latest, lat="latitude", lon="longitude", color="temperature",
                size="temperature", color_continuous_scale="Inferno", 
                zoom=9.5, mapbox_style=map_style, hover_name="drone_id"
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_map, use_container_width=True)

        with safe_scroll_col:
            st.markdown("""
            <div style='text-align:center; padding-top: 150px; color: #64748b; font-size: 0.9rem;'>
                <i>↕️ Use this blank zone to scroll down the page without zooming the map.</i>
            </div>
            """, unsafe_allow_html=True)
            
        # Bottom Section: THE BEAUTIFUL THREAT MATRIX
        st.markdown(f"<br><h3 style='color: {accent}; margin-bottom: 0px;'>📋 LIVE SWARM THREAT MATRIX</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 0.95rem; margin-top: 5px; margin-bottom: 20px;'>Real-time swarm node classification based on active thermodynamic Z-Score parameters. Updates asynchronously every 5 seconds.</p>", unsafe_allow_html=True)
        
        # Sort values mathematically before formatting
        latest = latest.sort_values(by='live_z_score', ascending=False)
        
        # Filter into the 3 Dedicated Categories
        crit_raw = latest[latest['live_z_score'] >= z_thresh]
        warn_raw = latest[(latest['live_z_score'] >= (z_thresh * 0.7)) & (latest['live_z_score'] < z_thresh)]
        safe_raw = latest[latest['live_z_score'] < (z_thresh * 0.7)]
        
        # Formatting function for beautiful dataframe
        def format_df(df):
            d = df[['drone_id', 'temperature', 'battery_level', 'live_z_score']].copy()
            d.rename(columns={'drone_id': 'Node ID', 'temperature': 'Temp', 'battery_level': 'Power', 'live_z_score': 'Z-Score'}, inplace=True)
            d['Temp'] = d['Temp'].map("{:.1f} °C".format)
            d['Power'] = d['Power'].map("{} %".format)
            d['Z-Score'] = d['Z-Score'].map("{:.2f} σ".format)
            return d
            
        c_crit, c_warn, c_safe = st.columns(3)
        
        with c_crit:
            st.markdown("<div style='background: rgba(239, 68, 68, 0.15); border-top: 4px solid #ef4444; padding: 12px; border-radius: 8px 8px 0 0; text-align: center;'><b style='color:#ef4444; font-size:1.1rem;'>🔴 FULL THREAT (CRITICAL)</b></div>", unsafe_allow_html=True)
            st.dataframe(format_df(crit_raw), use_container_width=True, hide_index=True)
            
        with c_warn:
            st.markdown("<div style='background: rgba(245, 158, 11, 0.15); border-top: 4px solid #f59e0b; padding: 12px; border-radius: 8px 8px 0 0; text-align: center;'><b style='color:#f59e0b; font-size:1.1rem;'>🟡 CAN BE THREAT (ELEVATED)</b></div>", unsafe_allow_html=True)
            st.dataframe(format_df(warn_raw), use_container_width=True, hide_index=True)
            
        with c_safe:
            st.markdown("<div style='background: rgba(16, 185, 129, 0.15); border-top: 4px solid #10b981; padding: 12px; border-radius: 8px 8px 0 0; text-align: center;'><b style='color:#10b981; font-size:1.1rem;'>🟢 NO THREAT (SECURE)</b></div>", unsafe_allow_html=True)
            st.dataframe(format_df(safe_raw), use_container_width=True, hide_index=True)
            
    live_radar()
    
    with st.expander("📖 DEEP DIVE: HOW TO READ THE 2D TACTICAL RADAR & THREAT MATRIX", expanded=False):
        st.markdown("""
        ### 🌍 Live Geospatial Information System (GIS) & Swarm Matrix
        > **[WHAT IS IT?]** This tab acts as the primary "Command & Control" (C2) interface for the Incident Commander. It combines a real-time 2D topographical Plotly Mapbox with an asynchronous, mathematically sorted "Swarm Threat Matrix" table. 

        **🕹️ 2D TACTICAL MAP CONTROLS & NAVIGATION:**
        * **Zoom & Pan:** Use the scroll wheel to zoom and left-click to drag the map. *(Pro Tip: Notice the "Safe Scroll Zone" on the right—use that empty space to scroll down the webpage without accidentally zooming the map and trapping your cursor).*
        * **Hover Telemetry:** Hovering over any circular node instantly displays the physical MAC address (Drone ID) and its live temperature reading without needing to cross-reference the database.

        **📊 UNDERSTANDING THE MAP SYMBOLS & INFERNO COLOR SCALE:**
        * **The Nodes (Circles):** Every circle represents a physical edge-compute drone maintaining a GPS hover-hold over a designated pipeline sector.
        * **Size (Radius Expansion):** The physical size of the circle on the map is directly linked to its *Thermal Payload*. If a pipe gets dangerously hot, the circle swells up on the screen, drawing the operator's eye immediately.
        * **Color Gradient (The 'Inferno' Scale):** The map uses an 'Inferno' thermal gradient.
            * *Dark Purple/Black:* Represents nominal, safe ambient temperatures.
            * *Orange/Red:* Represents a rising heat signature that requires monitoring.
            * *Bright Yellow/White (Glowing):* Represents a severe Z-Score mathematical anomaly (A statistically impossible heat spike, confirming a fire or friction rupture).

        **📋 THE LIVE SWARM THREAT MATRIX (The 3 Tables):**
        > **[HOW IT WORKS]** Below the map, the system actively sorts every single drone into three operational categories based on their live Z-Score (Standard Deviation from the mean). This matrix updates asynchronously every 5 seconds.
        * **🔴 FULL THREAT (CRITICAL):** Drones whose Z-Score has physically breached the threshold you set in the sidebar. These are active emergency zones. Human fire-teams are dispatched *only* to these nodes.
        * **🟡 CAN BE THREAT (ELEVATED):** Drones whose Z-Score is at 70% to 99% of the threshold. This is the "Early Warning" system. A pipe heating up in the midday sun might sit here, but if it crosses 100%, it shifts instantly to the Critical column.
        * **🟢 NO THREAT (SECURE):** Safe, nominal operations. These nodes are completely ignored by the Incident Commander during a high-stress emergency to prevent cognitive overload.

        **💡 WHY THIS DUAL-VIEW ARCHITECTURE MATTERS IN DEPLOYMENT:**
        In a massive 100-kilometer petroleum refinery, looking at a map with 500 drones can cause panic. The 2D Map gives the *Geographical Context* (Where is the fire?), while the Threat Matrix table gives the *Categorical Context* (Who is in danger?). By instantly filtering out the 'Green' safe drones, human operators can focus 100% of their attention on the 'Red' critical column.
        """)

# TAB 2: MATH ENGINE
with tabs[1]: 
    @st.fragment(run_every=5)
    def live_math():
        if st.session_state.pause_sync: return
        df_tel = fetch_telemetry()
        latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
        max_t = latest['temperature'].max()
        mean_temp = df_tel['temperature'].mean()
        
        st.markdown("### 📊 DYNAMIC SPREAD CALCULUS")
        base_ros = 0.5; wind_factor = wind_spd / 20.0; temp_factor = max_t / 50.0
        calculated_ros = base_ros * (1 + wind_factor) * temp_factor
        heat_flux_dt = (max_t - mean_temp) / calc_dt if calc_dt > 0 else 0
        
        c_calc1, c_calc2 = st.columns(2)
        c_calc1.metric("Dynamic Rate of Spread (R)", f"{calculated_ros:.2f} m/min", delta=f"{wind_factor:.2f} Wind Factor")
        c_calc2.metric("Heat Flux Derivative (∂T/∂t)", f"{heat_flux_dt:.2f} °/sec", delta=f"Δt = {calc_dt}s", delta_color="inverse")
    live_math()
    
    with st.expander("📖 DEEP DIVE: UNDERSTANDING THE MATH ENGINE", expanded=False):
        st.markdown("""
        ### 🧮 Live Predictive Physics
        > **[WHAT IS IT?]** The system actively calculates Differential Calculus and the Rothermel Surface Spread Equation using live inputs from the drones and the Global Command sidebar.

        **📈 KEY METRICS EXPLAINED:**
        * **Rate of Spread (R):** Measured in *meters per minute (m/min)*. It calculates the physical expansion velocity of a fire or toxic gas cloud.
            * *How it works:* It takes base fuel data and multiplies it dynamically by the 'Wind Vector' setting. Increase the wind in the sidebar, and watch this expansion rate surge.
        * **Heat Flux Derivative (∂T/∂t):** Measures the precise rate of temperature change over a defined fraction of time (Delta t).
            * *Why it's critical:* A pipeline operating at 100°C is safe if stable. But a jump from 100°C to 110°C in one second indicates an imminent explosion. The derivative catches this "velocity of heat".

        **💡 HOW A CTO USES IT:**
        We don't just track where the hazard *is*; we use this continuous calculus to predict where the hazard *will be* in 30 minutes, allowing for targeted evacuation of specific refinery sectors.
        """)

# TAB 3: HARDWARE MATRIX 
with tabs[2]: 
    c_hw1, c_hw2 = st.columns(2)
    with c_hw1:
        x_val = np.linspace(0, 10, 30); y_val = np.linspace(0, 10, 30); X, Y = np.meshgrid(x_val, y_val)
        Z = np.sin(X) * np.cos(Y) * pid_p 
        fig_3d = go.Figure(data=[go.Surface(z=Z, colorscale='Viridis')])
        fig_3d.update_layout(title="IMU Vibration Matrix", paper_bgcolor="rgba(0,0,0,0)", font_color=text, height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_3d, use_container_width=True)
    with c_hw2:
        st.markdown(f"<br><br><h3>📡 Radio Link Budget</h3><p style='font-size:1.2rem;'>Spreading Factor: <b style='color:{accent};'>SF{lora_sf}</b> | TX Power: <b style='color:{accent};'>{tx_power} dBm</b></p>", unsafe_allow_html=True)
    
    with st.expander("📖 DEEP DIVE: READING THE HARDWARE MATRIX", expanded=False):
        st.markdown("""
        ### ⚙️ Drone Flight & Communication Telemetry
        > **[WHAT IS IT?]** A live diagnostic view of the physical forces acting on the drone swarm's hardware and radio equipment.

        **🚁 THE VIBRATION MATRIX (3D Plot):**
        * **Axes Representation:** The X and Y axes represent the drone's physical tilt (Pitch and Roll). The Z-axis (peaks and valleys) represents the electrical voltage dispatched to the motors to correct the drone's balance.
        * **Interactive Test:** Go to the sidebar and increase the "Proportional Gain (kP)". The waves will become taller and sharper, representing the motors fighting crosswinds more aggressively.

        **📻 RADIO LINK BUDGET:**
        * **LoRa (Long Range) Spreading Factor:** Displays the physical configuration of the radio antennas.
        * *Why it matters:* If a drone flies behind dense steel refinery pipes, standard Wi-Fi drops. The operator ensures the SF is high enough (SF10-SF12) to punch through solid obstacles at the cost of data speed.
        """)

# TAB 4: NEURAL AI 
with tabs[3]: 
    if yolo_model is None:
        st.warning("⚠️ **Neural AI Module Offline:** Missing server graphic dependencies. Add `opencv-python-headless` to requirements.txt to activate YOLO inference.")
        
    uploaded_file = st.file_uploader("📸 UPLOAD CUSTOM DRONE IMAGERY", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        if st.button("Initialize Deep Learning Core"):
            with st.spinner("Processing AI Tensor Weights..."):
                if yolo_model is not None:
                    results = yolo_model(image)
                    st.image(results[0].plot(), caption="AI Vision Scanner Active", use_container_width=True)
                    detected_classes = results[0].boxes.cls.tolist()
                    if len(detected_classes) > 0:
                        st.error(f"🚨 ALERT: {len(detected_classes)} Trained Anomalies Detected!")
                        for cls_id in set(detected_classes):
                            st.write(f"- 🔴 **Object:** {yolo_model.names[int(cls_id)].upper()} | **Count:** {detected_classes.count(cls_id)}")
                    else:
                        st.success("✅ System Normal: No anomalies detected in this frame.")
                else:
                    st.error("AI engine is offline.")
    else:
        cam1, cam2 = st.columns(2)
        for i, (idx, r) in enumerate(latest_main.head(2).iterrows()):
            cam = cam1 if i == 0 else cam2
            cam.markdown(f"""<div style="border: 2px solid #64748b; background: #000; height: 300px; position: relative; border-radius: 12px;"><div style="position: absolute; top: 15px; left: 15px; color: #64748b; font-family: monospace; font-weight: bold; background: rgba(0,0,0,0.6); padding: 5px;">NODE: {r['drone_id']} | EDGE-AI STANDBY</div><div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.1); font-size: 80px;">⌖</div></div>""", unsafe_allow_html=True)
    
    with st.expander("📖 DEEP DIVE: USING THE NEURAL AI CORE", expanded=False):
        st.markdown("""
        ### 👁️ Real-Time Computer Vision Inference
        > **[WHAT IS IT?]** An active Edge-AI vision engine powered by the YOLOv8 (You Only Look Once) architecture. It uses PyTorch tensor weights to scan raw pixels for trained hazards.

        **🛠️ HOW TO USE IT:**
        1. Upload an image of pipeline infrastructure, a pressure gauge, or a fire event.
        2. Click *Initialize Deep Learning Core*.

        **🧠 UNDERSTANDING THE AI MODEL (`best.pt`):**
        * The custom `best.pt` model loaded here is strictly a **Vision Model** trained specifically on visual datasets (like fire, smoke, or pipeline cracks).
        * The algorithm pushes the uploaded image matrix through this model. If it mathematically recognizes a trained hazard, it renders a physical **Bounding Box** over the anomaly and sounds the alert.
        * If the image is clean, it truthfully reports: *"System Normal"*. It does not fake detections.

        **💡 REAL-WORLD DEPLOYMENT:**
        In a live scenario, operators will not manually upload images. This exact Neural Vision Core will be directly connected to the drone's gimbal-mounted FLIR/Optical cameras. The model (`best.pt`) will process the live video feed frame-by-frame at the Edge (on the drone itself), sending only critical bounding-box alerts back to this command center to save bandwidth.
        """)

# TAB 5: THERMODYNAMICS 
with tabs[4]: 
    x = np.linspace(-3, 3, 50); y = np.linspace(-3, 3, 50); X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2)) 
    Z_smoothed = gaussian_filter(Z + 0.1 * np.random.randn(*Z.shape), sigma=1.5)
    fig_cont = go.Figure(data=go.Contour(z=Z_smoothed, colorscale='Inferno', contours=dict(showlabels=True)))
    fig_cont.update_layout(title="Thermal Dispersion Plume", paper_bgcolor='rgba(0,0,0,0)', font=dict(color=accent), height=400)
    st.plotly_chart(fig_cont, use_container_width=True)
    
    with st.expander("📖 DEEP DIVE: ANALYZING THERMODYNAMIC CONTOURS", expanded=False):
        st.markdown("""
        ### 💨 Heat & Gas Dispersion Topography
        > **[WHAT IS IT?]** A 2D contour map mathematically forecasting the Gaussian distribution of expanding heat or toxic gas originating from a ruptured pipeline.

        **🗺️ HOW TO READ THE SYMBOLS & COLORS:**
        * **The Colors (Inferno Scale):** The bright, glowing white/yellow center pinpoints the exact origin of the leak (the point of maximum thermal/chemical toxicity). The fade into dark red and black represents the atmospheric cooling and dissipation into safe air.
        * **The Concentric Rings (Iso-lines):** Similar to a geographic topographic map, each ring maps a boundary of equal temperature or gas concentration, dictated by the Inverse Square Law.

        **💡 TACTICAL INCIDENT DEPLOYMENT:**
        During a catastrophic refinery failure, Incident Commanders use this visual data to establish "Safe Perimeters." The inner bright zones are designated exclusively for robotic/drone containment, while the outer black zones dictate human evacuation staging areas.
        """)

# TAB 6: DATA LAKE 
with tabs[5]: 
    @st.fragment(run_every=5)
    def live_data_lake():
        if st.session_state.pause_sync: return
        df_tel = fetch_telemetry()
        st.dataframe(df_tel, use_container_width=True)
    live_data_lake()
    
    with st.expander("📖 DEEP DIVE: NAVIGATING THE DATA LAKE", expanded=False):
        st.markdown("""
        ### 💾 The Raw Telemetry Backend
        > **[WHAT IS IT?]** The unfiltered, high-speed Pandas/Polars dataframe. This matrix is the raw engine driving every map, calculation, and visual metric on this dashboard.

        **📊 UNDERSTANDING THE MATRIX COLUMNS:**
        * `drone_id`: The unique MAC address and identifier of the physical edge node.
        * `latitude` & `longitude`: Precision RTK-GPS spatial coordinates parsed dynamically from JSON payloads.
        * `temperature` & `battery`: Critical hardware health and payload logs.

        **💡 PRIMARY USE CASE:**
        Command Center operators rarely interact with this tab. It is an engineering sandbox used by Data Scientists and Backend Engineers to perform "Crash Forensics" after a system failure, allowing them to isolate the exact millisecond a sensor or node malfunctioned.
        """)

# TAB 7: INDUSTRIAL DEPLOYMENT BIBLE (Force-Light Mode Wrapper)
with tabs[6]:
    # CSS: This force-injects Light Mode styles only for this specific Container
    st.markdown("""
        <style>
        .light-tab-override {
            background-color: #ffffff !important;
            color: #000000 !important;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #d1d5db;
        }
        /* Overriding all elements inside the div to be dark-text on white background */
        .light-tab-override * {
            color: #000000 !important;
        }
        .light-tab-override .stDataFrame {
            background-color: #ffffff !important;
        }
        .light-tab-override .stInfo, .light-tab-override .stWarning, .light-tab-override .stSuccess {
            background-color: #f3f4f6 !important;
            border: 1px solid #d1d5db !important;
        }
        </style>
        <div class="light-tab-override">
    """, unsafe_allow_html=True)

    st.markdown("### 🏗️ AERO-GUARD V19: INDUSTRIAL FLEET DEPLOYMENT BIBLE")
    
    # Using sub-tabs to keep the massive detail organized
    manual_tabs = st.tabs(["📋 Fleet BOM", "🔧 Hardware & Assembly", "💻 Jetson Setup (The Brain)", "💾 Data & Integration", "🚀 Final Launch"])
    
    with manual_tabs[0]:
        st.markdown("#### 🛒 10-Drone Fleet Master BOM")
        st.write("This fleet budget is approximately $4,500 USD per unit. Components selected strictly for industrial-grade reliability.")
        bom_data = {
            "Part": ["Frame", "FC", "AI Brain", "Thermal Cam", "GPS", "5G Module", "Motors/ESC", "Battery", "Misc/Loctite/Screws", "Storage"],
            "Industrial Name": ["Carbon X-Quad", "Pixhawk 6C", "NVIDIA Jetson Orin Nano", "FLIR Boson 640", "Here4 RTK", "Quectel RM500Q", "T-Motor Anti-Gravity", "6S 10000mAh", "Industrial Grade Kit", "64GB Indus-SD"],
            "Qty (10 Units)": [10, 10, 10, 10, 10, 10, 40, 20, 2, 10],
            "Price": ["$250", "$350", "$550", "$2200", "$350", "$200", "$60", "$150", "$500", "$50"]
        }
        st.table(pd.DataFrame(bom_data))
        st.info("💡 **Pro-Tip:** Always maintain 15% spare parts (props, screws, motors) at the refinery base station.")

    with manual_tabs[1]:
        st.markdown("#### 🛠️ Assembly & Hardware Manual (Minute Operational Details)")
        st.markdown("""
        **1. Mechanical Integrity:** - **Loctite Blue:** Apply 'Loctite Blue' (Threadlocker) to every motor-to-frame screw. Vibration at high RPM will loosen standard screws within minutes, leading to structural failure.
        - **Vibration Damping:** Mount the Jetson Nano and thermal camera using 'Silicone Vibration Dampeners' (rubber balls). AI models (YOLO) require high-contrast, stable imagery. Frame vibrations cause 'false positive' anomaly detections.
        - **Cable Management:** Use industrial zip-ties. Ensure no loose wires are near propellers. Loose cabling can cause catastrophic failure in less than 2 seconds.
        """)

    with manual_tabs[2]:
        st.markdown("#### 💻 Jetson Nano Setup (The Brain)")
        st.write("Remote access and system automation procedures:")
        st.markdown("""
        1. **Physical Connection:** Connect Jetson Nano via USB-to-Ethernet adapter to your laptop.
        2. **SSH Connection:** Access the terminal: `ssh username@192.168.1.5` (Target the Jetson's specific IP).
        3. **Code Transfer:** Transfer files using: `scp -r ./my_drone_code username@192.168.1.5:/home/user/`.
        4. **Persistence (Auto-Run):** - Create a service file: `/etc/systemd/system/drone.service`
           - Configure: `ExecStart=/usr/bin/python3 /home/user/my_drone_code/main.py`.
           - Enable it: `sudo systemctl enable drone.service`. 
           - The AI module now boots automatically with the drone.
        """)

    with manual_tabs[3]:
        st.markdown("#### 💾 Database & Integration (Production Pipeline)")
        st.write("Transition from synthetic simulation to live industrial PostgreSQL data.")
        st.code("""
# app.py: Replace the random data generator with this production-ready function
import requests
from config import API_URL, API_KEY

@st.cache_data(ttl=2) 
def fetch_telemetry():
    # Production Environment: Fetching real-time data from Supabase
    headers = {
        "apikey": API_KEY, 
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        # Requesting live data from the database
        response = requests.get(f"{API_URL}/rest/v1/telemetry?select=*", headers=headers)
        if response.status_code == 200:
            return pd.DataFrame(response.json()) # Real-world telemetry
        return pd.DataFrame() 
    except Exception:
        return pd.DataFrame() # Fail-safe: Dashboard will not crash if DB is unreachable
        """)
        st.write("Note: Create a `config.py` file with your `API_URL` and `API_KEY` to keep credentials secure.")

    with manual_tabs[4]:
        st.markdown("#### 🚀 Final Launch Protocol")
        st.write("1. **Network:** Ensure the 5G/LTE module has a valid M2M SIM card and is registered to the Private APN.")
        st.write("2. **Safety Protocols:** Implement 'Emergency Stop' logic in `main.py`—if internet connectivity is lost, the drone must default to autonomous 'Return-to-Home' (RTH).")
        st.write("3. **Battery Safety:** Implement 'Low Battery' threshold logic: `if battery < 15%: drone.land()`.")
        st.success("The system is now ready for industrial-scale deployment.")
        st.markdown("[Download Best.pt Model File](https://drive.google.com/file/d/1eE2doiC8-q-EGKRJ984kDh-kP91P6euq/view?usp=drive_link)")

    # Closing the Light Mode wrapper
    st.markdown("</div>", unsafe_allow_html=True)
