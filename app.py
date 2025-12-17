"""
🏎️ F1 Telemetry Dashboard
Aplicación web interactiva para análisis de telemetría de Fórmula 1
"""

import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import colormaps
import matplotlib.patches as mpatches
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
warnings.filterwarnings('ignore')

# Configuración de tema F1 para Plotly
F1_TEMPLATE = {
    'layout': {
        'paper_bgcolor': '#15151E',
        'plot_bgcolor': '#15151E',
        'font': {'family': 'Titillium Web, sans-serif', 'color': '#FFFFFF'},
        'title': {'font': {'size': 16, 'color': '#E10600'}},
        'xaxis': {
            'gridcolor': '#38383F', 'gridwidth': 1, 'linecolor': '#E10600',
            'tickfont': {'color': '#FFFFFF'}, 'title': {'font': {'color': '#FFFFFF'}}
        },
        'yaxis': {
            'gridcolor': '#38383F', 'gridwidth': 1, 'linecolor': '#E10600',
            'tickfont': {'color': '#FFFFFF'}, 'title': {'font': {'color': '#FFFFFF'}}
        },
        'legend': {'bgcolor': 'rgba(30,30,46,0.9)', 'bordercolor': '#E10600', 'borderwidth': 1}
    }
}

# Configuración de estilo F1 para matplotlib
plt.rcParams.update({
    'figure.facecolor': '#15151E',
    'axes.facecolor': '#15151E',
    'axes.edgecolor': '#E10600',
    'axes.labelcolor': '#FFFFFF',
    'text.color': '#FFFFFF',
    'xtick.color': '#FFFFFF',
    'ytick.color': '#FFFFFF',
    'grid.color': '#38383F',
    'grid.alpha': 0.3,
    'legend.facecolor': '#1E1E2E',
    'legend.edgecolor': '#E10600',
    'legend.labelcolor': '#FFFFFF',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 11,
    'legend.fontsize': 10,
})

# Configuración de la página
st.set_page_config(
    page_title="F1 Telemetry Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado - Tema F1 Moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap');
    
    /* Variables de colores F1 */
    :root {
        --f1-red: #E10600;
        --f1-dark: #15151E;
        --f1-darker: #0D0D12;
        --f1-gray: #38383F;
        --f1-light: #FFFFFF;
        --f1-accent: #FF1801;
    }
    
    /* Fuente principal */
    html, body, [class*="css"] {
        font-family: 'Titillium Web', sans-serif !important;
    }
    
    /* Fondo principal */
    .stApp {
        background: linear-gradient(180deg, var(--f1-darker) 0%, var(--f1-dark) 100%);
    }
    
    /* Header principal */
    .main-header {
        font-family: 'Titillium Web', sans-serif !important;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, var(--f1-red) 0%, #FF4136 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 2rem;
        text-shadow: 0 0 30px rgba(225, 6, 0, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A24 0%, var(--f1-dark) 100%);
        border-right: 2px solid var(--f1-red);
    }
    
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: var(--f1-red) !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid var(--f1-red);
        padding-bottom: 10px;
    }
    
    /* Selectbox y widgets */
    .stSelectbox label, .stSlider label, .stRadio label {
        font-weight: 600 !important;
        color: var(--f1-light) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
    }
    
    .stSelectbox > div > div {
        background-color: #1E1E2E !important;
        border: 1px solid var(--f1-gray) !important;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--f1-red) !important;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, var(--f1-red) 0%, #B00000 100%) !important;
        color: white !important;
        font-family: 'Titillium Web', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(225, 6, 0, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(225, 6, 0, 0.5) !important;
    }
    
    /* Métricas */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E1E2E 0%, #252532 100%);
        border: 1px solid var(--f1-gray);
        border-left: 4px solid var(--f1-red);
        border-radius: 10px;
        padding: 1rem 1.5rem;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: var(--f1-red);
        box-shadow: 0 0 20px rgba(225, 6, 0, 0.2);
    }
    
    [data-testid="stMetricLabel"] {
        color: #AAAAAA !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--f1-light) !important;
        font-weight: 700;
        font-size: 1.8rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E1E2E;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #AAAAAA;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--f1-red) 0%, #B00000 100%) !important;
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Titillium Web', sans-serif !important;
        color: var(--f1-light) !important;
        font-weight: 700;
    }
    
    /* Subheaders en tabs */
    .stTabs [data-testid="stMarkdownContainer"] h2 {
        color: var(--f1-light) !important;
        border-bottom: 2px solid var(--f1-red);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Radio buttons horizontales */
    .stRadio > div {
        background-color: #1E1E2E;
        border-radius: 10px;
        padding: 10px;
    }
    
    .stRadio [data-baseweb="radio"] {
        background-color: transparent;
    }
    
    /* Alertas y mensajes */
    .stSuccess {
        background-color: rgba(0, 200, 83, 0.1) !important;
        border: 1px solid #00C853 !important;
        border-radius: 10px;
    }
    
    .stError {
        background-color: rgba(225, 6, 0, 0.1) !important;
        border: 1px solid var(--f1-red) !important;
        border-radius: 10px;
    }
    
    .stInfo {
        background-color: rgba(33, 150, 243, 0.1) !important;
        border: 1px solid #2196F3 !important;
        border-radius: 10px;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--f1-red) !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        border: 1px solid var(--f1-gray);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: var(--f1-red) !important;
    }
    
    /* Separador */
    hr {
        border-color: var(--f1-gray) !important;
    }
    
    /* ===== RESPONSIVE - SIN SCROLL ===== */
    
    /* Ocultar scroll y ajustar altura */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    
    /* Header más compacto */
    .main-header {
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
        padding: 0 !important;
    }
    
    /* Métricas más compactas */
    [data-testid="stMetric"] {
        padding: 0.5rem 0.8rem !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
    }
    
    /* Tabs más compactos */
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px !important;
        font-size: 0.8rem !important;
    }
    
    /* Subheaders más pequeños */
    .stTabs h2, .stTabs h3 {
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
        padding-bottom: 5px !important;
    }
    
    /* Reducir espaciado general */
    .element-container {
        margin-bottom: 0.3rem !important;
    }
    
    /* Eliminar espacio extra debajo de gráficos Plotly */
    .stPlotlyChart {
        margin-bottom: -2rem !important;
        padding-bottom: 0 !important;
    }
    
    /* Reducir espacio entre elementos en tabs */
    .stTabs [data-testid="stVerticalBlock"] > div {
        gap: 0 !important;
    }
    
    /* Eliminar espacios en contenedores */
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    
    .stTabs [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Eliminar espacio debajo de métricas/cards */
    [data-testid="stMetric"] {
        margin-bottom: 0 !important;
    }
    
    .stTabs [data-testid="stHorizontalBlock"] {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Contenido de tabs sin espacio extra */
    .stTabs [data-baseweb="tab-panel"] {
        padding-bottom: 0 !important;
    }
    
    /* Footer fijo para no ocupar espacio */
    .footer-text {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        color: #666666;
        font-size: 0.75rem;
        padding: 5px 10px;
        background: linear-gradient(to top, #15151E 80%, transparent);
        z-index: 1000;
    }
    
    /* Gráficos responsivos */
    .stPlotlyChart, [data-testid="stImage"] {
        max-height: 50vh !important;
    }
    
    /* Radio buttons más compactos */
    .stRadio > div {
        padding: 5px !important;
    }
    
    .stRadio label {
        font-size: 0.8rem !important;
    }
    
    /* Sidebar más compacto */
    [data-testid="stSidebar"] {
        width: 280px !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox {
        margin-bottom: 0.5rem !important;
    }
    
    /* Mejorar contraste de selectboxes en sidebar */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background-color: #1E1E2E !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #1E1E2E !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] span {
        color: #FFFFFF !important;
    }
    
    /* Dropdown options - fondo blanco con texto negro */
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    
    [data-baseweb="popover"] li {
        color: #000000 !important;
    }
    
    [data-baseweb="popover"] li:hover {
        background-color: #E10600 !important;
        color: #FFFFFF !important;
    }
    
    /* Columns más ajustadas */
    [data-testid="column"] {
        padding: 0 0.3rem !important;
    }
    
    /* Success/Info messages compactos */
    .stSuccess, .stInfo, .stError {
        padding: 0.5rem !important;
        font-size: 0.85rem !important;
    }
    
    /* DataFrames compactos */
    .stDataFrame {
        max-height: 45vh !important;
    }
    
    /* Slider compacto */
    .stSlider {
        padding-top: 0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Media queries para pantallas pequeñas */
    @media (max-height: 800px) {
        .main-header {
            font-size: 1.5rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 8px !important;
            font-size: 0.7rem !important;
        }
    }
    
    @media (max-width: 1200px) {
        .main-header {
            font-size: 1.8rem !important;
        }
        
        [data-testid="stSidebar"] {
            width: 250px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Colores de equipos
TEAM_COLORS = {
    'Red Bull Racing': '#3671C6',
    'Ferrari': '#E80020',
    'Mercedes': '#27F4D2',
    'McLaren': '#FF8000',
    'Aston Martin': '#229971',
    'Alpine': '#FF87BC',
    'Williams': '#64C4FF',
    'RB': '#6692FF',
    'Sauber': '#52E252',
    'Haas F1 Team': '#B6BABD',
    'Kick Sauber': '#52E252',
    'Racing Bulls': '#6692FF',
}

# Configurar caché de FastF1
cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

# Título principal
st.markdown('<h1 class="main-header">🏎️ F1 Telemetry Dashboard</h1>', unsafe_allow_html=True)

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Selección de año (ahora incluye 2025 y prepara para 2026)
year = st.sidebar.selectbox(
    "📅 Año",
    options=[2025, 2024, 2023, 2022, 2021, 2020],
    index=0
)

# Obtener eventos del año
@st.cache_data(ttl=1800)  # Cache de 30 minutos para datos más frescos
def get_events(year):
    schedule = fastf1.get_event_schedule(year)
    # Filtrar solo eventos (no testing)
    events = schedule[schedule['EventFormat'] != 'testing']
    return events['EventName'].tolist()

try:
    events = get_events(year)
    gp = st.sidebar.selectbox("🏁 Gran Premio", options=events, index=0)
except Exception as e:
    st.sidebar.error(f"Error cargando eventos: {e}")
    gp = "Monaco"

# Selección de sesión
session_type = st.sidebar.selectbox(
    "📊 Sesión",
    options=['Q', 'R', 'FP1', 'FP2', 'FP3', 'S', 'SQ'],
    format_func=lambda x: {
        'Q': 'Clasificación',
        'R': 'Carrera',
        'FP1': 'Práctica Libre 1',
        'FP2': 'Práctica Libre 2',
        'FP3': 'Práctica Libre 3',
        'S': 'Sprint',
        'SQ': 'Sprint Qualifying'
    }.get(x, x),
    index=0
)

# Botón para cargar datos
col_load, col_live = st.sidebar.columns([2, 1])
with col_load:
    if st.button("🔄 Cargar Datos", type="primary"):
        st.session_state['load_data'] = True
with col_live:
    live_mode = st.checkbox("🔴 Live", help="Modo en vivo - actualiza datos más frecuentemente")

# Cargar datos de sesión
@st.cache_data(ttl=300, show_spinner=False)  # Cache corto para datos frescos
def load_session_data(year, gp, session_type, live=False):
    """Carga datos de sesión. El parámetro live fuerza recarga del cache."""
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session

# Obtener pilotos de la sesión
@st.cache_data(ttl=3600)
def get_drivers_info(_session):
    drivers_info = []
    for drv in _session.drivers:
        try:
            drv_laps = _session.laps.pick_driver(drv)
            if len(drv_laps) > 0:
                fastest = drv_laps.pick_fastest()
                if fastest is not None and not pd.isna(fastest['LapTime']):
                    drivers_info.append({
                        'code': fastest['Driver'],
                        'team': fastest['Team'],
                        'lap_time': fastest['LapTime'],
                        'lap_time_str': str(fastest['LapTime'])[-12:-3]
                    })
        except:
            continue
    return sorted(drivers_info, key=lambda x: x['lap_time'])

# Estado de sesión
if 'session' not in st.session_state:
    st.session_state['session'] = None
    st.session_state['drivers'] = []

# Cargar datos
if st.session_state.get('load_data', False) or st.session_state['session'] is None:
    with st.spinner(f"⏳ Cargando datos de {gp} {year}..."):
        try:
            session = load_session_data(year, gp, session_type, live_mode)
            st.session_state['session'] = session
            st.session_state['drivers'] = get_drivers_info(session)
            st.session_state['load_data'] = False
        except Exception as e:
            st.error(f"❌ Error cargando datos: {e}")
            st.info("💡 **Posibles causas:**\n- La sesión aún no ha terminado\n- Datos no disponibles todavía\n- Verifica tu conexión a internet")
            st.stop()

session = st.session_state['session']
drivers_info = st.session_state['drivers']

if session is None:
    st.info("👆 Selecciona un evento y haz clic en 'Cargar Datos' para comenzar")
    st.stop()

# Sidebar - Selección de pilotos
st.sidebar.markdown("---")
st.sidebar.header("👨‍✈️ Pilotos")

driver_options = [f"{d['code']} - {d['team']}" for d in drivers_info]
driver_codes = [d['code'] for d in drivers_info]

if len(driver_options) >= 1:
    # Selector de número de pilotos
    max_pilots = min(20, len(driver_options))
    num_pilots = st.sidebar.slider(
        "Número de pilotos a comparar",
        min_value=1,
        max_value=max_pilots,
        value=min(2, max_pilots),
        key="num_pilots"
    )
    
    # Generar selectores dinámicos
    selected_drivers = []
    for i in range(num_pilots):
        default_idx = i if i < len(driver_options) else 0
        driver_idx = st.sidebar.selectbox(
            f"Piloto {i + 1}",
            options=range(len(driver_options)),
            format_func=lambda x: driver_options[x],
            index=default_idx,
            key=f"pilot_{i}"
        )
        selected_drivers.append(driver_codes[driver_idx])
    
    # Para compatibilidad con código existente
    DRIVER_1 = selected_drivers[0]
    DRIVER_2 = selected_drivers[1] if len(selected_drivers) > 1 else selected_drivers[0]
    SELECTED_DRIVERS = selected_drivers
else:
    st.error("No hay suficientes pilotos con datos válidos")
    st.stop()

# Información del evento
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🏁 Gran Premio", session.event['EventName'])
with col2:
    st.metric("📅 Fecha", str(session.event['EventDate'])[:10])
with col3:
    st.metric("🏎️ Pilotos", len(drivers_info))

# Tabs para diferentes visualizaciones
tab_general, tab_mapa, tab_perfecta, tab_degradacion, tab_animacion, tab_clasificacion = st.tabs([
    "📊 General", 
    "🗺️ Mapa del Circuito",
    "⚡ Vuelta Perfecta",
    "💹 Degradación",
    "🎬 Animación",
    "📈 Clasificación"
])

# Obtener datos de los pilotos seleccionados
@st.cache_data(ttl=3600)
def get_lap_telemetry(_session, driver):
    lap = _session.laps.pick_driver(driver).pick_fastest()
    tel = lap.get_car_data().add_distance()
    tel_full = lap.get_telemetry()
    return lap, tel, tel_full

# Cargar datos de todos los pilotos seleccionados
pilots_data = {}
try:
    for drv in SELECTED_DRIVERS:
        lap, tel, tel_full = get_lap_telemetry(session, drv)
        color = TEAM_COLORS.get(lap['Team'], '#FFFFFF')
        pilots_data[drv] = {
            'lap': lap,
            'tel': tel,
            'tel_full': tel_full,
            'color': color,
            'team': lap['Team']
        }
    
    # Para compatibilidad con código existente
    lap_d1, tel_d1, tel_full_d1 = pilots_data[DRIVER_1]['lap'], pilots_data[DRIVER_1]['tel'], pilots_data[DRIVER_1]['tel_full']
    lap_d2, tel_d2, tel_full_d2 = pilots_data[DRIVER_2]['lap'], pilots_data[DRIVER_2]['tel'], pilots_data[DRIVER_2]['tel_full']
    color_d1 = pilots_data[DRIVER_1]['color']
    color_d2 = pilots_data[DRIVER_2]['color']
except Exception as e:
    st.error(f"Error obteniendo telemetría: {e}")
    st.stop()

# TAB 1: Speed Trace
with tab_general:
    drivers_str = " vs ".join(SELECTED_DRIVERS)
    
    # Preparar datos para todos los gráficos
    final_deltas = {}
    reference_driver = SELECTED_DRIVERS[0] if len(SELECTED_DRIVERS) >= 2 else None
    
    # Obtener coordenadas del circuito del primer piloto
    # Usar tel_full para coordenadas y tel para distancia/velocidad
    tel_full_circuit = pilots_data[SELECTED_DRIVERS[0]]['tel_full']
    tel_circuit = pilots_data[SELECTED_DRIVERS[0]]['tel']
    
    # Las coordenadas X,Y están en tel_full
    x_circuit_raw = tel_full_circuit['X'].values
    y_circuit_raw = tel_full_circuit['Y'].values
    
    # La distancia está en tel_full también (si existe) o la calculamos
    if 'Distance' in tel_full_circuit.columns:
        distance_circuit = tel_full_circuit['Distance'].values
        speed_circuit = tel_full_circuit['Speed'].values
    else:
        # Interpolar la distancia de tel a las coordenadas de tel_full
        # Usamos la distancia de tel_circuit interpolada al tamaño de tel_full
        distance_circuit = np.linspace(0, tel_circuit['Distance'].max(), len(x_circuit_raw))
        speed_circuit = np.interp(distance_circuit, tel_circuit['Distance'].values, tel_circuit['Speed'].values)
    
    # Rotar para orientación horizontal
    x_circuit = y_circuit_raw
    y_circuit = -x_circuit_raw
    
    # Calcular delta time si hay más de un piloto
    delta_traces = []
    if len(SELECTED_DRIVERS) >= 2:
        delta_data = {}
        for drv in SELECTED_DRIVERS:
            try:
                lap = session.laps.pick_driver(drv).pick_fastest()
                tel = lap.get_car_data().add_distance()
                team = lap['Team']
                color = TEAM_COLORS.get(team, '#FFFFFF')
                delta_data[drv] = {'tel': tel, 'color': color}
            except:
                pass
        
        if len(delta_data) >= 2:
            tel_ref = delta_data[reference_driver]['tel']
            max_distance = min([delta_data[drv]['tel']['Distance'].max() for drv in delta_data])
            distance_common = np.linspace(0, max_distance, num=500)
            time_ref = (tel_ref['Time'] - tel_ref['Time'].iloc[0]).dt.total_seconds().values
            time_ref_interp = np.interp(distance_common, tel_ref['Distance'].values, time_ref)
            
            for drv, data in delta_data.items():
                if drv == reference_driver:
                    continue
                tel = data['tel']
                color = data['color']
                time_drv = (tel['Time'] - tel['Time'].iloc[0]).dt.total_seconds().values
                time_drv_interp = np.interp(distance_common, tel['Distance'].values, time_drv)
                delta = time_drv_interp - time_ref_interp
                final_deltas[drv] = delta[-1]
                delta_traces.append({'drv': drv, 'x': distance_common, 'y': delta, 'color': color})
    
    # Crear gráfico unificado con 5 paneles
    fig_unified = make_subplots(
        rows=5, cols=1, shared_xaxes=True,
        row_heights=[0.25, 0.15, 0.20, 0.20, 0.20],
        vertical_spacing=0.02
    )
    
    dash_styles = ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    
    # Panel 1: Velocidad
    for idx, drv in enumerate(SELECTED_DRIVERS):
        data = pilots_data[drv]
        dash_style = dash_styles[idx % len(dash_styles)]
        fig_unified.add_trace(go.Scatter(
            x=data['tel']['Distance'], y=data['tel']['Speed'],
            mode='lines', name=f"{drv}",
            line=dict(color=data['color'], width=1.5, dash=dash_style if idx > 0 else 'solid'),
            hovertemplate=f'{drv}: %{{y:.1f}} km/h<extra></extra>',
            customdata=data['tel']['Distance']
        ), row=1, col=1)
    
    # Panel 2: Delta Time
    if delta_traces:
        for trace in delta_traces:
            fig_unified.add_trace(go.Scatter(
                x=trace['x'], y=trace['y'],
                mode='lines', name=f'Δ {trace["drv"]}',
                line=dict(color=trace['color'], width=1.5),
                fill='tozeroy', fillcolor=f"rgba{tuple(list(int(trace['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.3])}",
                showlegend=False,
                hovertemplate=f'{trace["drv"]}: %{{y:.3f}}s<extra></extra>'
            ), row=2, col=1)
        fig_unified.add_hline(y=0, line=dict(color='#E10600', width=1.5), row=2, col=1)
    
    # Paneles 3, 4, 5: Inputs (Acelerador, Freno, RPM)
    for idx, drv in enumerate(SELECTED_DRIVERS):
        data = pilots_data[drv]
        tel_full = data['tel']
        color = data['color']
        dash_style = dash_styles[idx % len(dash_styles)]
        
        # Panel 3: Acelerador
        fig_unified.add_trace(go.Scatter(
            x=tel_full['Distance'], y=tel_full['Throttle'],
            mode='lines', name=drv, line=dict(color=color, width=1.2, dash=dash_style if idx > 0 else 'solid'),
            showlegend=False, hovertemplate=f'{drv}: %{{y:.0f}}%<extra></extra>'
        ), row=3, col=1)
        
        # Panel 4: Freno
        fig_unified.add_trace(go.Scatter(
            x=tel_full['Distance'], y=tel_full['Brake'].astype(int) * 100,
            mode='lines', name=drv, line=dict(color=color, width=1.2, dash=dash_style if idx > 0 else 'solid'),
            showlegend=False, hovertemplate=f'{drv}: %{{y}}%<extra></extra>'
        ), row=4, col=1)
        
        # Panel 5: RPM
        fig_unified.add_trace(go.Scatter(
            x=tel_full['Distance'], y=tel_full['RPM'],
            mode='lines', name=drv, line=dict(color=color, width=1.2, dash=dash_style if idx > 0 else 'solid'),
            showlegend=False, hovertemplate=f'{drv}: %{{y:,.0f}} RPM<extra></extra>'
        ), row=5, col=1)
    
    fig_unified.update_layout(
        height=700,
        paper_bgcolor='#15151E', plot_bgcolor='#15151E',
        font=dict(family='Titillium Web, sans-serif', color='#FFFFFF', size=10),
        legend=dict(
            bgcolor='rgba(21,21,30,0.95)', bordercolor='#E10600', borderwidth=1,
            x=1, y=1, xanchor='right', font=dict(color='#FFFFFF'),
            orientation='h', yanchor='bottom'
        ),
        hovermode='x unified',
        margin=dict(l=100, r=20, t=5, b=25)
    )
    
    # Actualizar todos los ejes con títulos a la izquierda
    for i in range(1, 6):
        fig_unified.update_xaxes(gridcolor='#38383F', linecolor='#E10600', row=i, col=1)
        fig_unified.update_yaxes(gridcolor='#38383F', linecolor='#E10600', row=i, col=1)
    
    # Títulos de eje Y para cada panel
    fig_unified.update_yaxes(title_text='VELOCIDAD<br>(km/h)', title_font=dict(size=9, color='#AAAAAA'), row=1, col=1)
    fig_unified.update_yaxes(title_text=f'DELTA vs {reference_driver}<br>(s)' if reference_driver else 'DELTA (s)', title_font=dict(size=9, color='#AAAAAA'), row=2, col=1)
    fig_unified.update_yaxes(title_text='ACELERADOR<br>(%)', title_font=dict(size=9, color='#AAAAAA'), range=[-5, 105], row=3, col=1)
    fig_unified.update_yaxes(title_text='FRENO<br>(%)', title_font=dict(size=9, color='#AAAAAA'), range=[-5, 105], row=4, col=1)
    fig_unified.update_yaxes(title_text='RPM', title_font=dict(size=9, color='#AAAAAA'), row=5, col=1)
    
    fig_unified.update_xaxes(title='DISTANCIA (m)', row=5, col=1)
    
    # Reducir datos para el HTML (tomar cada N puntos)
    step_circuit = max(1, len(x_circuit) // 500)
    x_c = x_circuit[::step_circuit].tolist()
    y_c = y_circuit[::step_circuit].tolist()
    d_c = distance_circuit[::step_circuit].tolist()
    s_c = speed_circuit[::step_circuit].tolist()
    
    # RPM del circuito (del primer piloto)
    tel_full_rpm = pilots_data[SELECTED_DRIVERS[0]]['tel_full']
    rpm_circuit = tel_full_rpm['RPM'].values[::step_circuit].tolist()
    
    # Preparar datos de telemetría reducidos para cada piloto
    import json
    step_tel = max(1, len(pilots_data[SELECTED_DRIVERS[0]]['tel']) // 800)
    
    tel_traces_data = []
    for idx, drv in enumerate(SELECTED_DRIVERS):
        data = pilots_data[drv]
        tel = data['tel']
        tel_traces_data.append({
            'name': drv,
            'color': data['color'],
            'distance': tel['Distance'].values[::step_tel].tolist(),
            'speed': tel['Speed'].values[::step_tel].tolist(),
            'throttle': tel['Throttle'].values[::step_tel].tolist(),
            'brake': (tel['Brake'].astype(int) * 100).values[::step_tel].tolist(),
            'rpm': tel['RPM'].values[::step_tel].tolist()
        })
    
    # Preparar datos de delta reducidos
    delta_traces_data = []
    for trace in delta_traces:
        step_delta = max(1, len(trace['x']) // 800)
        delta_traces_data.append({
            'drv': trace['drv'],
            'color': trace['color'],
            'x': trace['x'][::step_delta].tolist(),
            'y': trace['y'][::step_delta].tolist()
        })
    
    # Preparar datos de métricas para las tarjetas
    metrics_data = []
    for drv in SELECTED_DRIVERS:
        data = pilots_data[drv]
        lap_time = str(data['lap']['LapTime'])[-12:-3]
        vmax = data['tel']['Speed'].max()
        delta_str = ""
        if drv in final_deltas:
            delta_val = final_deltas[drv]
            delta_str = f"({'+' if delta_val > 0 else ''}{delta_val:.3f}s)"
        metrics_data.append({
            'driver': drv,
            'color': data['color'],
            'lap_time': lap_time,
            'delta': delta_str,
            'vmax': f"{vmax:.0f}"
        })
    
    # Crear componente HTML con ambas gráficas sincronizadas
    html_component = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background-color: #15151E; font-family: 'Titillium Web', Arial, sans-serif; }}
            .main-container {{ display: flex; gap: 15px; padding: 10px; }}
            .telemetry-panel {{ flex: 3; }}
            .circuit-panel {{ flex: 1; display: flex; flex-direction: column; }}
            .circuit-title {{ color: white; font-size: 16px; margin-bottom: 10px; font-weight: bold; }}
            .info-box {{ 
                background: linear-gradient(135deg, #1a1a24 0%, #252530 100%);
                border: 1px solid #E10600;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
                text-align: center;
            }}
            .speed-value {{ color: #E10600; font-size: 28px; font-weight: bold; }}
            .speed-label {{ color: #888; font-size: 11px; margin-bottom: 3px; }}
            .rpm-value {{ color: #FF6B00; font-size: 22px; font-weight: bold; margin-top: 8px; }}
            .distance-value {{ color: white; font-size: 16px; margin-top: 8px; }}
            .hint {{ color: #666; font-size: 11px; margin-top: 8px; }}
            
            /* Tarjetas de métricas */
            .metrics-row {{
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
                margin-top: 10px;
                padding-top: 5px;
                flex-wrap: wrap;
            }}
            .metric-card {{
                flex: 1;
                min-width: 200px;
                background: linear-gradient(135deg, #1a1a24 0%, #252530 100%);
                border-radius: 10px;
                padding: 15px 20px;
                border-left: 4px solid;
            }}
            .metric-driver {{
                font-size: 13px;
                color: #888;
                margin-bottom: 5px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .metric-driver::before {{
                content: '';
                width: 20px;
                height: 3px;
                background: currentColor;
            }}
            .metric-time {{
                font-size: 26px;
                font-weight: bold;
                color: #00FF88;
            }}
            .metric-delta {{
                color: #E10600;
                font-size: 18px;
                margin-left: 8px;
            }}
            .metric-vmax {{
                font-size: 12px;
                color: #00D4FF;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="metrics-row" id="metricsRow"></div>
        <div class="main-container">
            <div class="telemetry-panel">
                <div id="telemetry"></div>
            </div>
            <div class="circuit-panel">
                <div class="circuit-title">🗺️ Circuito</div>
                <div id="circuit"></div>
                <div class="info-box">
                    <div class="speed-label">🏎️ VELOCIDAD</div>
                    <div class="speed-value" id="speedValue">-- km/h</div>
                    <div class="speed-label">⚙️ RPM</div>
                    <div class="rpm-value" id="rpmValue">--</div>
                    <div class="distance-value" id="distValue">📍 -- m</div>
                    <div class="hint">Pasa el ratón sobre la gráfica</div>
                </div>
            </div>
        </div>
        
        <script>
            // Datos del circuito
            // Datos de métricas
            const metricsData = {json.dumps(metrics_data)};
            
            // Generar tarjetas de métricas
            const metricsRow = document.getElementById('metricsRow');
            metricsData.forEach(m => {{
                const card = document.createElement('div');
                card.className = 'metric-card';
                card.style.borderColor = m.color;
                card.innerHTML = `
                    <div class="metric-driver" style="color: ${{m.color}}">🏎️ ${{m.driver}}</div>
                    <div>
                        <span class="metric-time">${{m.lap_time}}</span>
                        <span class="metric-delta">${{m.delta}}</span>
                    </div>
                    <div class="metric-vmax">↑ Vmax: ${{m.vmax}} km/h</div>
                `;
                metricsRow.appendChild(card);
            }});
            
            const xCircuit = {json.dumps(x_c)};
            const yCircuit = {json.dumps(y_c)};
            const distances = {json.dumps(d_c)};
            const speeds = {json.dumps(s_c)};
            const rpms = {json.dumps(rpm_circuit)};
            
            // Datos de telemetría
            const telData = {json.dumps(tel_traces_data)};
            const deltaData = {json.dumps(delta_traces_data)};
            const refDriver = "{reference_driver or ''}";
            
            // Construir trazas de telemetría
            const dashStyles = ['solid', 'dot', 'dash', 'longdash', 'dashdot'];
            let traces = [];
            
            // Panel 1: Velocidad
            telData.forEach((d, i) => {{
                traces.push({{
                    x: d.distance, y: d.speed,
                    mode: 'lines', name: d.name,
                    line: {{color: d.color, width: 1.5, dash: i > 0 ? dashStyles[i % dashStyles.length] : 'solid'}},
                    xaxis: 'x', yaxis: 'y',
                    hovertemplate: d.name + ': %{{y:.1f}} km/h<extra></extra>'
                }});
            }});
            
            // Panel 2: Delta
            deltaData.forEach(d => {{
                traces.push({{
                    x: d.x, y: d.y,
                    mode: 'lines', name: 'Δ ' + d.drv,
                    line: {{color: d.color, width: 1.5}},
                    fill: 'tozeroy',
                    fillcolor: d.color + '40',
                    xaxis: 'x', yaxis: 'y2',
                    showlegend: false,
                    hovertemplate: d.drv + ': %{{y:.3f}}s<extra></extra>'
                }});
            }});
            
            // Paneles 3, 4, 5: Throttle, Brake, RPM
            telData.forEach((d, i) => {{
                const dash = i > 0 ? dashStyles[i % dashStyles.length] : 'solid';
                traces.push({{
                    x: d.distance, y: d.throttle,
                    mode: 'lines', line: {{color: d.color, width: 1.2, dash: dash}},
                    xaxis: 'x', yaxis: 'y3', showlegend: false,
                    hovertemplate: d.name + ': %{{y:.0f}}%<extra></extra>'
                }});
                traces.push({{
                    x: d.distance, y: d.brake,
                    mode: 'lines', line: {{color: d.color, width: 1.2, dash: dash}},
                    xaxis: 'x', yaxis: 'y4', showlegend: false,
                    hovertemplate: d.name + ': %{{y}}%<extra></extra>'
                }});
                traces.push({{
                    x: d.distance, y: d.rpm,
                    mode: 'lines', line: {{color: d.color, width: 1.2, dash: dash}},
                    xaxis: 'x', yaxis: 'y5', showlegend: false,
                    hovertemplate: d.name + ': %{{y:,.0f}} RPM<extra></extra>'
                }});
            }});
            
            const layout = {{
                height: 700,
                paper_bgcolor: '#15151E',
                plot_bgcolor: '#15151E',
                font: {{family: 'Titillium Web, sans-serif', color: '#FFFFFF', size: 10}},
                hovermode: 'x unified',
                margin: {{l: 80, r: 20, t: 10, b: 40}},
                legend: {{
                    bgcolor: 'rgba(21,21,30,0.95)', bordercolor: '#E10600', borderwidth: 1,
                    x: 0.5, y: 1.02, xanchor: 'center', orientation: 'h', yanchor: 'bottom'
                }},
                xaxis: {{
                    domain: [0, 1], anchor: 'y5', title: 'DISTANCIA (m)',
                    gridcolor: '#38383F', linecolor: '#E10600', tickfont: {{color: '#FFF'}}
                }},
                yaxis: {{
                    domain: [0.82, 1], title: {{text: 'VELOCIDAD (km/h)', font: {{size: 9, color: '#AAA'}}}},
                    gridcolor: '#38383F', linecolor: '#E10600'
                }},
                yaxis2: {{
                    domain: [0.62, 0.80], title: {{text: refDriver ? 'DELTA vs ' + refDriver + ' (s)' : 'DELTA (s)', font: {{size: 9, color: '#AAA'}}}},
                    gridcolor: '#38383F', linecolor: '#E10600'
                }},
                yaxis3: {{
                    domain: [0.42, 0.60], title: {{text: 'ACELERADOR (%)', font: {{size: 9, color: '#AAA'}}}},
                    gridcolor: '#38383F', linecolor: '#E10600', range: [-5, 105]
                }},
                yaxis4: {{
                    domain: [0.22, 0.40], title: {{text: 'FRENO (%)', font: {{size: 9, color: '#AAA'}}}},
                    gridcolor: '#38383F', linecolor: '#E10600', range: [-5, 105]
                }},
                yaxis5: {{
                    domain: [0, 0.20], title: {{text: 'RPM', font: {{size: 9, color: '#AAA'}}}},
                    gridcolor: '#38383F', linecolor: '#E10600'
                }}
            }};
            
            Plotly.newPlot('telemetry', traces, layout, {{displayModeBar: true, scrollZoom: true, responsive: true}});
            
            // Crear circuito
            const circuitData = [
                {{x: xCircuit, y: yCircuit, mode: 'lines', line: {{color: '#2A2A35', width: 14}}, hoverinfo: 'skip'}},
                {{x: xCircuit, y: yCircuit, mode: 'markers+lines',
                    marker: {{color: speeds, colorscale: 'Plasma', size: 4, showscale: true,
                        colorbar: {{title: {{text: 'km/h', side: 'right'}}, thickness: 12, len: 0.6}}}},
                    line: {{color: 'rgba(255,107,0,0.2)', width: 1}}, hoverinfo: 'skip'}},
                {{x: [xCircuit[0]], y: [yCircuit[0]], mode: 'markers',
                    marker: {{color: '#E10600', size: 20, symbol: 'circle', line: {{color: 'white', width: 3}}}}, hoverinfo: 'skip'}},
                {{x: [xCircuit[0]], y: [yCircuit[0]], mode: 'markers',
                    marker: {{color: '#00FF00', size: 14, symbol: 'square', line: {{color: 'white', width: 2}}}}, hoverinfo: 'skip'}}
            ];
            
            Plotly.newPlot('circuit', circuitData, {{
                height: 400, paper_bgcolor: '#15151E', plot_bgcolor: '#15151E',
                xaxis: {{showgrid: false, zeroline: false, showticklabels: false, scaleanchor: 'y'}},
                yaxis: {{showgrid: false, zeroline: false, showticklabels: false}},
                margin: {{l: 5, r: 60, t: 5, b: 5}}, showlegend: false
            }}, {{displayModeBar: false, responsive: true}});
            
            // Función para encontrar índice más cercano
            function findIdx(targetDist) {{
                let minDiff = Infinity, idx = 0;
                for (let i = 0; i < distances.length; i++) {{
                    const diff = Math.abs(distances[i] - targetDist);
                    if (diff < minDiff) {{ minDiff = diff; idx = i; }}
                }}
                return idx;
            }}
            
            // Sincronizar hover
            document.getElementById('telemetry').on('plotly_hover', function(data) {{
                if (data.points && data.points.length > 0) {{
                    const xVal = data.points[0].x;
                    const idx = findIdx(xVal);
                    Plotly.restyle('circuit', {{x: [[xCircuit[idx]]], y: [[yCircuit[idx]]]}}, [2]);
                    document.getElementById('speedValue').textContent = speeds[idx].toFixed(0) + ' km/h';
                    document.getElementById('rpmValue').textContent = rpms[idx].toLocaleString();
                    document.getElementById('distValue').textContent = '📍 ' + xVal.toFixed(0) + ' m';
                }}
            }});
            
            document.getElementById('telemetry').on('plotly_unhover', function() {{
                document.getElementById('speedValue').textContent = '-- km/h';
                document.getElementById('rpmValue').textContent = '--';
                document.getElementById('distValue').textContent = '📍 -- m';
            }});
        </script>
    </body>
    </html>
    '''
    
    import streamlit.components.v1 as components
    components.html(html_component, height=800, scrolling=False)

# TAB: Mapa del Circuito
with tab_mapa:
    st.subheader("🗺️ Mapa del Circuito")
    
    map_type = st.radio(
        "Tipo de visualización:",
        ["Velocidad", "Mini-Sectores (Comparación)", "Marchas"],
        horizontal=True
    )
    
    # Selector de piloto para mapas individuales
    if map_type in ["Velocidad", "Marchas"]:
        selected_map_driver = st.selectbox("Piloto para el mapa:", SELECTED_DRIVERS)
    
    # Cargar datos del piloto seleccionado
    try:
        lap_map = session.laps.pick_driver(selected_map_driver if map_type in ["Velocidad", "Marchas"] else SELECTED_DRIVERS[0]).pick_fastest()
        pos_map = lap_map.get_telemetry()
        tel_full_map = lap_map.get_car_data().add_distance()
    except:
        lap_map = lap_d1
        pos_map = lap_d1.get_telemetry()
        tel_full_map = tel_full_d1
        selected_map_driver = DRIVER_1
    
    if map_type == "Velocidad":
        x = pos_map['X'].values
        y = pos_map['Y'].values
        speed = pos_map['Speed'].values
        
        # Rotar 90° para orientación horizontal
        x_rot = y
        y_rot = -x
        x, y = x_rot, y_rot
        
        # Calcular figsize basado en proporciones reales
        x_range = x.max() - x.min()
        y_range = y.max() - y.min()
        max_width = 10
        max_height = 3.5
        
        if x_range / y_range > max_width / max_height:
            fig_width = max_width
            fig_height = max_width * (y_range / x_range)
        else:
            fig_height = max_height
            fig_width = max_height * (x_range / y_range)
        
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        fig, ax = plt.subplots(figsize=(fig_width + 0.8, fig_height))
        
        # Colormap plasma (como en el notebook)
        norm = plt.Normalize(speed.min(), speed.max())
        cmap = colormaps['plasma']
        
        # Circuito base (sombra)
        ax.plot(x, y, color='#2A2A35', linewidth=8, solid_capstyle='round', zorder=1)
        
        lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=4, zorder=2)
        lc.set_array(speed)
        ax.add_collection(lc)
        
        ax.set_xlim(x.min() - 50, x.max() + 50)
        ax.set_ylim(y.min() - 50, y.max() + 50)
        ax.set_aspect('equal')
        ax.axis('off')
        
        cbar = fig.colorbar(lc, ax=ax, orientation='vertical', fraction=0.03, pad=0.02)
        cbar.set_label('km/h', fontsize=8)
        cbar.outline.set_edgecolor('#E10600')
        
        ax.set_title(f'VELOCIDAD — {selected_map_driver}', fontsize=10, fontweight='bold', color='#E10600')
        plt.tight_layout()
        
    elif map_type == "Mini-Sectores (Comparación)":
        if len(SELECTED_DRIVERS) < 2:
            st.info("Selecciona al menos 2 pilotos para la comparación de mini-sectores")
            fig, ax = plt.subplots(figsize=(10, 3.5))
            ax.text(0.5, 0.5, "Selecciona 2 pilotos", ha='center', va='center', fontsize=14, color='white')
            ax.axis('off')
        else:
            # Seleccionar dos pilotos para comparar
            col1, col2 = st.columns(2)
            with col1:
                compare_driver_1 = st.selectbox("Piloto 1:", SELECTED_DRIVERS, index=0, key="map_compare_1")
            with col2:
                other_drivers = [d for d in SELECTED_DRIVERS if d != compare_driver_1]
                compare_driver_2 = st.selectbox("Piloto 2:", other_drivers, index=0 if other_drivers else None, key="map_compare_2")
            
            try:
                lap_c1 = session.laps.pick_driver(compare_driver_1).pick_fastest()
                lap_c2 = session.laps.pick_driver(compare_driver_2).pick_fastest()
                pos_c1 = lap_c1.get_telemetry()
                pos_c2 = lap_c2.get_telemetry()
                color_c1 = TEAM_COLORS.get(lap_c1['Team'], '#FFFFFF')
                color_c2 = TEAM_COLORS.get(lap_c2['Team'], '#00FF00')
            except:
                pos_c1 = pos_map
                pos_c2 = pos_map
                color_c1 = '#FFFFFF'
                color_c2 = '#00FF00'
            
            speed_c1 = pos_c1['Speed'].values
            distance_c1 = pos_c1['Distance'].values
            speed_c2_interp = np.interp(distance_c1, pos_c2['Distance'].values, pos_c2['Speed'].values)
            
            faster = np.where(speed_c1 >= speed_c2_interp, 1, -1)
            
            x = pos_c1['X'].values
            y = pos_c1['Y'].values
            
            # Rotar 90° para orientación horizontal
            x_rot = y
            y_rot = -x
            x, y = x_rot, y_rot
            
            # Calcular figsize basado en proporciones reales
            x_range = x.max() - x.min()
            y_range = y.max() - y.min()
            max_width = 10
            max_height = 3.5
            
            if x_range / y_range > max_width / max_height:
                fig_width = max_width
                fig_height = max_width * (y_range / x_range)
            else:
                fig_height = max_height
                fig_width = max_height * (x_range / y_range)
            
            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            
            fig, ax = plt.subplots(figsize=(fig_width + 0.8, fig_height))
            
            # Circuito base (sombra)
            ax.plot(x, y, color='#2A2A35', linewidth=8, solid_capstyle='round', zorder=1)
            
            from matplotlib.colors import ListedColormap
            cmap_custom = ListedColormap([color_c2, color_c1])
            norm = plt.Normalize(-1, 1)
            
            lc = LineCollection(segments, cmap=cmap_custom, norm=norm, linewidth=4, zorder=2)
            lc.set_array(faster)
            ax.add_collection(lc)
            
            ax.set_xlim(x.min() - 50, x.max() + 50)
            ax.set_ylim(y.min() - 50, y.max() + 50)
            ax.set_aspect('equal')
            ax.axis('off')
            
            legend_elements = [
                mpatches.Patch(facecolor=color_c1, edgecolor='white', linewidth=1, label=compare_driver_1),
                mpatches.Patch(facecolor=color_c2, edgecolor='white', linewidth=1, label=compare_driver_2)
            ]
            ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.01, 0.5),
                     fontsize=8, framealpha=0.9, edgecolor='#E10600', title='MÁS RÁPIDO', title_fontsize=8)
            ax.set_title(f'MINI-SECTORES — {compare_driver_1} vs {compare_driver_2}', fontsize=10, fontweight='bold', color='#E10600')
            plt.tight_layout()
        
    else:  # Marchas
        x = pos_map['X'].values
        y = pos_map['Y'].values
        gear = tel_full_map['nGear'].values
        
        # Rotar 90° para orientación horizontal
        x_rot = y
        y_rot = -x
        x, y = x_rot, y_rot
        
        # Calcular figsize basado en proporciones reales
        x_range = x.max() - x.min()
        y_range = y.max() - y.min()
        max_width = 10
        max_height = 3.5
        
        if x_range / y_range > max_width / max_height:
            fig_width = max_width
            fig_height = max_width * (y_range / x_range)
        else:
            fig_height = max_height
            fig_width = max_height * (x_range / y_range)
        
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        fig, ax = plt.subplots(figsize=(fig_width + 0.8, fig_height))
        
        # Circuito base (sombra)
        ax.plot(x, y, color='#2A2A35', linewidth=8, solid_capstyle='round', zorder=1)
        
        # Colormap viridis para marchas (como en el notebook)
        cmap = colormaps['viridis']
        norm = plt.Normalize(1, 8)
        
        lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=4, zorder=2)
        lc.set_array(gear)
        ax.add_collection(lc)
        
        ax.set_xlim(x.min() - 50, x.max() + 50)
        ax.set_ylim(y.min() - 50, y.max() + 50)
        ax.set_aspect('equal')
        ax.axis('off')
        
        cbar = fig.colorbar(lc, ax=ax, orientation='vertical', fraction=0.03, pad=0.02, ticks=range(1, 9))
        cbar.set_label('MARCHA', fontsize=8)
        cbar.outline.set_edgecolor('#E10600')
        
        ax.set_title(f'MARCHAS — {selected_map_driver}', fontsize=10, fontweight='bold', color='#E10600')
        plt.tight_layout()
    
    st.pyplot(fig)
    plt.close()

# TAB: Vuelta Perfecta
with tab_perfecta:
    st.subheader("⚡ Análisis de Vuelta Perfecta")
    
    NUM_MINISECTORS = st.slider("Número de mini-sectores", 10, 50, 25)
    
    @st.cache_data(ttl=3600)
    def calculate_perfect_lap(_session, num_sectors):
        all_fastest = []
        pilot_colors = {}
        
        for drv in _session.drivers:
            try:
                drv_laps = _session.laps.pick_driver(drv)
                if len(drv_laps) > 0:
                    fastest = drv_laps.pick_fastest()
                    if fastest is not None and not pd.isna(fastest['LapTime']):
                        all_fastest.append({
                            'driver': fastest['Driver'],
                            'team': fastest['Team'],
                            'lap_time': fastest['LapTime'],
                            'lap_data': fastest
                        })
                        pilot_colors[fastest['Driver']] = TEAM_COLORS.get(fastest['Team'], '#FFFFFF')
            except:
                continue
        
        all_fastest = sorted(all_fastest, key=lambda x: x['lap_time'])
        
        # Calcular mini-sectores
        base_tel = all_fastest[0]['lap_data'].get_car_data().add_distance()
        total_distance = base_tel['Distance'].max()
        sector_length = total_distance / num_sectors
        
        minisector_data = []
        
        for lap_info in all_fastest:
            try:
                tel = lap_info['lap_data'].get_car_data().add_distance()
                tel_time = (tel['Time'] - tel['Time'].iloc[0]).dt.total_seconds().values
                tel_dist = tel['Distance'].values
                
                for ms in range(num_sectors):
                    ms_start = ms * sector_length
                    ms_end = (ms + 1) * sector_length
                    
                    if ms_start < tel_dist.min() or ms_end > tel_dist.max():
                        continue
                    
                    time_start = np.interp(ms_start, tel_dist, tel_time)
                    time_end = np.interp(ms_end, tel_dist, tel_time)
                    ms_time = time_end - time_start
                    
                    minisector_data.append({
                        'driver': lap_info['driver'],
                        'team': lap_info['team'],
                        'minisector': ms + 1,
                        'time': ms_time,
                        'distance_start': ms_start,
                        'distance_end': ms_end
                    })
            except:
                continue
        
        df_ms = pd.DataFrame(minisector_data)
        perfect = df_ms.loc[df_ms.groupby('minisector')['time'].idxmin()]
        perfect = perfect.sort_values('minisector').reset_index(drop=True)
        
        return df_ms, perfect, all_fastest, pilot_colors, base_tel
    
    with st.spinner("Calculando vuelta perfecta..."):
        df_minisectors, perfect_lap, all_fastest, pilot_colors, base_tel = calculate_perfect_lap(
            session, NUM_MINISECTORS
        )
    
    perfect_time = perfect_lap['time'].sum()
    pole_time = all_fastest[0]['lap_time'].total_seconds()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⚡ Vuelta Perfecta Teórica", f"{perfect_time:.3f}s")
    with col2:
        st.metric(f"🏆 Pole ({all_fastest[0]['driver']})", f"{pole_time:.3f}s")
    with col3:
        st.metric("📉 Diferencia", f"+{pole_time - perfect_time:.3f}s")
    
    # Dominio por piloto
    st.markdown("### 📊 Dominio por Mini-Sector")
    driver_counts = perfect_lap['driver'].value_counts()
    
    # Gráfico de barras interactivo con Plotly
    colors_bars = [pilot_colors.get(d, '#FFFFFF') for d in driver_counts.index]
    
    fig_bars = go.Figure()
    fig_bars.add_trace(go.Bar(
        y=driver_counts.index[::-1],
        x=driver_counts.values[::-1],
        orientation='h',
        marker=dict(
            color=colors_bars[::-1],
            line=dict(color='#E10600', width=2)
        ),
        text=driver_counts.values[::-1],
        textposition='outside',
        textfont=dict(size=12, color='#E10600', family='Titillium Web'),
        hovertemplate='%{y}: %{x} sectores<extra></extra>'
    ))
    
    fig_bars.update_layout(
        height=250,
        paper_bgcolor='#15151E', plot_bgcolor='#15151E',
        font=dict(family='Titillium Web, sans-serif', color='#FFFFFF'),
        xaxis=dict(
            title=dict(text='SECTORES DOMINADOS', font=dict(size=11)),
            gridcolor='#38383F',
            linecolor='#E10600'
        ),
        yaxis=dict(gridcolor='#38383F', linecolor='#E10600'),
        margin=dict(l=80, r=40, t=20, b=50),
        shapes=[dict(type='line', x0=0, y0=-0.5, x1=0, y1=len(driver_counts)-0.5, line=dict(color='#E10600', width=3))]
    )
    
    st.plotly_chart(fig_bars, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
    
    # Mapa de vuelta perfecta
    st.markdown("### 🗺️ Mapa de la Vuelta Perfecta")
    
    # Obtener telemetría con posición del mejor piloto
    try:
        map_tel = all_fastest[0]['lap_data'].get_telemetry()
        base_x = map_tel['X'].values
        base_y = map_tel['Y'].values
        base_dist = map_tel['Distance'].values
        
        # Rotar 90° para orientación horizontal
        base_x_rot = base_y.copy()
        base_y_rot = -base_x.copy()
        base_x, base_y = base_x_rot, base_y_rot
        
        # Calcular figsize basado en proporciones reales
        x_range = base_x.max() - base_x.min()
        y_range = base_y.max() - base_y.min()
        max_width = 10
        max_height = 3.5
        
        if x_range / y_range > max_width / max_height:
            fig_width = max_width
            fig_height = max_width * (y_range / x_range)
        else:
            fig_height = max_height
            fig_width = max_height * (x_range / y_range)
        
        fig, ax = plt.subplots(figsize=(fig_width + 1, fig_height))
        
        # Circuito base (sombra)
        ax.plot(base_x, base_y, color='#2A2A35', linewidth=10, solid_capstyle='round', zorder=1)
        
        for _, row in perfect_lap.iterrows():
            mask = (base_dist >= row['distance_start']) & (base_dist < row['distance_end'])
            if mask.sum() > 1:
                x_seg = base_x[mask]
                y_seg = base_y[mask]
                color = pilot_colors.get(row['driver'], '#FFFFFF')
                # Borde blanco para resaltar
                ax.plot(x_seg, y_seg, color='white', linewidth=7, solid_capstyle='round', zorder=2, alpha=0.3)
                ax.plot(x_seg, y_seg, color=color, linewidth=5, solid_capstyle='round', zorder=3)
        
        unique_drivers = perfect_lap['driver'].unique()
        legend_patches = [mpatches.Patch(color=pilot_colors.get(d, '#FFFFFF'), 
                                         edgecolor='white', linewidth=1, label=d) for d in unique_drivers]
        ax.legend(handles=legend_patches, loc='center left', bbox_to_anchor=(1.01, 0.5),
                 fontsize=8, framealpha=0.9, edgecolor='#E10600', title='MEJOR EN SECTOR', title_fontsize=8)
        
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'VUELTA PERFECTA — {perfect_time:.3f}s', fontsize=10, fontweight='bold', color='#E10600')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    except Exception as e:
        st.warning(f"No se pudo generar el mapa: {e}")

# TAB: Degradación de Neumáticos
with tab_degradacion:
    st.subheader("📉 Análisis de Degradación de Neumáticos")
    
    # Verificar si hay datos de carrera disponibles
    st.info("📊 Este análisis requiere datos de carrera para mostrar la evolución de tiempos por vuelta.")
    
    try:
        with st.spinner("Cargando datos de carrera..."):
            @st.cache_data(ttl=3600)
            def load_race_data(_year, _gp):
                race = fastf1.get_session(_year, _gp, 'R')
                race.load()
                return race
            
            race = load_race_data(year, gp)
        
        # Selector de piloto para análisis
        race_driver = st.selectbox(
            "Seleccionar piloto para análisis de degradación:",
            options=SELECTED_DRIVERS,
            key="race_driver"
        )
        
        # Obtener vueltas del piloto
        driver_laps = race.laps.pick_driver(race_driver).pick_quicklaps().reset_index()
        
        if len(driver_laps) > 0:
            # Convertir tiempos a segundos
            driver_laps['LapTimeSeconds'] = driver_laps['LapTime'].dt.total_seconds()
            
            # Filtrar vueltas válidas
            median_time = driver_laps['LapTimeSeconds'].median()
            driver_laps = driver_laps[driver_laps['LapTimeSeconds'] < median_time * 1.1]
            
            # Colores de compuestos
            compound_colors = {
                'SOFT': '#FF3333', 'MEDIUM': '#FFFF33', 'HARD': '#FFFFFF',
                'INTERMEDIATE': '#33FF33', 'WET': '#3333FF'
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de tiempos brutos
                fig_deg1 = go.Figure()
                
                for compound in driver_laps['Compound'].unique():
                    mask = driver_laps['Compound'] == compound
                    color = compound_colors.get(compound, '#888888')
                    fig_deg1.add_trace(go.Scatter(
                        x=driver_laps.loc[mask, 'LapNumber'],
                        y=driver_laps.loc[mask, 'LapTimeSeconds'],
                        mode='markers',
                        name=compound,
                        marker=dict(color=color, size=8, line=dict(color='black', width=1)),
                        hovertemplate='Vuelta %{x}<br>Tiempo: %{y:.3f}s<extra></extra>'
                    ))
                
                fig_deg1.update_layout(
                    title=f'Tiempos de Vuelta - {race_driver}',
                    xaxis_title='Número de Vuelta',
                    yaxis_title='Tiempo (s)',
                    yaxis=dict(autorange='reversed'),
                    height=350,
                    paper_bgcolor='#15151E', plot_bgcolor='#15151E',
                    font=dict(color='#FFFFFF'),
                    legend=dict(bgcolor='rgba(21,21,30,0.95)', font=dict(color='#FFFFFF'))
                )
                st.plotly_chart(fig_deg1, use_container_width=True)
            
            with col2:
                # Gráfico con corrección de combustible
                FUEL_CORRECTION = 0.03
                driver_laps['LapTimeCorrected'] = driver_laps['LapTimeSeconds'] + (driver_laps['LapNumber'] * FUEL_CORRECTION)
                
                fig_deg2 = go.Figure()
                
                for compound in driver_laps['Compound'].unique():
                    mask = driver_laps['Compound'] == compound
                    color = compound_colors.get(compound, '#888888')
                    fig_deg2.add_trace(go.Scatter(
                        x=driver_laps.loc[mask, 'LapNumber'],
                        y=driver_laps.loc[mask, 'LapTimeCorrected'],
                        mode='markers',
                        name=compound,
                        marker=dict(color=color, size=8, line=dict(color='black', width=1)),
                        hovertemplate='Vuelta %{x}<br>Tiempo corregido: %{y:.3f}s<extra></extra>'
                    ))
                
                fig_deg2.update_layout(
                    title=f'Tiempos Corregidos (+{FUEL_CORRECTION}s/vuelta)',
                    xaxis_title='Número de Vuelta',
                    yaxis_title='Tiempo Corregido (s)',
                    height=350,
                    paper_bgcolor='#15151E', plot_bgcolor='#15151E',
                    font=dict(color='#FFFFFF'),
                    legend=dict(bgcolor='rgba(21,21,30,0.95)', font=dict(color='#FFFFFF'))
                )
                st.plotly_chart(fig_deg2, use_container_width=True)
            
            # Estadísticas por stint
            st.markdown("### 📊 Resumen por Compuesto")
            stint_stats = driver_laps.groupby('Compound').agg({
                'LapTimeSeconds': ['count', 'min', 'mean', 'max'],
                'LapNumber': ['min', 'max']
            }).round(3)
            stint_stats.columns = ['Vueltas', 'Mejor', 'Media', 'Peor', 'Inicio', 'Fin']
            st.dataframe(stint_stats, use_container_width=True)
        else:
            st.warning("No hay suficientes datos de carrera para este piloto.")
            
    except Exception as e:
        st.error(f"No se pudieron cargar los datos de carrera: {e}")

# TAB: Animación
with tab_animacion:
    st.subheader("🎬 Animación de Vuelta Avanzada")
    
    if len(SELECTED_DRIVERS) < 2:
        st.info("Selecciona al menos 2 pilotos para ver la animación comparativa")
    else:
        # Selectores de piloto para animación
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            anim_driver_1 = st.selectbox("Piloto 1:", SELECTED_DRIVERS, index=0, key="anim_driver_1")
        with col_sel2:
            other_anim_drivers = [d for d in SELECTED_DRIVERS if d != anim_driver_1]
            anim_driver_2 = st.selectbox("Piloto 2:", other_anim_drivers, index=0, key="anim_driver_2")
        
        # Cargar datos de los pilotos para animación
        try:
            lap_anim_1 = session.laps.pick_driver(anim_driver_1).pick_fastest()
            lap_anim_2 = session.laps.pick_driver(anim_driver_2).pick_fastest()
            color_anim_1 = TEAM_COLORS.get(lap_anim_1['Team'], '#FFFFFF')
            color_anim_2 = TEAM_COLORS.get(lap_anim_2['Team'], '#00FF00')
        except:
            lap_anim_1, lap_anim_2 = lap_d1, lap_d2
            color_anim_1, color_anim_2 = color_d1, color_d2
        
        # Obtener telemetría completa
        tel_anim_1 = lap_anim_1.get_car_data().add_distance()
        tel_anim_2 = lap_anim_2.get_car_data().add_distance()
        pos_anim_1 = lap_anim_1.get_telemetry()
        pos_anim_2 = lap_anim_2.get_telemetry()
        
        # Controles de animación
        st.markdown("### ⚙️ Controles")
        col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
        
        with col_ctrl1:
            animation_speed = st.slider("🏎️ Velocidad", 1, 10, 5, key="anim_speed")
        with col_ctrl2:
            show_trail = st.checkbox("💨 Estela", value=True, key="show_trail")
        with col_ctrl3:
            follow_camera = st.checkbox("📹 Cámara seguimiento", value=True, key="follow_cam")
        with col_ctrl4:
            show_telemetry = st.checkbox("📊 Telemetría", value=True, key="show_tel")
        
        # Preparar datos
        time_d1 = (pos_anim_1['Time'] - pos_anim_1['Time'].iloc[0]).dt.total_seconds().values
        time_d2 = (pos_anim_2['Time'] - pos_anim_2['Time'].iloc[0]).dt.total_seconds().values
        
        x_d1, y_d1 = pos_anim_1['X'].values, pos_anim_1['Y'].values
        x_d2, y_d2 = pos_anim_2['X'].values, pos_anim_2['Y'].values
        
        speed_d1 = pos_anim_1['Speed'].values
        speed_d2 = pos_anim_2['Speed'].values
        
        throttle_d1 = tel_anim_1['Throttle'].values
        throttle_d2 = tel_anim_2['Throttle'].values
        
        brake_d1 = tel_anim_1['Brake'].astype(int).values * 100
        brake_d2 = tel_anim_2['Brake'].astype(int).values * 100
        
        gear_d1 = tel_anim_1['nGear'].values
        gear_d2 = tel_anim_2['nGear'].values
        
        # Crear frames de animación
        max_time = max(time_d1[-1], time_d2[-1])
        n_frames = 150
        time_points = np.linspace(0, max_time, n_frames)
        
        # Layout con subplots para animación avanzada
        from plotly.subplots import make_subplots
        
        if show_telemetry:
            fig_anim = make_subplots(
                rows=2, cols=3,
                specs=[
                    [{"rowspan": 2, "colspan": 2}, None, {"type": "indicator"}],
                    [None, None, {"type": "indicator"}]
                ],
                column_widths=[0.4, 0.4, 0.2],
                row_heights=[0.5, 0.5],
                horizontal_spacing=0.02,
                vertical_spacing=0.1
            )
        else:
            fig_anim = go.Figure()
        
        # Circuito de fondo (rotado para horizontal)
        x_circuit = y_d1  # Rotar
        y_circuit = -x_d1
        x_d1_rot, y_d1_rot = y_d1, -x_d1
        x_d2_rot, y_d2_rot = y_d2, -x_d2
        
        # Añadir circuito base
        if show_telemetry:
            fig_anim.add_trace(go.Scatter(
                x=x_circuit, y=y_circuit,
                mode='lines', line=dict(color='#2A2A35', width=12),
                showlegend=False, hoverinfo='skip'
            ), row=1, col=1)
        else:
            fig_anim.add_trace(go.Scatter(
                x=x_circuit, y=y_circuit,
                mode='lines', line=dict(color='#2A2A35', width=12),
                showlegend=False, hoverinfo='skip'
            ))
        
        # Crear frames
        frames = []
        trail_length = 30
        
        # Calcular límites del circuito para cámara
        x_min, x_max = x_circuit.min(), x_circuit.max()
        y_min, y_max = y_circuit.min(), y_circuit.max()
        x_range = x_max - x_min
        y_range = y_max - y_min
        zoom_factor = 0.25  # Porción del circuito visible en zoom
        
        for i, t in enumerate(time_points):
            idx1 = min(np.searchsorted(time_d1, t), len(x_d1) - 1)
            idx2 = min(np.searchsorted(time_d2, t), len(x_d2) - 1)
            
            # Posiciones rotadas
            x1, y1 = y_d1[idx1], -x_d1[idx1]
            x2, y2 = y_d2[idx2], -x_d2[idx2]
            
            trail_start1 = max(0, idx1 - trail_length)
            trail_start2 = max(0, idx2 - trail_length)
            
            frame_data = []
            
            # Circuito base
            frame_data.append(go.Scatter(
                x=x_circuit, y=y_circuit,
                mode='lines', line=dict(color='#2A2A35', width=12),
                showlegend=False, hoverinfo='skip'
            ))
            
            if show_trail:
                # Estela con degradado D1
                trail_x1 = y_d1[trail_start1:idx1+1]
                trail_y1 = -x_d1[trail_start1:idx1+1]
                for j in range(len(trail_x1) - 1):
                    opacity = 0.1 + 0.5 * (j / max(len(trail_x1) - 1, 1))
                    frame_data.append(go.Scatter(
                        x=trail_x1[j:j+2], y=trail_y1[j:j+2],
                        mode='lines', line=dict(color=color_anim_1, width=6),
                        opacity=opacity, showlegend=False, hoverinfo='skip'
                    ))
                
                # Estela con degradado D2
                trail_x2 = y_d2[trail_start2:idx2+1]
                trail_y2 = -x_d2[trail_start2:idx2+1]
                for j in range(len(trail_x2) - 1):
                    opacity = 0.1 + 0.5 * (j / max(len(trail_x2) - 1, 1))
                    frame_data.append(go.Scatter(
                        x=trail_x2[j:j+2], y=trail_y2[j:j+2],
                        mode='lines', line=dict(color=color_anim_2, width=6),
                        opacity=opacity, showlegend=False, hoverinfo='skip'
                    ))
            
            # Indicador de frenada (círculo rojo cuando frena)
            brake_size_1 = 25 if brake_d1[min(idx1, len(brake_d1)-1)] > 50 else 18
            brake_size_2 = 25 if brake_d2[min(idx2, len(brake_d2)-1)] > 50 else 18
            brake_color_1 = '#FF0000' if brake_d1[min(idx1, len(brake_d1)-1)] > 50 else color_anim_1
            brake_color_2 = '#FF0000' if brake_d2[min(idx2, len(brake_d2)-1)] > 50 else color_anim_2
            
            # Coches con indicador de frenada
            frame_data.append(go.Scatter(
                x=[x1], y=[y1],
                mode='markers+text',
                marker=dict(
                    color=brake_color_1, size=brake_size_1,
                    line=dict(color='white', width=2),
                    symbol='circle'
                ),
                text=[anim_driver_1],
                textposition='top center',
                textfont=dict(color='white', size=10, family='Arial Black'),
                name=anim_driver_1, showlegend=(i==0)
            ))
            frame_data.append(go.Scatter(
                x=[x2], y=[y2],
                mode='markers+text',
                marker=dict(
                    color=brake_color_2, size=brake_size_2,
                    line=dict(color='white', width=2),
                    symbol='circle'
                ),
                text=[anim_driver_2],
                textposition='top center',
                textfont=dict(color='white', size=10, family='Arial Black'),
                name=anim_driver_2, showlegend=(i==0)
            ))
            
            # Indicadores de telemetría
            if show_telemetry:
                # Velocímetro D1
                frame_data.append(go.Indicator(
                    mode="gauge+number",
                    value=speed_d1[idx1],
                    title={'text': f"🏎️ {anim_driver_1}", 'font': {'size': 12, 'color': color_anim_1}},
                    number={'suffix': " km/h", 'font': {'size': 20, 'color': 'white'}},
                    gauge={
                        'axis': {'range': [0, 360], 'tickcolor': 'white'},
                        'bar': {'color': color_anim_1},
                        'bgcolor': '#1E1E2E',
                        'bordercolor': '#E10600',
                        'steps': [
                            {'range': [0, 120], 'color': '#2A2A35'},
                            {'range': [120, 240], 'color': '#3A3A45'},
                            {'range': [240, 360], 'color': '#4A4A55'}
                        ],
                        'threshold': {
                            'line': {'color': '#E10600', 'width': 2},
                            'value': 340
                        }
                    },
                    domain={'row': 0, 'column': 2}
                ))
                
                # Velocímetro D2
                frame_data.append(go.Indicator(
                    mode="gauge+number",
                    value=speed_d2[idx2],
                    title={'text': f"🏎️ {anim_driver_2}", 'font': {'size': 12, 'color': color_anim_2}},
                    number={'suffix': " km/h", 'font': {'size': 20, 'color': 'white'}},
                    gauge={
                        'axis': {'range': [0, 360], 'tickcolor': 'white'},
                        'bar': {'color': color_anim_2},
                        'bgcolor': '#1E1E2E',
                        'bordercolor': '#E10600',
                        'steps': [
                            {'range': [0, 120], 'color': '#2A2A35'},
                            {'range': [120, 240], 'color': '#3A3A45'},
                            {'range': [240, 360], 'color': '#4A4A55'}
                        ]
                    },
                    domain={'row': 1, 'column': 2}
                ))
            
            # Calcular rango de cámara si está activada
            if follow_camera:
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                view_range_x = x_range * zoom_factor
                view_range_y = y_range * zoom_factor
                
                frame_layout = {
                    'xaxis': {
                        'range': [center_x - view_range_x/2, center_x + view_range_x/2],
                        'scaleanchor': 'y', 'scaleratio': 1,
                        'showgrid': False, 'zeroline': False, 'visible': False
                    },
                    'yaxis': {
                        'range': [center_y - view_range_y/2, center_y + view_range_y/2],
                        'showgrid': False, 'zeroline': False, 'visible': False
                    }
                }
                frames.append(go.Frame(data=frame_data, name=str(i), layout=frame_layout))
            else:
                frames.append(go.Frame(data=frame_data, name=str(i)))
        
        fig_anim.frames = frames
        
        # Layout principal
        layout_update = {
            'updatemenus': [{
                'type': 'buttons',
                'showactive': True,
                'y': 1.12,
                'x': 0.5,
                'xanchor': 'center',
                'bgcolor': '#1E1E2E',
                'bordercolor': '#E10600',
                'font': {'color': 'white'},
                'buttons': [
                    {
                        'label': '▶️ PLAY',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 80 // animation_speed, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 0}
                        }]
                    },
                    {
                        'label': '⏸️ PAUSE',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    },
                    {
                        'label': '🔄 RESET',
                        'method': 'animate',
                        'args': [['0'], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }],
            'sliders': [{
                'active': 0,
                'bgcolor': '#1E1E2E',
                'bordercolor': '#E10600',
                'font': {'color': 'white'},
                'steps': [{'args': [[str(i)], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate'}],
                          'label': f'{time_points[i]:.1f}s', 'method': 'animate'} for i in range(0, n_frames, 5)],
                'x': 0.1, 'len': 0.8,
                'currentvalue': {
                    'prefix': '⏱️ Tiempo: ',
                    'visible': True,
                    'xanchor': 'center',
                    'font': {'color': 'white', 'size': 14}
                },
                'transition': {'duration': 0}
            }],
            'height': 600 if show_telemetry else 500,
            'paper_bgcolor': '#15151E',
            'plot_bgcolor': '#15151E',
            'font': {'color': '#FFFFFF', 'family': 'Arial'},
            'legend': {'bgcolor': 'rgba(21,21,30,0.95)', 'x': 0.02, 'y': 0.98, 'font': {'color': '#FFFFFF'}},
            'margin': {'l': 20, 'r': 20, 't': 80, 'b': 20},
            'title': {
                'text': f'🏁 {anim_driver_1} vs {anim_driver_2}',
                'font': {'size': 18, 'color': '#E10600'},
                'x': 0.5
            }
        }
        
        if not follow_camera:
            layout_update['xaxis'] = {'scaleanchor': 'y', 'scaleratio': 1, 'showgrid': False, 'zeroline': False, 'visible': False}
            layout_update['yaxis'] = {'showgrid': False, 'zeroline': False, 'visible': False}
        
        fig_anim.update_layout(**layout_update)
        
        # Añadir traces iniciales
        fig_anim.add_trace(go.Scatter(
            x=[y_d1[0]], y=[-x_d1[0]],
            mode='markers+text',
            marker=dict(color=color_anim_1, size=18, line=dict(color='white', width=2)),
            text=[anim_driver_1], textposition='top center',
            textfont=dict(color='white', size=10),
            name=anim_driver_1
        ))
        fig_anim.add_trace(go.Scatter(
            x=[y_d2[0]], y=[-x_d2[0]],
            mode='markers+text',
            marker=dict(color=color_anim_2, size=18, line=dict(color='white', width=2)),
            text=[anim_driver_2], textposition='top center',
            textfont=dict(color='white', size=10),
            name=anim_driver_2
        ))
        
        st.plotly_chart(fig_anim, use_container_width=True)
        
        # Panel de información
        st.markdown("---")
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color_anim_1}22, #15151E); padding: 15px; border-radius: 10px; border-left: 4px solid {color_anim_1};'>
                <h4 style='color: {color_anim_1}; margin: 0;'>🏎️ {anim_driver_1}</h4>
                <p style='color: white; margin: 5px 0;'>⏱️ {str(lap_anim_1['LapTime'])[-12:-3]}</p>
                <p style='color: #888; margin: 0; font-size: 12px;'>{lap_anim_1['Team']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_info2:
            # Calcular delta
            delta_time = (lap_anim_2['LapTime'] - lap_anim_1['LapTime']).total_seconds()
            delta_color = '#00FF00' if delta_time > 0 else '#FF0000'
            delta_sign = '+' if delta_time > 0 else ''
            st.markdown(f"""
            <div style='background: #1E1E2E; padding: 15px; border-radius: 10px; text-align: center;'>
                <h4 style='color: #E10600; margin: 0;'>⚡ DELTA</h4>
                <p style='color: {delta_color}; font-size: 24px; font-weight: bold; margin: 10px 0;'>{delta_sign}{delta_time:.3f}s</p>
                <p style='color: #888; margin: 0; font-size: 12px;'>{'🏆 ' + anim_driver_1 + ' más rápido' if delta_time > 0 else '🏆 ' + anim_driver_2 + ' más rápido'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_info3:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color_anim_2}22, #15151E); padding: 15px; border-radius: 10px; border-left: 4px solid {color_anim_2};'>
                <h4 style='color: {color_anim_2}; margin: 0;'>🏎️ {anim_driver_2}</h4>
                <p style='color: white; margin: 5px 0;'>⏱️ {str(lap_anim_2['LapTime'])[-12:-3]}</p>
                <p style='color: #888; margin: 0; font-size: 12px;'>{lap_anim_2['Team']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Leyenda de indicadores
        st.markdown("""
        <div style='background: #1E1E2E; padding: 10px; border-radius: 5px; margin-top: 10px;'>
            <span style='color: #888; font-size: 12px;'>
                💡 <b>Indicadores:</b> 
                🔴 Frenando | 
                💨 Estela = trayectoria reciente |
                📹 Cámara seguimiento = zoom dinámico
            </span>
        </div>
        """, unsafe_allow_html=True)

# TAB: Clasificación
with tab_clasificacion:
    st.subheader("📈 Clasificación de la Sesión")
    
    # Crear DataFrame de clasificación
    df_classification = pd.DataFrame(drivers_info)
    df_classification.index = range(1, len(df_classification) + 1)
    df_classification.columns = ['Piloto', 'Equipo', 'Tiempo', 'Tiempo (str)']
    
    # Calcular diferencias
    if len(df_classification) > 0:
        pole_time = df_classification.iloc[0]['Tiempo']
        df_classification['Gap'] = df_classification['Tiempo'].apply(
            lambda x: f"+{(x - pole_time).total_seconds():.3f}s" if x != pole_time else "-"
        )
    
    st.dataframe(
        df_classification[['Piloto', 'Equipo', 'Tiempo (str)', 'Gap']],
        width='stretch',
        height=350
    )

# Footer
st.markdown(
    """
    <div class='footer-text'>
        <span style='color: #E10600; font-weight: bold;'>🏎️ F1 TELEMETRY DASHBOARD</span> · 
        <span>Powered by FastF1 & Streamlit | Datos: © Formula 1</span>
    </div>
    """,
    unsafe_allow_html=True
)
