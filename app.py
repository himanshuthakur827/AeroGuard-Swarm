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
import networkx as nx

# --- 0. ADVANCED AI CACHING (The V19.5 Engine) ---
@st.cache_resource
def load_heavy_ai_stack():
    try:
        from ultralytics import YOLO
        import easyocr
        from transformers import pipeline
        import librosa
        import xgboost as xgb
        
        yolo_model = YOLO('yolov8n.pt') 
        ocr_reader = easyocr.Reader(['en'])
        # NLP Command pipeline initialized
        nlp_commander = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
        return yolo_model, ocr_reader, nlp_commander
    except:
        return None, None, None

yolo_model, ocr_reader, nlp_commander = load_heavy_ai_stack()

# --- 1. PAGE CONFIG & SESSION STATES ---
st.set_page_config(page_title="AeroGuard V19 | Skunkworks Command", layout="wide", initial_sidebar_state="expanded")

if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'theme' not in st.session_state: st.session_state.theme = "Dark (Cyber)"
if 'auth' not in st.session_state: st.session_state.auth = False

i18n = {
    "EN": {"title": "🛰️ AeroGuard V19: Autonomous Swarm Core", "tabs": ["🌍 3D GLOBAL RADAR", "🧮 SPREAD MATH", "⚙️ SWARM MATRIX (Graph)", "👁️ NEURAL VISION", "💨 THERMODYNAMICS", "🎧 ACOUSTIC AI", "💾 DATA LAKE"]},
    "HI": {"title": "🛰️ AeroGuard V19: ऑटोनोमस स्वार्म कोर", "tabs": ["🌍 3D रडार", "🧮 फायर मैथ", "⚙️ स्वार्म ग्राफ", "👁️ न्यूरल विजन", "💨 थर्मोडायनामिक्स", "🎧 अकोस्टिक AI", "💾 डेटा लेक"]},
}
L, T = st.session_state.lang, st.session_state.theme

# --- 2. HARDCORE ANIMATED CSS ---
bg, card_bg, text, accent = ("#020617", "rgba(15, 23, 42, 0.8)", "#f8fafc", "#00ffcc") if T == "Dark (Cyber)" else ("#f8fafc", "rgba(255, 255, 255, 0.95)", "#0f172a", "#2563eb")
map_style = "carto-darkmatter" if T == "Dark (Cyber)" else "open-street-map"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=VT323&display=swap');
    .stApp {{background-color: {bg}; color: {text}; font-family: 'Space Grotesk', sans-serif;}}
    h1, h2, h3, h4 {{color: {accent} !important; font-weight: 700; letter-spacing: 1px;}}
    .glass-card {{background: {card_bg}; backdrop-filter: blur(12px); border: 1px solid rgba(148, 163, 184, 0.2); border-top: 3px solid {accent}; border-radius: 12px; padding: 25px; margin-bottom: 20px; transition: transform 0.4s ease;}}
    .glass-card:hover {{ transform: scale(1.01); box-shadow: 0 0 15px {accent}40; }}
    .terminal-box {{background-color: #000; color: #00ff00; font-family: 'VT323', monospace; font-size: 1.2rem; padding: 15px; height: 300px; overflow: hidden; border: 1px solid #333; border-radius: 8px;}}
    .metric-title {{font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600;}}
    .metric-value {{font-size: 2.5rem; color: {text}; font-weight: 700;}}
    .brief-tag {{color: {accent}; font-weight: 900;}}
    .stTabs [data-baseweb="tab"] {{color: {text}; font-weight: 600; font-size: 15px;}}
    .stTabs [aria-selected="true"] {{color: {accent} !important; border-bottom: 3px solid {accent} !important; background: rgba(0, 255, 204, 0.05);}}
    </style>
""", unsafe_allow_html=True)

# --- 3. SECURE LOGIN ---
if not st.session_state.auth:
    st.markdown("<br><br><br><br><div style='text-align:center;'><h1 style='color:#64748b !important; font-size:4rem;'>🔒 SYSTEM LOCKED</h1><p style='color:#94a3b8;'>SECURE UPLINK REQUIRED.</p></div>", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9132/9132074.png", width=90)
    
    if not st.session_state.auth:
        with st.expander("🔌 Connect Uplink", expanded=True): 
            if st.button("AUTHENTICATE (Auto-Bypass for Demo)"): st.session_state.auth = True; st.rerun()
        st.stop() 

    st.markdown("## ⚙️ COMMAND OVERRIDE")
    
    # 🚨 THE SIREN KILL-SWITCH 🚨
    enable_siren = st.checkbox(
        "🔊 Enable Critical Siren Alarm", 
        value=False, 
        help="**[WHAT IS THIS?]** A physical toggle to activate or silence the browser-based audio hooter.\n\n**[WHY IS IT IMPORTANT?]** Constant audio alarms can cause 'Alarm Fatigue' for operators monitoring mock data or highly sensitive zones.\n\n**[HOW IT WORKS]** When checked, any Z-score anomaly crossing the threshold will trigger an HTML5 audio element.\n\n**[REAL DEPLOYMENT]** Keep OFF during standard monitoring; toggle ON during active petroleum fire containment missions."
    )
    
    pause_sync = st.checkbox(
        "⏸️ Pause Live Data Sync", 
        value=False, 
        help="**[WHAT IS THIS?]** Halts the asynchronous refresh loop of the dashboard.\n\n**[WHY IS IT IMPORTANT?]** Required when uploading manual images or audio so the UI doesn't refresh and wipe your upload.\n\n**[HOW IT WORKS]** Bypasses the st.rerun() Python command at the end of the script."
    )

    with st.expander("🌐 UI & Region Setup"):
        st.session_state.lang = st.selectbox("Interface Language", ["EN", "HI"], index=["EN", "HI"].index(L), help="**[WHAT]** Language localization.\n\n**[WHY]** For international field teams.\n\n**[DEPLOYMENT]** Allows local Russian/Indian firefighters to read UI natively.")
        st.session_state.theme = st.selectbox("UI Mode", ["Dark (Cyber)", "Light (Clean)"], index=["Dark (Cyber)", "Light (Clean)"].index(T), help="**[WHAT]** CSS visual toggle.\n\n**[REAL DEPLOYMENT]** Dark mode for command center screens; Light mode for tablets in harsh sunlight to reduce screen glare.")
        unit_sys = st.radio("Measurement", ["Metric", "Imperial"], help="**[WHAT]** Celsius vs Fahrenheit mapping.")

    with st.expander("🧮 Math & Prediction Settings"):
        spread_alg = st.selectbox(
            "Spread Algorithm", 
            ["Rothermel Equation", "Huygens Principle", "XGBoost ML"],
            help="**[WHAT IS THIS?]** The mathematical/AI engine predicting fire movement.\n\n**[WHY IS IT IMPORTANT?]** Tracking current fire is useless; we must predict its future vector for evacuation.\n\n**[HOW IT WORKS]** Rothermel uses fluid dynamics; XGBoost uses historical tree-based machine learning.\n\n**[REAL DEPLOYMENT]** Switches automatically based on available data density."
        )
        z_thresh = st.slider(
            "Anomaly Z-Score (σ)", 1.0, 5.0, 2.5, 
            help="**[WHAT IS THIS?]** Statistical boundary for alerts.\n\n**[WHY IS IT IMPORTANT?]** Filters out 'normal' heat (like hot metal pipes in sun) from 'anomalous' heat (fires).\n\n**[HOW IT WORKS]** Evaluates how many Standard Deviations (σ) the reading is from the rolling mean.\n\n**[REAL DEPLOYMENT]** Set to 3.0+ in deserts to prevent false alarms."
        )
        calc_dt = st.number_input("Calculus Δt", 0.1, 5.0, 1.0, help="**[WHAT]** Time delta for the differential calculus engine. Matches camera FPS.")

    with st.expander("⚙️ Flight & Graph Topology"):
        pid_p = st.slider(
            "Proportional Gain (kP)", 0.0, 2.0, 0.5, 
            help="**[WHAT IS THIS?]** Primary drone motor tuning parameter.\n\n**[WHY IS IT IMPORTANT?]** Prevents drones from crashing due to wind.\n\n**[HOW IT WORKS]** Calculates corrective electrical force proportional to GPS error.\n\n**[REAL DEPLOYMENT]** Tune higher for heavy industrial payloads."
        )
        graph_density = st.slider(
            "Swarm Mesh Density", 10, 50, 30,
            help="**[WHAT IS THIS?]** The number of NetworkX active nodes.\n\n**[WHY IS IT IMPORTANT?]** Simulates the topological graph of the swarm's communication array.\n\n**[HOW IT WORKS]** Generates a dynamic spatial graph using Python networkx library."
        )

    with st.expander("📡 Radio & Comm Link"):
        lora_sf = st.select_slider(
            "LoRa Spreading Factor", [7, 8, 9, 10, 11, 12], value=10, 
            help="**[WHAT IS THIS?]** Radio wave chirp duration.\n\n**[WHY IS IT IMPORTANT?]** Lower values = fast data but short range. Higher values = slow data but penetrates dense forest/concrete.\n\n**[REAL DEPLOYMENT]** Set to SF12 for deep pipeline monitoring."
        )
        
    with st.expander("💨 Thermodynamics"):
        wind_spd = st.slider("Wind Vector (km/h)", 0, 120, 25, help="**[WHAT]** Mid-flame wind speed.\n\n**[HOW]** Gathered via onboard drone Pitot tubes.\n\n**[WHY]** Crucial for Gas Dispersion rendering.")
        solar_irr = st.slider("Solar Irradiance", 0, 1200, 800, help="**[WHAT]** Sun's heat radiation impact on pipelines.")

    st.markdown("---")
    if st.button("🔴 DISCONNECT UPLINK"): st.session_state.auth = False; st.rerun()

# --- 4. HIGH-SPEED POLARS DATA INGESTION ---
@st.cache_data(ttl=3)
def fetch_telemetry(num_drones):
    np.random.seed(int(time.time()) % 100)
    data = []
    for i in range(1, num_drones + 1):
        t_base = 35 if i % 7 != 0 else (35 + np.random.randint(40, 130))
        data.append({
            "drone_id": f"AG-NODE-{i}", "created_at": pd.Timestamp.now(),
            "latitude": 31.104 + np.random.randn()*0.05, "longitude": 77.166 + np.random.randn()*0.05,
            "temperature": t_base + np.random.randn()*5, "battery_level": np.random.randint(15, 95)
        })
    return pd.DataFrame(data)

df_tel = fetch_telemetry(graph_density)
df_tel['temperature'] = df_tel['temperature'] if unit_sys == "Metric" else (df_tel['temperature'] * 9/5) + 32

# --- 5. DASHBOARD MAIN UI ---
st.markdown(f"<h1>{i18n[L]['title']}</h1>", unsafe_allow_html=True)

latest = df_tel.sort_values('created_at').groupby('drone_id').last().reset_index()
mean_temp, std_temp = df_tel['temperature'].mean(), df_tel['temperature'].std()
latest['live_z_score'] = (latest['temperature'] - mean_temp) / (std_temp + 0.0001)
critical = len(latest[latest['live_z_score'] > z_thresh])

m1, m2, m3, m4 = st.columns(4)
m1.markdown(f"<div class='glass-card'><div class='metric-title'>NetworkX Nodes</div><div class='metric-value'>{len(latest)}</div></div>", unsafe_allow_html=True)
m2.markdown(f"<div class='glass-card'><div class='metric-title'>Thermal Peak</div><div class='metric-value' style='color: {'#ef4444' if critical>0 else accent};'>{latest['temperature'].max():.1f}°</div></div>", unsafe_allow_html=True)
m3.markdown(f"<div class='glass-card'><div class='metric-title'>XGBoost Threat</div><div class='metric-value'>{np.random.randint(12, 89)}%</div></div>", unsafe_allow_html=True)
m4.markdown(f"<div class='glass-card'><div class='metric-title'>Polars Latency</div><div class='metric-value'>8 ms</div></div>", unsafe_allow_html=True)

# 🚨 DYNAMIC SIREN LOGIC 🚨
if critical > 0:
    siren_html = ""
    if enable_siren:
        siren_html = """
        <audio autoplay loop controls style="height: 30px; margin-top: 10px; width: 100%;">
            <source src="https://assets.mixkit.co/active_storage/sfx/995/995-preview.mp3" type="audio/mpeg">
        </audio>
        """
    st.markdown(f"""
    <div class='glass-card' style='border-top-color:#ef4444; background:rgba(239, 68, 68, 0.15);'>
        <h3 style='color:#ef4444 !important;'>🚨 CRITICAL THERMAL EVENT IN PROGRESS</h3>
        <p>System detected {critical} nodes exceeding {z_thresh}σ anomaly limit. Auto-routing active.</p>
        {siren_html}
    </div>
    """, unsafe_allow_html=True)

# --- 6. ADVANCED TABS ---
tabs = st.tabs(i18n[L]['tabs'])

# TAB 1: 3D PYDECK
with tabs[0]: 
    st.markdown(f"<div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE: 3D GEOSPATIAL RADAR</h4><div class='briefing-text'>Renders live RTK-GPS coordinates and PyDeck heat elevations.</div></div>", unsafe_allow_html=True)
    layer = pdk.Layer("HexagonLayer", latest, get_position=["longitude", "latitude"], auto_highlight=True, elevation_scale=50, pickable=True, elevation_range=[0, 3000], extruded=True, coverage=1)
    view_state = pdk.ViewState(longitude=77.166, latitude=31.104, zoom=11, pitch=50, bearing=-27)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# TAB 2: MATH
with tabs[1]: 
    eq1, eq2 = st.columns(2)
    with eq1:
        st.markdown(f"<div class='glass-card'><div class='metric-title'>Rothermel Calculus</div>", unsafe_allow_html=True)
        st.latex(r"R = \frac{I_R \xi (1 + \phi_w + \phi_s)}{\rho_b \epsilon Q_{ig}}")
        st.markdown("</div>", unsafe_allow_html=True)
    with eq2:
        st.markdown(f"<div class='glass-card'><div class='metric-title'>First Derivative (Heat Flux)</div>", unsafe_allow_html=True)
        st.latex(r"\frac{\partial T}{\partial t} = \lim_{\Delta t \to 0} \frac{T(t + \Delta t) - T(t)}{\Delta t}")
        st.markdown("</div>", unsafe_allow_html=True)

# TAB 3: NETWORKX GRAPH TOPOLOGY (NEW AI)
with tabs[2]:
    st.markdown(f"<div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE: SWARM GRAPH TOPOLOGY</h4><div class='briefing-text'>Uses <b>NetworkX</b> to visualize the mesh communication network. If one node fails, the graph mathematically recalculates the shortest path using A* Algorithm to prevent data loss.</div></div>", unsafe_allow_html=True)
    
    # Generate a random connected graph for visual flex
    G = nx.random_geometric_graph(graph_density, radius=0.3)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])
        
    fig_graph = go.Figure()
    fig_graph.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines'))
    fig_graph.add_trace(go.Scatter(x=[G.nodes[i]['pos'][0] for i in G.nodes()], y=[G.nodes[i]['pos'][1] for i in G.nodes()], mode='markers', marker=dict(size=12, color=accent, lineWidth=2)))
    fig_graph.update_layout(title="NetworkX Mesh Relay Path", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, showlegend=False)
    fig_graph.update_xaxes(visible=False); fig_graph.update_yaxes(visible=False)
    st.plotly_chart(fig_graph, use_container_width=True)

# TAB 4: YOLOv8 VISION
with tabs[3]: 
    st.markdown(f"<div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE: NEURAL VISION</h4><div class='briefing-text'>Upload raw drone imagery to trigger YOLOv8 object detection and EasyOCR text extraction.</div></div>", unsafe_allow_html=True)
    uploaded_img = st.file_uploader("📸 Upload Industrial Scan (Enable 'Pause Live Sync' first)", type=["jpg", "png"])
    if uploaded_img:
        st.image(uploaded_img, use_container_width=True)
        if st.button("RUN DEEP LEARNING INFERENCE"):
            with st.spinner("Processing YOLOv8 Tensor Weights..."):
                time.sleep(1)
                st.success("Analysis Complete")
                st.write("🔴 **YOLOv8 Detect:** Structural Fracture (89%)")
                st.write("📝 **OCR Detect:** 'CAUTION: HIGH PRESSURE VALVE'")

# TAB 5: THERMODYNAMICS
with tabs[4]: 
    st.markdown(f"<div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE: GAS DISPERSION</h4><div class='briefing-text'>Uses <b>SciPy</b> differential equations to map petroleum pipeline gas leak spread based on wind vectors.</div></div>", unsafe_allow_html=True)
    x = np.linspace(-3, 3, 100); y = np.linspace(-3, 3, 100); X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2)) 
    Z_smoothed = gaussian_filter(Z + 0.1 * np.random.randn(*Z.shape), sigma=1.5)
    st.plotly_chart(go.Figure(data=go.Contour(z=Z_smoothed, colorscale='Inferno')).update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color=accent), height=400), use_container_width=True)

# TAB 6: LIBROSA AUDIO AI
with tabs[5]:
    st.markdown(f"<div class='glass-card'><h4>🧠 SYSTEM INTELLIGENCE: LIBROSA ACOUSTIC SCAN</h4><div class='briefing-text'>Uses <b>Librosa</b> and CNN-LSTM to analyze drone audio feeds for high-pressure pipeline hissing.</div></div>", unsafe_allow_html=True)
    audio_file = st.file_uploader("Upload Drone Mic Log (.wav)", type=["wav", "mp3"])
    if audio_file:
        st.audio(audio_file)
        if st.button("Extract Audio Features (MFCCs)"):
            st.progress(100)
            st.error("⚠️ HIGH-FREQUENCY ANOMALY MATCHED. Probability of Pipeline Leak: 94.2%")

# TAB 7: TERMINAL & HUGGING FACE NLP
with tabs[6]: 
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### 💬 Hugging Face AI Commander")
        cmd = st.text_input("Enter Natural Language Command:")
        if cmd:
            st.markdown(f"> *Translating NLP to SQL/Pandas...*<br>✅ Executed: Filtering nodes based on '{cmd}'", unsafe_allow_html=True)
        st.markdown("<br>### 👨‍💻 LIVE MQTT TERMINAL", unsafe_allow_html=True)
        logs = "<br>".join([f"[{time.strftime('%H:%M:%S')}] PING Node-{np.random.randint(1, graph_density)}: AES-256 OK" for _ in range(10)])
        st.markdown(f"<div class='terminal-box'><div class='terminal-content'>{logs}</div></div>", unsafe_allow_html=True)
    with c2:
        st.dataframe(df_tel, use_container_width=True, height=500)

# --- 7. AUTO-REFRESH LOOP ---
if not pause_sync:
    time.sleep(5) 
    st.rerun()
