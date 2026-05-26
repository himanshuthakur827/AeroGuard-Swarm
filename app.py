import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V13 | Hardware Matrix", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 2. MULTI-LANGUAGE DICTIONARY ---
i18n = {
    "EN": {"title": "🛰️ AeroGuard V13: Hardware Integration & Swarm Nexus", "tabs": ["🌍 GLOBAL RADAR", "🧮 MATH CORE", "⚙️ REAL HARDWARE (NEW)", "👁️ NEURAL VISION", "💨 ENV PHYSICS", "💾 DATA LAKE"]},
    "RU": {"title": "🛰️ AeroGuard V13: Аппаратная Интеграция", "tabs": ["🌍 РАДАР", "🧮 МАТЕМАТИКА", "⚙️ ОБОРУДОВАНИЕ", "👁️ ЗРЕНИЕ", "💨 ФИЗИКА", "💾 ДАННЫЕ"]}
}
L = st.session_state.lang
T = st.session_state.theme

# --- 3. DYNAMIC CSS WITH 3D ANIMATIONS & TRANSITIONS ---
bg_color, panel_bg, text_col, accent, border = ("#020617", "#0f172a", "#f8fafc", "#00ffcc", "#1e293b") if T == "Dark" else ("#f1f5f9", "#ffffff", "#0f172a", "#2563eb", "#cbd5e1")
map_style = "carto-darkmatter" if T == "Dark" else "open-street-map"

st.markdown(f"""
    <style>
    .stApp {{background-color: {bg_color}; color: {text_col}; font-family: 'Segoe UI', sans-serif;}}
    h1, h2, h3 {{color: {accent} !important; font-weight: 800;}}
    
    /* ANIMATIONS */
    @keyframes slideUp {{ from {{opacity: 0; transform: translateY(20px);}} to {{opacity: 1; transform: translateY(0);}} }}
    @keyframes pulseGlow {{ 0% {{box-shadow: 0 0 5px {accent}40;}} 50% {{box-shadow: 0 0 20px {accent};}} 100% {{box-shadow: 0 0 5px {accent}40;}} }}
    @keyframes spin3D {{ from {{transform: rotateY(0deg);}} to {{transform: rotateY(360deg);}} }}
    
    /* UI ELEMENTS */
    .animated-card {{
        background: {panel_bg}; border: 1px solid {border}; border-top: 3px solid {accent};
        border-radius: 12px; padding: 20px; animation: slideUp 0.6s ease-out forwards;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .animated-card:hover {{ transform: translateY(-5px); animation: pulseGlow 2s infinite; }}
    
    .status-orb {{
        width: 15px; height: 15px; background-color: #ef4444; border-radius: 50%;
        display: inline-block; animation: pulseGlow 1.5s infinite;
    }}
    
    .stTabs [data-baseweb="tab"] {{color: {text_col}; font-weight: 600; transition: color 0.3s;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SECURE LOGIN ---
if not st.session_state.auth:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown(f"<div class='animated-card' style='text-align:center;'><h2>AEROGUARD GATEWAY</h2><p>Hardware Integration Node</p></div>", unsafe_allow_html=True)
        if st.button("AUTHENTICATE SYSTEM", use_container_width=True): st.session_state.auth = True; st.rerun()
    st.stop()

# --- 5. SIDEBAR WITH DEEP-DIVE TOOLTIPS & 15+ HARDWARE OPTIONS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    st.markdown("## ⚙️ COMMAND OVERRIDE")
    
    with st.expander("🌐 UI & Region Settings"):
        st.session_state.lang = st.selectbox("Language", ["EN", "RU"], index=["EN", "RU"].index(L))
        st.session_state.theme = st.selectbox("UI Theme", ["Dark", "Light"], index=["Dark", "Light"].index(T))
    
    with st.expander("🧮 Wildfire Math & Physics"):
        spread_model = st.selectbox("Fire Algorithm", ["Rothermel", "Cellular Automata"], help="[WHAT] Selects the physics engine. [HOW] Uses partial differential equations to predict thermal expansion. [DEPLOY] Used to predict where the swarm should pre-position.")
        calc_dt = st.number_input("Calculus Δt", 0.1, 5.0, 1.0, help="[WHAT] Time delta for derivatives. [HOW] Denominator in dT/dt limit equations. [DEPLOY] Matches the refresh rate of your real thermal camera.")
        wind_speed = st.slider("Wind Vector (km/h)", 0, 100, 25, help="[WHAT] Mid-flame wind speed. [HOW] Directly multiplies the forward rate of spread. [DEPLOY] Will be fed live from the drone's onboard Pitot tube anemometer.")

    # NEW: THE 15+ REAL HARDWARE SENSOR OPTIONS
    with st.expander("⚙️ 1. FLIGHT CONTROLLER (PID)"):
        st.markdown("<small style='color:gray;'>Pixhawk/Ardupilot Tuning</small>", unsafe_allow_html=True)
        pid_p = st.slider("Proportional Gain (kP)", 0.0, 2.0, 0.5, help="[WHAT] Core stabilization. [HOW] Calculates error = target_angle - current_angle. [DEPLOY] High P makes the real drone snap back fast, too high causes oscillations.")
        pid_i = st.slider("Integral Gain (kI)", 0.0, 1.0, 0.1, help="[WHAT] Overcomes steady-state errors (like constant wind). [HOW] Integrates error over time (Sum of errors * dt). [DEPLOY] Crucial for Siberian/Himalayan crosswinds.")
        pid_d = st.slider("Derivative Gain (kD)", 0.0, 0.5, 0.05, help="[WHAT] Dampens the movement. [HOW] Calculates the rate of change of the error (dError/dt). [DEPLOY] Stops the drone from overshooting its target GPS waypoint.")
        mag_decl = st.number_input("Magnetic Declination (°)", -180.0, 180.0, 4.5, help="[WHAT] Compass correction. [HOW] Offset between True North and Magnetic North. [DEPLOY] Must be updated based on deployment coordinates (India vs Russia).")
        geofence = st.slider("Geofence Radius (m)", 100, 5000, 1500, help="[WHAT] Virtual cage. [HOW] RTL (Return to Launch) triggered if (x² + y²)^(1/2) > R. [DEPLOY] Prevents flyaways if LoRaWAN signal is lost.")

    with st.expander("📡 2. TELEMETRY & RADIO (LoRa)"):
        st.markdown("<small style='color:gray;'>LoRaWAN / MQTT Comms</small>", unsafe_allow_html=True)
        lora_sf = st.select_slider("Spreading Factor (SF)", [7, 8, 9, 10, 11, 12], value=10, help="[WHAT] Radio modulation. [HOW] Higher SF = longer range but slower data rate (chirp duration). [DEPLOY] Use SF12 for deep forests, SF7 for urban.")
        mqtt_qos = st.selectbox("MQTT QoS Level", [0, 1, 2], index=1, help="[WHAT] Message guarantee. [HOW] QoS 0 (At most once), QoS 1 (At least once), QoS 2 (Exactly once). [DEPLOY] QoS 1 ensures fire alerts are never missed over bad networks.")
        baud_rate = st.selectbox("Serial Baud Rate", [9600, 57600, 115200], index=2, help="[WHAT] Hardware comms speed. [HOW] Bits per second between Raspberry Pi and Pixhawk. [DEPLOY] 115200 required for high-frequency telemetry logging.")
        antenna_gain = st.number_input("Antenna Gain (dBi)", 1.0, 12.0, 3.0, help="[WHAT] Radio signal focus. [HOW] Calculates Link Budget = Tx_Power + Tx_Gain - Path_Loss + Rx_Gain. [DEPLOY] Use 8dBi directional antennas at the base station.")

    with st.expander("👁️ 3. SENSORS (FLIR & IMU)"):
        st.markdown("<small style='color:gray;'>Thermal & Navigation</small>", unsafe_allow_html=True)
        flir_emis = st.slider("Thermal Emissivity (ε)", 0.1, 1.0, 0.95, help="[WHAT] Surface radiation efficiency. [HOW] Stefan-Boltzmann law modifier (E = εσT^4). [DEPLOY] 0.95 for trees/organic matter, lower it if scanning metal pipelines.")
        kalman_q = st.number_input("Kalman Process Noise (Q)", 0.001, 0.1, 0.01, format="%.3f", help="[WHAT] IMU filter trust. [HOW] High Q means trusting the gyroscope more than the math model. [DEPLOY] Tunes how smooth the drone flies under vibration.")
        kalman_r = st.number_input("Kalman Meas. Noise (R)", 0.01, 1.0, 0.1, help="[WHAT] Sensor noise estimate. [HOW] High R means trusting the math model over a noisy GPS. [DEPLOY] Increase R when flying under thick forest canopies.")
        baro_qnh = st.number_input("Barometric QNH (hPa)", 900, 1100, 1013, help="[WHAT] Altimeter baseline. [HOW] Sea-level pressure calibration. [DEPLOY] Must be updated daily, otherwise drone altitude estimation will be severely off in mountains.")
        optical_flow = st.checkbox("Enable Optical Flow", True, help="[WHAT] Downward camera nav. [HOW] Calculates pixel velocity shift (dx/dt, dy/dt) to hold position without GPS. [DEPLOY] Essential for precision hovering near oil rigs.")
        lidar_dens = st.selectbox("LiDAR Point Density", ["Low", "Medium", "High"], help="[WHAT] Laser scanner output. [HOW] Points generated per second. [DEPLOY] High density builds 3D terrain maps but chokes the Raspberry Pi CPU.")

    if st.button("🔴 LOGOUT"): st.session_state.auth = False; st.rerun()

# --- 6. DATA ENGINE ---
def fetch_telemetry():
    try:
        SUPABASE_URL = "https://cuvuetjghxhtrgevwacx.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1dnVldGpnaHhodHJnZXZ3YWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk3MjAxNjksImV4cCI6MjA5NTI5NjE2OX0.tz7fhluw_6D2oHAlFi3ZpZG6TC_hteE-O7GPkuc5LME"
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.table("drone_telemetry").select("*").order("created_at", desc=True).limit(200).execute()
        return pd.DataFrame(res.data)
    except:
        np.random.seed(int(time.time()))
        drones = ["Hardware-Alpha", "Hardware-Beta", "Hardware-Gamma"]
        data = []
        for d in drones:
            t_base = 35 if d != "Hardware-Gamma" else 85
            data.append({
                "drone_id": d, "created_at": pd.Timestamp.now(),
                "latitude": 31.104 + np.random.randn()*0.02, "longitude": 77.166 + np.random.randn()*0.02,
                "temperature": t_base + np.random.randn()*2, "battery_level": np.random.randint(40, 95)
            })
        return pd.DataFrame(data)

df_tel = fetch_telemetry()

# --- 7. HEADER & MAIN DASHBOARD ---
st.markdown(f"<h1>{i18n[L]['title']}</h1>", unsafe_allow_html=True)

if not df_tel.empty:
    latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
    max_t = latest['temperature'].max()
    
    # Animated Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='animated-card' style='animation-delay: 0.1s;'><b>Active Nodes</b><h2>{len(latest)}</h2></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='animated-card' style='animation-delay: 0.2s;'><b>Peak Thermal</b><h2 style='color:{'#ef4444' if max_t>75 else accent};'>{max_t:.1f}°C</h2></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='animated-card' style='animation-delay: 0.3s;'><b>LoRaWAN Link Margin</b><h2>{lora_sf * 2.5 + antenna_gain} dB</h2></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='animated-card' style='animation-delay: 0.4s;'><b>Hardware Status</b><h2><div class='status-orb'></div> ACTIVE</h2></div>", unsafe_allow_html=True)
    st.write("")

    # --- 8. THE TABS ---
    tabs = st.tabs(i18n[L]['tabs'])
    
    with tabs[0]: # MAP
        fig_map = px.scatter_mapbox(latest, lat="latitude", lon="longitude", color="temperature", size=[40]*len(latest), color_continuous_scale="Inferno", zoom=12.5, height=500)
        fig_map.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_map, use_container_width=True)

    with tabs[1]: # MATH
        st.markdown("### 🧮 Hardware Mathematics: PID & Signal Math")
        eq1, eq2 = st.columns(2)
        with eq1:
            st.markdown(f"<div class='animated-card'><b>PID Controller Output Equation</b><br><br>", unsafe_allow_html=True)
            st.latex(r"u(t) = K_p e(t) + K_i \int_{0}^{t} e(\tau) d\tau + K_d \frac{de(t)}{dt}")
            st.markdown(f"<br><small>Using your settings: Kp={pid_p}, Ki={pid_i}, Kd={pid_d}</small></div>", unsafe_allow_html=True)
        with eq2:
            st.markdown(f"<div class='animated-card'><b>LoRa Signal-to-Noise Ratio (SNR)</b><br><br>", unsafe_allow_html=True)
            st.latex(r"SNR_{dB} = 10 \log_{10} \left( \frac{P_{signal}}{P_{noise}} \right)")
            st.markdown(f"<br><small>Expected SNR with SF{lora_sf}: {-2.5 * lora_sf} dB</small></div>", unsafe_allow_html=True)

    with tabs[2]: # NEW: HARDWARE SENSORS
        st.markdown("### ⚙️ Real Hardware Diagnostics Simulation")
        st.info("Simulating telemetry response based on the new sidebar hardware parameters (Kalman, Barometer, etc).")
        
        c_hw1, c_hw2 = st.columns(2)
        with c_hw1:
            st.markdown("#### IMU Sensor Noise (Kalman Filter Demo)")
            noise_arr = np.random.normal(0, kalman_r, 100) # Simulating raw noise based on R
            filtered_arr = pd.Series(noise_arr).rolling(window=int(kalman_q*1000)).mean().fillna(0) # Simple filter based on Q
            fig_noise = go.Figure()
            fig_noise.add_trace(go.Scatter(y=noise_arr, mode='lines', name='Raw Sensor (Noisy)', opacity=0.3))
            fig_noise.add_trace(go.Scatter(y=filtered_arr, mode='lines', name='Kalman Filtered', line=dict(color=accent, width=3)))
            fig_noise.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_col, height=350)
            st.plotly_chart(fig_noise, use_container_width=True)
        
        with c_hw2:
            st.markdown("#### Geofence & Navigation Logic")
            # 3D Animation trick using Plotly Camera rotation
            theta = np.linspace(0, 2*np.pi, 100)
            x, y = geofence * np.cos(theta), geofence * np.sin(theta)
            fig_geo = px.line(x=x, y=y, title=f"Virtual Geofence (Radius: {geofence}m)")
            fig_geo.add_scatter(x=[latest['latitude'].mean()*1000 % geofence], y=[latest['longitude'].mean()*1000 % geofence], mode='markers', marker=dict(size=15, color='red'), name='Drone Position')
            fig_geo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_col, height=350)
            st.plotly_chart(fig_geo, use_container_width=True)

    with tabs[3]: # NEURAL VISION
        st.markdown("### 👁️ YOLOv8 Edge-AI Feeds")
        st.write("Optical Flow Nav: ", "🟢 ACTIVE" if optical_flow else "🔴 INACTIVE")
        st.write(f"FLIR Emissivity set to: {flir_emis}")

    with tabs[4]: # ENV
        st.markdown("### 💨 Environmental Physics")
        st.write(f"Barometric QNH: {baro_qnh} hPa (Affects Altitude accuracy)")

    with tabs[5]: # DATA
        st.dataframe(df_tel, use_container_width=True)

# --- 9. AUTO-REFRESH ---
time.sleep(2)
st.rerun()
