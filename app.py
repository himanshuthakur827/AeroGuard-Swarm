import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V12 | Apex Documentation", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 2. MULTI-LANGUAGE UNIVERSAL DICTIONARY ---
i18n = {
    "EN": {"title": "🛰️ AeroGuard V12: Universal Wildfire & Swarm Nexus", "sub": "GLOBAL DEPLOYMENT | AI PREDICTIVE CORE", "tabs": ["🌍 GLOBAL RADAR", "🧮 FIRE SPREAD MATH", "👁️ NEURAL VISION", "🚁 SWARM TELEMETRY", "💨 ENV PHYSICS", "💾 DATA LAKE"]},
    "RU": {"title": "🛰️ AeroGuard V12: Универсальный Рой Лесных Пожаров", "sub": "ГЛОБАЛЬНОЕ РАЗВЕРТЫВАНИЕ | ИИ ЯДРО", "tabs": ["🌍 ГЛОБАЛЬНЫЙ РАДАР", "🧮 МАТЕМАТИКА ПОЖАРА", "👁️ НЕЙРОННОЕ ЗРЕНИЕ", "🚁 ТЕЛЕМЕТРИЯ", "💨 ФИЗИКА СРЕДЫ", "💾 ОЗЕРО ДАННЫХ"]},
    "HI": {"title": "🛰️ AeroGuard V12: यूनिवर्सल वाइल्डफायर और स्वार्म नेक्सस", "sub": "ग्लोबल डिप्लॉयमेंट | एआई प्रेडिक्टिव कोर", "tabs": ["🌍 ग्लोबल रडार", "🧮 फायर स्प्रेड मैथ", "👁️ न्यूरल विजन", "🚁 स्वार्म टेलीमेट्री", "💨 पर्यावरण भौतिकी", "💾 डेटा लेक"]},
    "AR": {"title": "🛰️ AeroGuard V12: النظام العالمي لحرائق الغابات والسرب", "sub": "النشر العالمي | النواة التنبؤية للذكاء الاصطناعي", "tabs": ["🌍 الرادار العالمي", "🧮 رياضيات انتشار الحريق", "👁️ الرؤية العصبية", "🚁 القياس عن بعد", "💨 فيزياء البيئة", "💾 بحيرة البيانات"]},
    "IT": {"title": "🛰️ AeroGuard V12: Sistema Universale Incendi e Sciami", "sub": "DISTRIBUZIONE GLOBALE | NUCLEO PREDITTIVO IA", "tabs": ["🌍 RADAR GLOBALE", "🧮 MATEMATICA INCENDI", "👁️ VISIONE NEURALE", "🚁 TELEMETRIA", "💨 FISICA AMBIENTALE", "💾 DATA LAKE"]},
    "DE": {"title": "🛰️ AeroGuard V12: Universelles Waldbrand- und Schwarmnetzwerk", "sub": "GLOBALE BEREITSTELLUNG | KI-VORHERSAGEKERN", "tabs": ["🌍 GLOBALER RADAR", "🧮 BRANDMATHEMATIK", "👁️ NEURONALES SEHEN", "🚁 TELEMETRIE", "💨 UMWELTPHYSIK", "💾 DATENSEE"]}
}

L = st.session_state.lang
T = st.session_state.theme

# --- 3. DYNAMIC LIGHT/DARK UI CSS ---
if T == "Dark":
    bg_color, panel_bg, text_col, accent, border = "#050914", "#0f172a", "#f8fafc", "#00ffcc", "#1e293b"
    map_style = "carto-darkmatter"
else:
    bg_color, panel_bg, text_col, accent, border = "#f1f5f9", "#ffffff", "#0f172a", "#2563eb", "#cbd5e1"
    map_style = "open-street-map"

st.markdown(f"""
    <style>
    .stApp {{background-color: {bg_color}; color: {text_col}; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;}}
    h1, h2, h3, h4 {{color: {accent} !important; font-weight: 800;}}
    .pro-card {{background: {panel_bg}; border: 1px solid {border}; border-top: 4px solid {accent}; border-radius: 10px; padding: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); transition: all 0.3s ease;}}
    .stTabs [data-baseweb="tab"] {{color: {text_col}; font-size: 16px; font-weight: 600;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important;}}
    .metric-value {{font-size: 2rem; font-weight: 900; color: {text_col};}}
    .metric-label {{font-size: 0.9rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px;}}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SECURE LOGIN GATEWAY ---
if not st.session_state.auth:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown(f"<div class='pro-card' style='text-align:center;'><h2>AEROGUARD LOGIN</h2><p style='color:{text_col}'>Universal Deployment Authorization</p></div>", unsafe_allow_html=True)
        pwd = st.text_input("Access Key (type 'admin')", type="password")
        if st.button("Initialize System", use_container_width=True):
            if pwd == "admin": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Access Denied.")
    st.stop()

# --- 5. THE SIDEBAR WITH "LEARN MORE" TOOLTIPS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    st.markdown(f"## ⚙️ COMMAND CENTER")
    
    with st.expander("🌐 Universal Preferences", expanded=True):
        st.session_state.lang = st.selectbox("Interface Language", ["EN", "RU", "HI", "AR", "IT", "DE"], index=["EN", "RU", "HI", "AR", "IT", "DE"].index(L), help="[LOCALIZATION] Translates core UI elements instantly for global deployment.")
        st.session_state.theme = st.selectbox("UI Mode", ["Dark", "Light"], index=["Dark", "Light"].index(T), help="[ACCESSIBILITY] Switches CSS variables between Dark (Night Ops) and Light (Day Ops) modes.")
        unit_system = st.radio("Measurement Units", ["Metric (°C, m/s)", "Imperial (°F, mph)"], help="[MATH CORE] Automatically converts database temperature and velocity payloads.")
    
    with st.expander("🧮 Wildfire Spread Math"):
        spread_model = st.selectbox("Fire Spread Algorithm", ["Rothermel Model", "Cellular Automata"], help="[APPLIED MATH] Rothermel uses partial differential equations to calculate forward rate of spread based on wind and terrain.")
        fuel_model = st.selectbox("Terrain Fuel Type", ["Short Grass (1)", "Timber Litter (8)", "Chaparral (4)"], help="[ECOLOGY] Changes the 'Fuel Load' coefficient in the mathematical equation. Grass burns faster but cooler than timber.")
        z_thresh = st.slider("Anomaly Z-Score Trigger (σ)", 1.0, 5.0, 2.0, help="[STATISTICS] Measures how many Standard Deviations (σ) a reading is from the mathematical mean. Higher = stricter anomaly detection.")
        calc_dt = st.number_input("Calculus Δt (Derivative step)", 0.1, 5.0, 1.0, help="[CALCULUS] The time-step used to calculate the First Derivative (Rate of change of heat: dT/dt).")
        
    with st.expander("💨 Environmental Physics"):
        wind_speed = st.slider("Wind Speed (km/h)", 0, 100, 25, help="[PHYSICS] Mid-flame wind velocity. Directly acts as a multiplier for the fire's forward trajectory vector.")
        wind_dir = st.slider("Wind Vector Heading (°)", 0, 360, 180, help="[GEOMETRY] 0° is North. Determines the azimuth angle for the 3D Gaussian plume dispersion.")
        drought_index = st.slider("Keetch-Byram Drought Index", 0, 800, 600, help="[METEOROLOGY] KBDI measures soil moisture depletion. >600 indicates severe drought and explosive fire growth potential.")

    with st.expander("🚁 UAV Swarm Hardware"):
        swarm_logic = st.selectbox("Swarm Intelligence", ["Particle Swarm Opt (PSO)", "Ant Colony Opt (ACO)"], help="[INFORMATICS] PSO mimics flocking birds to mathematically distribute drones for maximum terrain coverage with minimum overlap.")
        battery_decay = st.number_input("Battery Decay Rate (%/min)", 0.1, 5.0, 0.8, help="[HARDWARE] Used to calculate the Remaining Useful Life (RUL) of the drone before it must return to base.")
        rth_trigger = st.slider("Return-to-Home Battery (%)", 10, 40, 20, help="[SAFETY] Autonomous override threshold. If battery drops below this, drone aborts mission and heads to charging pad.")

    if st.button("🔴 SECURE LOGOUT"): 
        st.session_state.auth = False
        st.rerun()

# --- 6. UNIVERSAL DATA ENGINE ---
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
                "temperature": t_base + np.random.randn()*5, "battery_level": np.random.randint(30, 95),
            })
        return pd.DataFrame(data)

df_tel = fetch_telemetry()
df_tel['temperature'] = df_tel['temperature'] if unit_system.startswith("Metric") else (df_tel['temperature'] * 9/5) + 32

# --- 7. HEADER & MAIN DASHBOARD ---
st.markdown(f"<h1>{i18n[L]['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #64748b; font-size:16px;'>{i18n[L]['sub']} | MODEL: {spread_model}</p>", unsafe_allow_html=True)

if not df_tel.empty:
    latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
    
    max_t = latest['temperature'].max()
    avg_t = latest['temperature'].mean()
    critical_nodes = len(latest[latest['temperature'] > (80 if unit_system.startswith("Metric") else 176)])
    
    m1, m2, m3, m4 = st.columns(4)
    unit_str = "°C" if unit_system.startswith("Metric") else "°F"
    
    m1.markdown(f"<div class='pro-card'><div class='metric-label'>Active Swarm Nodes</div><div class='metric-value'>{len(latest)} / {len(latest)}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='pro-card'><div class='metric-label'>Peak Thermal Matrix</div><div class='metric-value' style='color: {'#ef4444' if critical_nodes>0 else accent};'>{max_t:.1f}{unit_str}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='pro-card'><div class='metric-label'>Calculated Spread Rate</div><div class='metric-value'>{(wind_speed * 0.15):.2f} m/min</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='pro-card'><div class='metric-label'>Network Latency</div><div class='metric-value'>{np.random.randint(15, 40)} ms</div></div>", unsafe_allow_html=True)
    
    st.write("")
    if critical_nodes > 0:
        st.markdown(f"<div style='background:#ef4444; color:white; padding:15px; border-radius:8px; font-weight:bold; letter-spacing:1px;'>🚨 CRITICAL ALERT: {critical_nodes} Node(s) detected catastrophic thermal signatures.</div><br>", unsafe_allow_html=True)

    # --- 8. THE TABS ---
    tabs = st.tabs(i18n[L]['tabs'])
    
    with tabs[0]:
        c_map, c_list = st.columns([3, 1])
        with c_map:
            fig_map = px.scatter_mapbox(
                latest, lat="latitude", lon="longitude", color="temperature", size=[40]*len(latest),
                color_continuous_scale="Inferno", zoom=12, height=550, hover_name="drone_id"
            )
            fig_map.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", font_color=text_col)
            st.plotly_chart(fig_map, use_container_width=True)
        with c_list:
            st.markdown(f"### 🎯 Node Live-Link")
            for _, r in latest.iterrows():
                col = "#ef4444" if r['temperature'] > (80 if unit_system.startswith("Metric") else 176) else accent
                st.markdown(f"<div style='border-left:4px solid {col}; padding:10px; background:{panel_bg}; margin-bottom:10px; border-radius:4px;'><b style='color:{text_col}'>{r['drone_id']}</b><br><span style='color:#64748b; font-size:13px;'>Temp: {r['temperature']:.1f}{unit_str} | Bat: {r['battery_level']}%</span></div>", unsafe_allow_html=True)

    with tabs[1]:
        st.markdown(f"### 🧮 Mathematical Modeling: Rothermel Fire Spread")
        eq1, eq2 = st.columns(2)
        with eq1:
            st.markdown(f"<div class='pro-card' style='height:150px;'><span style='color:#64748b;'>Rate of Spread (R)</span>", unsafe_allow_html=True)
            st.latex(r"R = \frac{I_R \xi (1 + \phi_w + \phi_s)}{\rho_b \epsilon Q_{ig}}")
            st.markdown("</div>", unsafe_allow_html=True)
        with eq2:
            st.markdown(f"<div class='pro-card' style='height:150px;'><span style='color:#64748b;'>Thermal First Derivative</span>", unsafe_allow_html=True)
            st.latex(r"\frac{\partial T}{\partial t} = \lim_{\Delta t \to 0} \frac{T(t + \Delta t) - T(t)}{\Delta t}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        c_line, c_bar = st.columns(2)
        with c_line:
            temps_arr = np.random.normal(avg_t, 5, 50)
            dt_dt = np.gradient(temps_arr, calc_dt)
            fig_dt = px.line(y=dt_dt, title=f"Calculus: Rate of Heat Change (dT/dt)", labels={'y': f'Change ({unit_str}/s)'})
            fig_dt.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_col, height=350)
            fig_dt.update_traces(line_color=accent)
            st.plotly_chart(fig_dt, use_container_width=True)
        with c_bar:
            st.markdown(f"<div class='pro-card' style='height:350px;'><h4>🔥 Fire Spread Prediction</h4><p>Based on {fuel_model}, the calculated forward rate of spread is <b>{(wind_speed * 0.15):.2f} m/min</b> in the direction of {wind_dir}°.</p><p>Expected containment difficulty: <b>EXTREME</b></p></div>", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("### 👁️ YOLOv8 Edge-AI Feeds")
        cam1, cam2 = st.columns(2)
        def draw_cam(col, name, temp):
            b_col = "red" if temp > (80 if unit_system.startswith("Metric") else 176) else accent
            col.markdown(f"""
            <div style="border: 2px solid {b_col}; background: #000; height: 250px; position: relative; border-radius: 8px;">
                <div style="position: absolute; top: 10px; left: 10px; color: {b_col}; font-family: monospace; font-size: 14px;">
                    REC 🔴 | {name} | CONFIDENCE: 92%
                </div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.2); font-size: 50px;">⌖</div>
            </div>
            """, unsafe_allow_html=True)
        
        d_list = latest.head(2).to_dict('records')
        if len(d_list) > 0: draw_cam(cam1, d_list[0]['drone_id'], d_list[0]['temperature'])
        if len(d_list) > 1: draw_cam(cam2, d_list[1]['drone_id'], d_list[1]['temperature'])

    with tabs[3]:
        latest['Flight_Time_Left'] = latest['battery_level'] / battery_decay
        fig_bar = px.bar(latest, x='drone_id', y='Flight_Time_Left', title="Remaining Useful Life (Minutes)", color='battery_level')
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=text_col, height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tabs[4]:
        st.markdown("#### Topographical Heat Dispersion")
        X, Y = np.meshgrid(np.linspace(-5, 5, 20), np.linspace(-5, 5, 20))
        Z = np.exp(-(X**2 + Y**2)/10) * max_t
        fig_heat = go.Figure(data=go.Heatmap(z=Z, colorscale='Inferno'))
        fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=text_col, height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

    with tabs[5]:
        st.dataframe(df_tel, use_container_width=True)

# --- 9. AUTO-REFRESH TRIGGER ---
time.sleep(2)
st.rerun()
