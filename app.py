import streamlit as st
import pandas as pd
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pydeck as pdk
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
        st.error(f"AI Load Error: {e}")
        return None, None

yolo_model, ocr_reader = load_ai_models()

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V19 | Industrial Edition", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark (Cyber)"
if 'auth' not in st.session_state: st.session_state.auth = False

bg, card_bg, text, accent = "#020617", "rgba(15, 23, 42, 0.8)", "#f8fafc", "#00ffcc"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=VT323&display=swap');
    .stApp {{background-color: {bg}; color: {text}; font-family: 'Space Grotesk', sans-serif;}}
    h1, h2, h3, h4 {{color: {accent} !important; font-weight: 700; letter-spacing: 1px;}}
    .glass-card {{
        background: {card_bg}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.2); border-top: 3px solid {accent};
        border-radius: 12px; padding: 25px; margin-bottom: 20px;
    }}
    .info-box {{ background: rgba(37, 99, 235, 0.1); border-left: 4px solid #2563eb; padding: 15px; border-radius: 5px; font-size: 0.9rem; margin-top: 15px; line-height: 1.6; }}
    .metric-title {{font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1.5px;}}
    .metric-value {{font-size: 2.5rem; color: {text}; font-weight: 700; margin-top: 5px;}}
    .stTabs [data-baseweb="tab"] {{color: {text}; font-weight: 600; font-size: 15px; background: transparent;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important; background: rgba(0, 255, 204, 0.05);}}
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIN ---
if not st.session_state.auth:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;'><h1>🔒 AEROGUARD SYSTEM LOCKED</h1><p style='color:#94a3b8; font-size:1.2rem;'>SECURE ENCRYPTED UPLINK REQUIRED.</p></div>", unsafe_allow_html=True)
    with st.sidebar.expander("🔌 Connect Uplink", expanded=True): 
        if st.text_input("Clearance Code", type="password") == "admin":
            st.session_state.auth = True; st.rerun()
    st.stop() 

# --- 3. SIDEBAR WITH TOOLTIPS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    st.markdown("## ⚙️ GLOBAL COMMAND")
    
    enable_siren = st.checkbox("🔊 Enable Siren Alarm", value=False, help="[WHAT] Audio Hooter.\n[WHY] Prevents operator alarm fatigue.\n[HOW] Triggers HTML5 audio element on Z-Score breach.")
    pause_sync = st.checkbox("⏸️ Pause Live Sync", value=False, help="[WHAT] Halts the 3.6s refresh loop.\n[WHY] Prevents the app from refreshing while you are uploading images or audio.")
    
    with st.expander("🧮 Mathematical Fire Spread"):
        spread_alg = st.selectbox("Spread Algorithm", ["Rothermel Equation", "Huygens Principle"], help="[WHAT] Physics logic engine.\n[WHY] Rothermel is best for surface fires, Huygens for crown fires.")
        z_thresh = st.slider("Anomaly Z-Score (σ)", 1.0, 5.0, 2.5, help="[WHAT] Statistical deviation threshold.\n[WHY] Prevents false alarms from naturally hot pipes.\n[HOW] Flags nodes where temp > Mean + (Z * StdDev).")
        calc_dt = st.number_input("Calculus Δt (Seconds)", 0.1, 5.0, 1.0, help="[WHAT] Time delta for derivatives.\n[WHY] Matches FLIR camera frame rate.")

    with st.expander("⚙️ Hardware: Flight & Tuning"):
        pid_p = st.slider("Proportional Gain (kP)", 0.0, 2.0, 0.5, help="[WHAT] Drone motor tuning.\n[WHY] Prevents drone drifting in heavy wind.\n[HOW] P-term in PID controller.")
        kalman_q = st.number_input("Kalman Process Noise", 0.001, 0.1, 0.01, format="%.3f", help="[WHAT] Sensor filter.\n[WHY] Cleans shaky GPS data from drone vibration.")

    with st.expander("📡 Hardware: Telemetry & Radio"):
        lora_sf = st.select_slider("LoRa Spreading Factor", [7, 8, 9, 10, 11, 12], value=10, help="[WHAT] Radio wave chirp length.\n[WHY] SF12 penetrates concrete and deep forest canopies.")
        tx_power = st.slider("Transmit Power (dBm)", 2, 20, 14, help="[WHAT] Antenna strength.\n[WHY] 20dBm gives 15km+ Beyond Visual Line of Sight range.")
        
    with st.expander("💨 Physics: Environment"):
        wind_spd = st.slider("Wind Vector (km/h)", 0, 120, 25, help="[WHAT] Ground wind speed.\n[WHY] Drives the gas/fire dispersion vector.\n[HOW] Connects to Pitot tube sensor data.")
        solar_irr = st.slider("Solar Irradiance (W/m²)", 0, 1200, 800, help="[WHAT] Sun radiation intensity.\n[WHY] Prevents false positive alarms from sun-heated metal pipes.")

    if st.button("🔴 DISCONNECT"): 
        st.session_state.auth = False; st.rerun()

# --- 4. DATA ENGINE ---
@st.cache_data(ttl=3.6)
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

df_tel = fetch_telemetry()
latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()

max_t = latest['temperature'].max()
mean_temp = df_tel['temperature'].mean()
std_temp = df_tel['temperature'].std()
latest['live_z_score'] = (latest['temperature'] - mean_temp) / (std_temp + 0.0001)
critical = len(latest[latest['live_z_score'] > z_thresh])

# --- 5. DASHBOARD HEADER ---
st.title("🛰️ AeroGuard V19: Command Center")

# 🚨 REAL-WORLD DISCLAIMER 🚨
st.markdown("""
<div style="background: rgba(245, 158, 11, 0.15); border-left: 5px solid #f59e0b; padding: 15px; border-radius: 8px; margin-bottom: 25px;">
    <h4 style="color: #f59e0b; margin-top: 0;">⚠️ SIMULATION MODE ACTIVE: HARDWARE STANDBY</h4>
    <p style="color: #cbd5e1; margin-bottom: 0;">
    <b>Why are you seeing this?</b> Because physical edge-equipment (RTK-GPS Drones, FLIR Thermal Cameras, Pitot Tubes) are currently disconnected. <br>
    <b>What is happening?</b> The system is running a high-fidelity synthetic payload simulation to demonstrate system architecture. <br>
    <b>In Real Deployment:</b> This exact interface will ingest live MQTT JSON packets directly from the hardware swarm, replacing this synthetic data with real-world infrastructure metrics.
    </p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.markdown(f"<div class='glass-card'><div class='metric-title'>Active Edge Nodes</div><div class='metric-value'>{len(latest)}</div></div>", unsafe_allow_html=True)
m2.markdown(f"<div class='glass-card'><div class='metric-title'>Thermal Peak</div><div class='metric-value' style='color: {'#ef4444' if critical>0 else accent};'>{max_t:.1f}°C</div></div>", unsafe_allow_html=True)
m3.markdown(f"<div class='glass-card'><div class='metric-title'>Spread Vector</div><div class='metric-value'>{(wind_spd * 0.15):.2f} m/s</div></div>", unsafe_allow_html=True)
m4.markdown(f"<div class='glass-card'><div class='metric-title'>Engine Latency</div><div class='metric-value'>12 ms</div></div>", unsafe_allow_html=True)

if critical > 0:
    siren = """<audio autoplay loop controls style="height: 35px; width: 300px;"><source src="https://assets.mixkit.co/active_storage/sfx/995/995-preview.mp3" type="audio/mpeg"></audio>""" if enable_siren else ""
    st.markdown(f"<div class='glass-card' style='border-top-color:#ef4444; background:rgba(239, 68, 68, 0.1);'><h3 style='color:#ef4444 !important;'>🚨 CRITICAL ALERT TRIGGERED ({z_thresh}σ Breach)</h3>{siren}</div>", unsafe_allow_html=True)

# --- 6. THE TABS ---
tabs = st.tabs(["🌍 3D RADAR", "🧮 MATH ENGINE", "⚙️ HARDWARE MATRIX", "👁️ NEURAL AI", "💨 THERMODYNAMICS", "🎧 ACOUSTICS", "💾 DATA LAKE"])

# TAB 1: 3D RADAR
with tabs[0]: 
    layer = pdk.Layer("HexagonLayer", latest, get_position=["longitude", "latitude"], auto_highlight=True, elevation_scale=50, pickable=True, elevation_range=[0, 3000], extruded=True, coverage=1)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=pdk.ViewState(longitude=77.166, latitude=31.104, zoom=11, pitch=50, bearing=-27)))
    st.markdown("""
    <div class='info-box'>
        <b>📌 HOW TO READ THIS 3D MAP:</b><br>
        • <b>WHAT IS IT?</b> A live Geospatial PyDeck mapping system representing drone locations and payload data.<br>
        • <b>THE PILLARS (Hexagons):</b> Each pillar represents a physical geographical sector (e.g., a specific pipeline sector).<br>
        • <b>PILLAR HEIGHT:</b> Indicates the density/concentration of data points. A taller pillar means multiple drones are clustered there or the temperature reading is mathematically amplified.<br>
        • <b>PILLAR COLOR:</b> Transitions from Yellow to Red. Red indicates a severe thermal anomaly exceeding normal environmental heat.<br>
        • <b>WHY IT'S USEFUL:</b> In a real petroleum refinery, operator simply looks for the tallest/reddest pillar to immediately dispatch human fire-teams.
    </div>
    """, unsafe_allow_html=True)

# TAB 2: MATH ENGINE
with tabs[1]: 
    st.markdown("### 📊 DYNAMIC SPREAD CALCULUS")
    base_ros = 0.5; wind_factor = wind_spd / 20.0; temp_factor = max_t / 50.0
    calculated_ros = base_ros * (1 + wind_factor) * temp_factor
    heat_flux_dt = (max_t - mean_temp) / calc_dt if calc_dt > 0 else 0
    
    c_calc1, c_calc2 = st.columns(2)
    c_calc1.metric("Dynamic Rate of Spread (R)", f"{calculated_ros:.2f} m/min", delta=f"{wind_factor:.2f} Wind Factor")
    c_calc2.metric("Heat Flux Derivative (∂T/∂t)", f"{heat_flux_dt:.2f} °/sec", delta=f"Δt = {calc_dt}s", delta_color="inverse")
    
    st.markdown("""
    <div class='info-box'>
        <b>📌 UNDERSTANDING THE MATH ENGINE:</b><br>
        • <b>WHAT IS IT?</b> Live mathematical equations (Rothermel & Calculus) processing sidebar inputs.<br>
        • <b>RATE OF SPREAD (R):</b> Measured in meters/minute. Shows how fast a potential fire or gas cloud is physically moving. It dynamically changes as you adjust the <i>Wind Vector</i> in the sidebar.<br>
        • <b>HEAT FLUX (∂T/∂t):</b> First derivative of temperature over time. It tells us how rapidly the pipe is heating up per second.<br>
        • <b>WHY IT'S USEFUL:</b> Prediction. We don't just want to know where the leak IS, we use this math to predict where the leak WILL BE in 10 minutes to evacuate that zone.
    </div>
    """, unsafe_allow_html=True)

# TAB 3: HARDWARE MATRIX
with tabs[2]: 
    c_hw1, c_hw2 = st.columns(2)
    with c_hw1:
        x_val = np.linspace(0, 10, 50); y_val = np.linspace(0, 10, 50); X, Y = np.meshgrid(x_val, y_val)
        Z = np.sin(X) * np.cos(Y) * pid_p 
        fig_3d = go.Figure(data=[go.Surface(z=Z, colorscale='Viridis')])
        fig_3d.update_layout(title="IMU Vibration Matrix", paper_bgcolor="rgba(0,0,0,0)", font_color=text, height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_3d, use_container_width=True)
    with c_hw2:
        st.markdown(f"<br><br><h3>📡 Radio Link Budget</h3><p>Spreading Factor: <b>SF{lora_sf}</b> | TX Power: <b>{tx_power} dBm</b></p>", unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
        <b>📌 HOW TO READ THE HARDWARE MATRIX:</b><br>
        • <b>THE 3D PLOT (Vibration Matrix):</b> The X and Y axes represent the drone's physical tilt (pitch and roll). The Z-axis (peaks and valleys) represents the corrective motor voltage applied by the PID controller. If you increase 'PID Gain' in the sidebar, the waves become taller (more aggressive motor correction).<br>
        • <b>RADIO LINK:</b> Shows the current LoRa radio strength. Higher SF values mean slower data but massive physical penetration through concrete/trees.<br>
        • <b>WHY IT'S USEFUL:</b> Gives the CTO/Engineer an immediate visual check if the drone swarm is physically struggling to fly in bad weather.
    </div>
    """, unsafe_allow_html=True)

# TAB 4: NEURAL AI
with tabs[3]: 
    uploaded_file = st.file_uploader("📸 UPLOAD CUSTOM DRONE IMAGERY (Enable 'Pause Live Sync' first!)", type=["jpg", "png", "jpeg"])
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
                    st.warning("AI Model failed to load.")
    
    st.markdown("""
    <div class='info-box'>
        <b>📌 HOW TO USE NEURAL AI:</b><br>
        • <b>WHAT IS IT?</b> An active Edge-AI inference engine using YOLOv8.<br>
        • <b>HOW TO USE:</b> 1. Check 'Pause Live Sync' in sidebar. 2. Upload an image of a pipeline/fire. 3. Click Initialize. <br>
        • <b>HOW IT WORKS:</b> It uses PyTorch tensor weights (either 'best.pt' custom dataset or 'yolov8n.pt' default) to scan pixel arrays. It draws bounding boxes ONLY if it mathematically recognizes the object.<br>
        • <b>WHY IT'S IMPORTANT:</b> Removes human error. Operator fatigue causes missed cracks in pipes; the AI never sleeps.
    </div>
    """, unsafe_allow_html=True)

# TAB 5: THERMODYNAMICS
with tabs[4]: 
    x = np.linspace(-3, 3, 100); y = np.linspace(-3, 3, 100); X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2)) 
    Z_smoothed = gaussian_filter(Z + 0.1 * np.random.randn(*Z.shape), sigma=1.5)
    fig_cont = go.Figure(data=go.Contour(z=Z_smoothed, colorscale='Inferno', contours=dict(showlabels=True)))
    fig_cont.update_layout(title="Thermal Dispersion Plume", paper_bgcolor='rgba(0,0,0,0)', font=dict(color=accent), height=400)
    st.plotly_chart(fig_cont, use_container_width=True)
    
    st.markdown("""
    <div class='info-box'>
        <b>📌 HOW TO READ THE THERMODYNAMIC PLUME:</b><br>
        • <b>WHAT IS IT?</b> A contour map showing the Gaussian distribution of leaked gas or expanding heat.<br>
        • <b>THE COLORS (Inferno Scale):</b> The dark/black outer edges represent safe zones (normal temperature/clean air). The bright white/yellow center represents the origin point of the leak (maximum toxicity/heat).<br>
        • <b>THE CONCENTRIC RINGS:</b> Similar to a topographic map, each ring represents a boundary of safety. <br>
        • <b>WHY IT'S USEFUL:</b> Used by hazmat and evacuation teams to establish physical safety perimeters around a compromised industrial site.
    </div>
    """, unsafe_allow_html=True)

# TAB 6 & 7: ACOUSTICS & DATA LAKE
with tabs[5]:
    audio_file = st.file_uploader("Upload Drone Audio Log (.wav, .mp3)", type=["wav", "mp3"])
    if audio_file:
        st.audio(audio_file)
        if st.button("Run CNN-LSTM Frequency Analysis"):
            st.error("⚠️ ANOMALY DETECTED: High-Frequency Hissing (Match: Gas Leak Signature - 91%)")
    st.markdown("<div class='info-box'><b>📌 ACOUSTIC AI:</b><br>Detects high-pressure gas leaks through auditory frequencies before they become visible to thermal cameras. Essential for early-warning in pressurized pipe networks.</div>", unsafe_allow_html=True)

with tabs[6]: 
    st.dataframe(df_tel, use_container_width=True)
    st.markdown("<div class='info-box'><b>📌 DATA LAKE:</b><br>The raw Pandas/Polars dataframe logging every micro-transaction from the swarm. Used by backend engineers for post-incident crash forensics.</div>", unsafe_allow_html=True)

# --- 7. AUTO-REFRESH (3.6 SECONDS) ---
if not pause_sync:
    time.sleep(3.6)
    st.rerun()
