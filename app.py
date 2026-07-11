import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import warnings
warnings.filterwarnings("ignore")

BACKGROUND_IMAGE_PATH = "assets/holi_fondo.png"
LOGO_IMAGE_PATH = "assets/holilogo.png"
FAVICON_PATH = "assets/pestaña.png"

# Importar módulos propios
from modules.etl import (
    validar_columnas,
    diagnosticar_dataset,
    aplicar_etl,
)
from modules.analisis import (
    calcular_kpis,
    analisis_abc,
    resumen_abc,
    analisis_rotacion,
    top_productos,
    ventas_por_sucursal,
    ventas_por_categoria,
    analisis_temporal,
    ventas_por_metodo_pago,
)
from modules.prediccion import (
    PROPHET_DISPONIBLE,
    predecir_demanda,
    obtener_prediccion_futura,
    resumen_prediccion,
)
from modules.reportes import generar_pdf_ejecutivo
from modules.database import cargar_datos


def aplicar_tema(fig):
    """Aplica el tema cálido de Holi a cualquier gráfico Plotly."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,248,240,0.6)",
        font=dict(family="Inter, sans-serif", color="#4a3828"),
        title_font=dict(size=15, color="#7b3e1b", family="Inter, sans-serif"),
        xaxis=dict(
            gridcolor="rgba(219,160,106,0.18)",
            linecolor="rgba(219,160,106,0.3)",
            tickfont=dict(color="#8a6040", size=11),
            title_font=dict(color="#8a6040"),
        ),
        yaxis=dict(
            gridcolor="rgba(219,160,106,0.18)",
            linecolor="rgba(219,160,106,0.3)",
            tickfont=dict(color="#8a6040", size=11),
            title_font=dict(color="#8a6040"),
        ),
        legend=dict(
            bgcolor="rgba(255,248,240,0.85)",
            bordercolor="rgba(219,160,106,0.3)",
            borderwidth=1,
            font=dict(color="#4a3828"),
        ),
        margin=dict(t=40, b=20, l=10, r=10),
    )
    return fig


# ================================================================
# CONFIGURACIÓN GENERAL DE LA APP
# ================================================================
from PIL import Image as PILImage

_favicon = None
try:
    _favicon = PILImage.open(FAVICON_PATH)
except Exception:
    _favicon = "🛒"

st.set_page_config(
    page_title="Holi Intelligence Platform",
    layout="wide",
    page_icon=_favicon,
    initial_sidebar_state="expanded",
)


def get_base64_image(path):
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


# ================================================================
# ESTILOS PERSONALIZADOS
# ================================================================
image_base64 = get_base64_image(BACKGROUND_IMAGE_PATH)
logo_base64 = get_base64_image(LOGO_IMAGE_PATH)
# Construir el CSS del fondo dinámicamente con la imagen real
if image_base64:
    fondo_estilo = f"""
        background:
            linear-gradient(135deg, rgba(255, 240, 220, 0.85), rgba(255, 220, 180, 0.85)),
            url("data:image/png;base64,{image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    """
else:
    fondo_estilo = """
        background: radial-gradient(circle at top left, #ffe3c0 0%, #ffd09b 24%, #ffe5cd 56%, #fff2e9 100%);
        background-attachment: fixed;
    """

background_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* FONDO PRINCIPAL */
    .stApp {{
        {fondo_estilo}
        color: #4a3f35;
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }}

    /* ANIMACIÓN ENTRADA */
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(18px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes shimmer {{
        0%   {{ background-position: -400px 0; }}
        100% {{ background-position: 400px 0; }}
    }}

    /* HERO CARD */
    .hero-card {{
        max-width: 1080px;
        margin: 0 auto 28px auto;
        padding: 36px 44px;
        background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%);
        border: 1px solid rgba(219, 160, 106, 0.22);
        border-radius: 28px;
        box-shadow:
            0 2px 8px rgba(180,100,30,0.06),
            0 16px 48px rgba(180,100,30,0.10);
        animation: fadeUp 0.6s ease both;
        position: relative;
        overflow: hidden;
    }}
    .hero-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #FF9E0F, #D35400, #ff6b1a, #FF9E0F);
        background-size: 400px 100%;
        animation: shimmer 3s infinite linear;
    }}
    .hero-card::after {{
        content: '';
        position: absolute;
        top: -80px; right: -80px;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(255,158,15,0.10) 0%, transparent 70%);
        pointer-events: none;
    }}
    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        background: linear-gradient(135deg, rgba(255,158,15,0.12), rgba(211,84,0,0.08));
        border: 1px solid rgba(211, 84, 0, 0.20);
        border-radius: 100px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #c45a10;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }}
    .hero-title {{
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.08;
        color: #3d1f08;
        margin: 0;
        letter-spacing: -0.025em;
    }}
    .hero-title span {{
        background: linear-gradient(135deg, #FF9E0F 0%, #D35400 60%, #c23a00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .hero-subtitle {{
        font-size: 0.95rem;
        margin-top: 10px;
        color: #9a7050;
        font-weight: 400;
    }}

    /* TARJETAS KPI */
    .tarjeta-kpi {{
        padding: 24px 18px;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        transition: transform 0.28s ease, box-shadow 0.28s ease;
        animation: fadeUp 0.5s ease both;
        position: relative;
        overflow: hidden;
    }}
    .tarjeta-kpi::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, #FF9E0F 0%, #D35400 55%, #b83000 100%);
        z-index: 0;
    }}
    .tarjeta-kpi::after {{
        content: '';
        position: absolute;
        top: -30px; right: -30px;
        width: 100px; height: 100px;
        background: rgba(255,255,255,0.10);
        border-radius: 50%;
    }}
    .tarjeta-kpi > * {{ position: relative; z-index: 1; }}
    .tarjeta-kpi:hover {{
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 20px 48px rgba(211,84,0,0.30) !important;
    }}
    .kpi-valor {{
        font-size: 2rem;
        font-weight: 800;
        color: white !important;
        letter-spacing: -0.02em;
    }}
    .kpi-etiqueta {{
        font-size: 0.70rem;
        font-weight: 600;
        color: rgba(255,255,255,0.82) !important;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin-bottom: 6px;
    }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(160deg, #ffffff 0%, #fff5ea 60%, #ffe8cc 100%) !important;
        border-right: 1px solid rgba(219, 160, 106, 0.25) !important;
        box-shadow: 4px 0 32px rgba(180, 100, 30, 0.08) !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #5e3b1a !important;
    }}
    .sidebar-brand {{
        background: linear-gradient(135deg, #FF9E0F 0%, #D35400 100%);
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 6px 20px rgba(211,84,0,0.25);
    }}
    .sidebar-title {{
        font-size: 1.35rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.02em;
        margin-bottom: 2px;
    }}
    .sidebar-subtitle {{
        font-size: 0.75rem;
        color: rgba(255,255,255,0.80) !important;
        font-weight: 500;
    }}
    .sidebar-info {{
        background: rgba(255,255,255,0.70);
        border: 1px solid rgba(219, 160, 106, 0.22);
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 10px;
        backdrop-filter: blur(4px);
    }}
    .sidebar-info-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        font-size: 0.81rem;
        border-bottom: 1px solid rgba(219, 160, 106, 0.12);
    }}
    .sidebar-info-row:last-child {{ border-bottom: none; }}
    .sidebar-label {{ color: #a07850 !important; font-weight: 500; }}
    .sidebar-value {{ color: #7b3e1b !important; font-weight: 700; }}

    /* CONTENEDOR PRINCIPAL */
    .block-container {{
        backdrop-filter: blur(12px);
        background: rgba(255, 252, 248, 0.82) !important;
        border-radius: 28px;
        padding: 30px !important;
        margin-top: 18px !important;
        box-shadow: 0 4px 32px rgba(180, 100, 30, 0.07);
    }}

    /* TÍTULOS */
    h1, h2, h3, h4, h5, h6 {{
        color: #7b3e1b !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }}

    /* MÉTRICAS */
    [data-testid="stMetric"] {{
        background: rgba(255, 245, 230, 0.9) !important;
        border: 1px solid rgba(219, 160, 106, 0.25) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        box-shadow: 0 4px 14px rgba(180, 100, 30, 0.08) !important;
        transition: transform 0.2s ease !important;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-2px) !important;
    }}
    [data-testid="stMetricValue"] {{
        color: #7b3e1b !important;
        font-weight: 700 !important;
    }}

    /* LOGO TOP RIGHT */
    .logo-top-right {{
        position: fixed;
        top: 18px;
        right: 24px;
        z-index: 999;
        width: 110px;
        height: 110px;
        padding: 8px;
        border-radius: 50%;
        background: rgba(255, 250, 242, 0.96);
        border: 2px solid rgba(255, 158, 15, 0.35);
        box-shadow:
            0 4px 12px rgba(180, 100, 30, 0.14),
            0 12px 32px rgba(180, 100, 30, 0.10);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .logo-top-right:hover {{
        transform: scale(1.06);
        box-shadow: 0 8px 28px rgba(211, 84, 0, 0.22);
    }}
    .logo-top-right img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 50%;
    }}

    /* OCULTAR menú y header */
    #MainMenu {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}

    /* DIVIDER */
    hr {{ border-color: rgba(219, 160, 106, 0.25) !important; }}

    /* EXPANDER */
    details, [data-testid="stExpander"] {{
        background: rgba(255,248,240,0.95) !important;
        border: 1px solid rgba(219,160,106,0.25) !important;
        border-radius: 14px !important;
    }}
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {{
        color: #7b3e1b !important;
        font-weight: 600 !important;
    }}
    [data-testid="stExpander"] > div {{
        background: rgba(255,248,240,0.95) !important;
    }}

    /* DATAFRAME / TABLAS */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] iframe,
    .stDataFrame > div {{
        background: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(219,160,106,0.2) !important;
    }}
    [data-testid="stDataFrame"] th {{
        background: rgba(255,235,210,0.8) !important;
        color: #7b3e1b !important;
        font-weight: 700 !important;
    }}
    [data-testid="stDataFrame"] td {{
        color: #4a3828 !important;
        background: #ffffff !important;
    }}

    /* ALERTAS CON TEMA CÁLIDO */
    .alerta-ok {{
        background: linear-gradient(135deg, rgba(255,158,15,0.12), rgba(211,84,0,0.08));
        border: 1px solid rgba(211,84,0,0.25);
        border-left: 4px solid #FF9E0F;
        border-radius: 10px;
        padding: 12px 16px;
        color: #7b3e1b !important;
        font-weight: 500;
        font-size: 0.9rem;
        margin: 8px 0;
    }}

    /* OCULTAR alertas verdes nativas y reemplazar visualmente */
    div[data-testid="stSuccess"] {{
        background: linear-gradient(135deg, rgba(255,158,15,0.10), rgba(211,84,0,0.06)) !important;
        border: 1px solid rgba(211,84,0,0.22) !important;
        border-left: 4px solid #FF9E0F !important;
        border-radius: 10px !important;
        color: #7b3e1b !important;
    }}
    div[data-testid="stSuccess"] svg {{ color: #FF9E0F !important; fill: #FF9E0F !important; }}
    div[data-testid="stSuccess"] p {{ color: #7b3e1b !important; font-weight: 500 !important; }}

    div[data-testid="stInfo"] {{
        background: rgba(255,158,15,0.07) !important;
        border: 1px solid rgba(211,84,0,0.18) !important;
        border-radius: 10px !important;
        color: #7b3e1b !important;
    }}
    div[data-testid="stInfo"] p {{ color: #7b3e1b !important; }}

    /* CONTRASTE GENERAL DE TEXTO */
    p, li, .stMarkdown p {{ color: #4a3828 !important; }}
    label, .stMetric label {{ color: #6b4c30 !important; font-weight: 500 !important; }}
    [data-testid="stMetricValue"] {{ color: #3d1f08 !important; font-weight: 800 !important; }}
    [data-testid="stMetricLabel"] {{ color: #8a6040 !important; font-weight: 600 !important; }}

    /* CARDS DE MÉTRICAS — MISMO TAMAÑO */
    [data-testid="stMetric"] {{
        background: rgba(255, 245, 230, 0.9) !important;
        border: 1px solid rgba(219, 160, 106, 0.25) !important;
        border-radius: 16px !important;
        padding: 20px 18px !important;
        box-shadow: 0 2px 10px rgba(180,100,30,0.08) !important;
        min-height: 110px !important;
        height: 110px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        transition: transform 0.2s ease !important;
        overflow: hidden !important;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(180,100,30,0.12) !important;
    }}
    [data-testid="stMetricValue"] {{
        color: #3d1f08 !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
        line-height: 1.2 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: #8a6040 !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}
    /* Ocultar delta para no romper altura */
    [data-testid="stMetricDelta"] {{
        font-size: 0.75rem !important;
        margin-top: 2px !important;
    }}

    /* GRÁFICOS — borde y sombra */
    [data-testid="stPlotlyChart"] {{
        background: #ffffff !important;
        border: 1px solid rgba(219,160,106,0.22) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-shadow: 0 2px 12px rgba(180,100,30,0.07) !important;
        transition: box-shadow 0.25s ease !important;
    }}
    [data-testid="stPlotlyChart"]:hover {{
        box-shadow: 0 8px 28px rgba(180,100,30,0.13) !important;
    }}

    /* OCULTAR botón de colapsar sidebar */
    button[data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] button[kind="header"] {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }}

    /* NAV SIDEBAR — ocultar label "Sección:" */
    section[data-testid="stSidebar"] .stRadio > label {{
        display: none !important;
    }}
    /* Cada opción del radio como botón nav */
    section[data-testid="stSidebar"] .stRadio > div {{
        gap: 4px !important;
        flex-direction: column !important;
    }}
    section[data-testid="stSidebar"] .stRadio > div > label {{
        display: flex !important;
        align-items: center !important;
        padding: 11px 16px !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all 0.22s ease !important;
        background: transparent !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #7b3e1b !important;
        margin: 0 !important;
        border: 1px solid transparent !important;
    }}
    section[data-testid="stSidebar"] .stRadio > div > label:hover {{
        background: rgba(255, 158, 15, 0.14) !important;
        border-color: rgba(211, 84, 0, 0.18) !important;
        transform: translateX(4px);
    }}
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {{
        background: linear-gradient(135deg, #FF9E0F, #D35400) !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(211, 84, 0, 0.30) !important;
        border-color: transparent !important;
        transform: translateX(0);
    }}
    /* Ocultar el círculo del radio */
    section[data-testid="stSidebar"] .stRadio > div > label > div:first-child {{
        display: none !important;
    }}

    /* NAV LABEL */
    .nav-label {{
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #b08060 !important;
        padding: 12px 4px 6px;
    }}

    /* FILTROS SIDEBAR — date input */
    section[data-testid="stSidebar"] .stDateInput input {{
        background: rgba(255,255,255,0.85) !important;
        border: 1px solid rgba(219,160,106,0.4) !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        color: #5e3b1a !important;
    }}

    /* FILTROS SIDEBAR — multiselect contenedor */
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {{
        background: rgba(255,255,255,0.85) !important;
        border: 1px solid rgba(219,160,106,0.4) !important;
        border-radius: 10px !important;
    }}

    /* Tags seleccionados */
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
        background: linear-gradient(135deg, #FF9E0F, #D35400) !important;
        border: none !important;
        border-radius: 6px !important;
    }}
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {{
        color: white !important;
        font-size: 0.74rem !important;
        font-weight: 600 !important;
    }}
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] button {{
        color: rgba(255,255,255,0.85) !important;
    }}

    /* Dropdown lista opciones */
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="popover"] ul,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="menu"] {{
        background: #fff8f0 !important;
        border: 1px solid rgba(219,160,106,0.3) !important;
        border-radius: 10px !important;
    }}
    section[data-testid="stSidebar"] .stMultiSelect [role="option"] {{
        background: transparent !important;
        color: #5e3b1a !important;
        font-size: 0.82rem !important;
    }}
    section[data-testid="stSidebar"] .stMultiSelect [role="option"]:hover {{
        background: rgba(255,158,15,0.12) !important;
    }}

    /* Labels de los filtros */
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label {{
        color: #8a6040 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }}

    /* BOTONES GENERALES */
    .stButton > button {{
        background: linear-gradient(135deg, #FF9E0F, #D35400) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(211, 84, 0, 0.28) !important;
        transition: all 0.22s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 28px rgba(211, 84, 0, 0.38) !important;
    }}
</style>
"""

st.markdown(background_css, unsafe_allow_html=True)

if logo_base64:
    st.markdown(
        f"""
        <div class='logo-top-right'>
            <img src='data:image/png;base64,{logo_base64}' alt='Logo Holi' />
        </div>
        """,
        unsafe_allow_html=True,
    )

# ================================================================
# CARGA DE DATOS DESDE NEON (antes del sidebar para que df esté disponible)
# ================================================================
RUTA_SUCIO = "data/VENTAS_HOLI_2025_SIN_ETL.xlsx"

with st.spinner("Conectando a Neon PostgreSQL..."):
    try:
        df = cargar_datos()
    except Exception as e:
        st.error(f"Error al conectar con Neon: {e}")
        st.stop()

try:
    df_sucio = pd.read_excel(RUTA_SUCIO, engine="openpyxl")
except Exception:
    df_sucio = None

# ================================================================
# TÍTULO PRINCIPAL
# ================================================================
st.markdown(
    """
    <div class='hero-card'>
      <div class='hero-title'>Holi <span>Intelligence</span> Platform</div>
      <div class='hero-subtitle'>Sales analytics & demand forecasting — Supermercados Holi · Lima 2025</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")


# ================================================================
# SIDEBAR - PANEL DE CONTROL
# ================================================================
st.sidebar.markdown("""
<div style='padding: 8px 4px 0px 4px'>
  <div class='sidebar-brand'>
    <div class='sidebar-title'>Holi Analytics</div>
    <div class='sidebar-subtitle'>Supermercados Holi · Lima 2025</div>
  </div>
  <div class='sidebar-info'>
    <div class='sidebar-info-row'>
      <span class='sidebar-label'>Período</span>
      <span class='sidebar-value'>Año 2025</span>
    </div>
    <div class='sidebar-info-row'>
      <span class='sidebar-label'>Base de datos</span>
      <span class='sidebar-value'>Neon PostgreSQL</span>
    </div>
    <div class='sidebar-info-row'>
      <span class='sidebar-label'>Registros</span>
      <span class='sidebar-value'>4,479</span>
    </div>
    <div class='sidebar-info-row'>
      <span class='sidebar-label'>Sedes</span>
      <span class='sidebar-value'>5 sucursales</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div class='nav-label'>Navegación</div>", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Sección:",
    [
        "📊  Vista General",
        "🏆  Rankings",
        "📋  Análisis ABC",
        "🔄  Rotación",
        "🔮  Predicción",
        "📄  Reportes",
    ],
    label_visibility="collapsed",
)

# ================================================================
# FILTROS GLOBALES
# ================================================================
st.sidebar.markdown("<div class='nav-label'>Filtros</div>", unsafe_allow_html=True)

fecha_min = df["FECHA"].min().date()
fecha_max = df["FECHA"].max().date()
rango_fecha = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
    label_visibility="collapsed",
)

sucursales_disponibles = sorted(df["SUCURSAL"].unique().tolist())
sucursales_sel = st.sidebar.multiselect(
    "Sucursales",
    sucursales_disponibles,
    default=sucursales_disponibles,
    placeholder="Todas las sucursales",
)

categorias_disponibles = sorted(df["CATEGORIA"].unique().tolist())
categorias_sel = st.sidebar.multiselect(
    "Categorías",
    categorias_disponibles,
    default=categorias_disponibles,
    placeholder="Todas las categorías",
)

# Aplicar filtros
if len(rango_fecha) == 2:
    fecha_ini, fecha_fin = rango_fecha
    df = df[
        (df["FECHA"].dt.date >= fecha_ini) &
        (df["FECHA"].dt.date <= fecha_fin)
    ]
if sucursales_sel:
    df = df[df["SUCURSAL"].isin(sucursales_sel)]
if categorias_sel:
    df = df[df["CATEGORIA"].isin(categorias_sel)]

# KPIs con datos filtrados
kpis = calcular_kpis(df)




# ================================================================
# PROCESO ETL — DEMOSTRACIÓN CON DATOS ORIGINALES
# ================================================================
st.subheader("Proceso ETL (Limpieza y Transformación)")

if df_sucio is not None:
    diagnostico = diagnosticar_dataset(df_sucio)

    with st.expander("Ver diagnóstico del dataset original (datos sucios)", expanded=True):
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.metric("Registros totales", f"{diagnostico['total_registros']:,}")
        with col_d2:
            st.metric("Duplicados", diagnostico["duplicados"])
        with col_d3:
            st.metric("Valores nulos", diagnostico["total_nulos"])
        with col_d4:
            st.metric("Categorías detectadas", diagnostico.get("categorias_unicas_sucias", 0))

        st.markdown("**Distribución de valores nulos por columna:**")
        nulos_df = pd.DataFrame(
            list(diagnostico["nulos_por_columna"].items()),
            columns=["Columna", "Nulos"],
        )
        nulos_df = nulos_df[nulos_df["Nulos"] > 0]
        if len(nulos_df) > 0:
            st.dataframe(nulos_df, use_container_width=True, hide_index=True)
        else:
            st.markdown("<div class='alerta-ok'>Sin valores nulos detectados</div>", unsafe_allow_html=True)

    with st.spinner("Aplicando proceso ETL..."):
        _, log = aplicar_etl(df_sucio)

    st.markdown("### Resumen del Proceso ETL")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        st.metric("Registros iniciales", f"{log['registros_iniciales']:,}")
    with col_e2:
        st.metric("Registros finales", f"{log['registros_finales']:,}",
                  delta=f"-{log['registros_eliminados']}", delta_color="inverse")
    with col_e3:
        st.metric("Duplicados eliminados", log["duplicados_eliminados"])
    with col_e4:
        porcentaje = round(log["registros_finales"] / log["registros_iniciales"] * 100, 1)
        st.metric("Calidad final", f"{porcentaje}%")

    with st.expander("Ver detalles del proceso ETL aplicado"):
        detalles = pd.DataFrame([
            {"Acción": "Duplicados eliminados",           "Cantidad": log["duplicados_eliminados"]},
            {"Acción": "Fechas inválidas eliminadas",     "Cantidad": log["fechas_invalidas_eliminadas"]},
            {"Acción": "Categorías normalizadas",         "Cantidad": log["categorias_normalizadas"]},
            {"Acción": "Sucursales normalizadas",         "Cantidad": log["sucursales_normalizadas"]},
            {"Acción": "Métodos de pago normalizados",    "Cantidad": log["metodos_pago_normalizados"]},
            {"Acción": "Precios imputados (mediana)",     "Cantidad": log["nulos_precio_imputados"]},
            {"Acción": "Stock imputado",                  "Cantidad": log["nulos_stock_imputados"]},
            {"Acción": "Método de pago imputado",         "Cantidad": log["nulos_metodo_pago_imputados"]},
            {"Acción": "Cantidades inválidas eliminadas", "Cantidad": log["cantidades_invalidas_eliminadas"]},
            {"Acción": "Stock negativo corregido",        "Cantidad": log["stock_negativo_corregido"]},
        ])
        st.dataframe(detalles, use_container_width=True, hide_index=True)

    st.markdown("<div class='alerta-ok'>ETL completado — Los datos limpios están almacenados en Neon PostgreSQL</div>",
                unsafe_allow_html=True)
else:
    st.info("Archivo de datos originales no encontrado. El análisis usa los datos limpios de Neon.")



# ================================================================
# DASHBOARD PRINCIPAL
# ================================================================
st.markdown("---")
st.subheader("Dashboard Analítico")

# Mostrar KPIs principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Ventas Totales</div>
        <div class='kpi-valor'>S/ {kpis['ventas_totales']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Productos Únicos</div>
        <div class='kpi-valor'>{kpis['productos_unicos']}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Transacciones</div>
        <div class='kpi-valor'>{kpis['transacciones']:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Ticket Promedio</div>
        <div class='kpi-valor'>S/ {kpis['ticket_promedio']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ================================================================
# SECCIÓN: VISTA GENERAL
# ================================================================
if menu == "📊  Vista General":
    st.markdown("### Evolución y Distribución de Ventas")

    tab1, tab2, tab3 = st.tabs(["Evolución Temporal", "Por Sucursal", "Métodos de Pago"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            ventas_mensuales = analisis_temporal(df, "mensual")
            fig = px.line(
                ventas_mensuales,
                x="Periodo", y="Ventas",
                title="Evolución Mensual de Ventas",
                markers=True,
            )
            fig.update_traces(line_color="#667eea", line_width=3)
            st.plotly_chart(aplicar_tema(fig), use_container_width=True)

        with col2:
            ventas_diarias = analisis_temporal(df, "diaria")
            fig = px.area(
                ventas_diarias,
                x="Periodo", y="Ventas",
                title="Tendencia Diaria",
            )
            fig.update_traces(line_color="#764ba2")
            st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            ventas_suc = ventas_por_sucursal(df)
            fig = px.bar(
                ventas_suc,
                x="SUCURSAL", y="Ventas_Totales",
                title="Ventas por Sucursal",
                color="Ventas_Totales",
                color_continuous_scale=["#FFCC99", "#FF9E0F", "#5E2638"],
            )
            st.plotly_chart(aplicar_tema(fig), use_container_width=True)

        with col2:
            fig = px.pie(
                ventas_suc,
                names="SUCURSAL", values="Ventas_Totales",
                title="Distribución porcentual",
                hole=0.4,
            )
            st.plotly_chart(aplicar_tema(fig), use_container_width=True)

        st.dataframe(ventas_suc, use_container_width=True, hide_index=True)

    with tab3:
        col1, col2 = st.columns(2)
        metodo_pago = ventas_por_metodo_pago(df)

        with col1:
            fig = px.bar(
                metodo_pago,
                x="METODO_PAGO", y="Ventas_Totales",
                title="Ventas por Método de Pago",
                color="METODO_PAGO",
                color_discrete_sequence=["#FF9E0F", "#FFCC99", "#5E2638"],
            )
            st.plotly_chart(aplicar_tema(fig), use_container_width=True)

        with col2:
            fig = px.pie(
                metodo_pago,
                names="METODO_PAGO", values="Transacciones",
                title="Transacciones por Método",
                hole=0.4,
            )
            st.plotly_chart(aplicar_tema(fig), use_container_width=True)


# ================================================================
# SECCIÓN: RANKINGS
# ================================================================
elif menu == "🏆  Rankings":
    st.markdown("### Rankings de Productos y Categorías")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 10 Productos")
        top = top_productos(df, n=10)
        fig = px.bar(
            top,
            x="TOTAL_VENTA", y="PRODUCTO",
            orientation="h",
            color="TOTAL_VENTA",
            color_continuous_scale=["#FFCC99", "#FF9E0F", "#5E2638"],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    with col2:
        st.markdown("#### Ventas por Categoría")
        cat = ventas_por_categoria(df)
        fig = px.bar(
            cat,
            x="CATEGORIA", y="Ventas_Totales",
            color="CATEGORIA",
        )
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    st.markdown("#### Tabla Completa - Top Productos")
    st.dataframe(top, use_container_width=True, hide_index=True)


# ================================================================
# SECCIÓN: ANÁLISIS ABC
# ================================================================
elif menu == "📋  Análisis ABC":
    st.markdown("### Clasificación ABC de Productos")
    st.markdown("""
    El análisis ABC clasifica los productos según el **principio de Pareto (80/20)**:
    - **Categoría A**: productos que generan el 80% de las ventas
    - **Categoría B**: productos que aportan el 15%
    - **Categoría C**: productos de baja rotación (5%)
    """)

    abc = analisis_abc(df)
    resumen = resumen_abc(abc)

    col1, col2, col3 = st.columns(3)
    with col1:
        cat_a = resumen[resumen["Clasificación"] == "A"]
        if not cat_a.empty:
            st.metric("Categoría A", f"{int(cat_a['Productos'].iloc[0])} productos",
                     f"{cat_a['Porcentaje'].iloc[0]:.1f}% ventas")
    with col2:
        cat_b = resumen[resumen["Clasificación"] == "B"]
        if not cat_b.empty:
            st.metric("Categoría B", f"{int(cat_b['Productos'].iloc[0])} productos",
                     f"{cat_b['Porcentaje'].iloc[0]:.1f}% ventas")
    with col3:
        cat_c = resumen[resumen["Clasificación"] == "C"]
        if not cat_c.empty:
            st.metric("Categoría C", f"{int(cat_c['Productos'].iloc[0])} productos",
                     f"{cat_c['Porcentaje'].iloc[0]:.1f}% ventas")

    fig = px.bar(
        abc,
        x="PRODUCTO", y="TOTAL_VENTA",
        color="Clasificación",
        title="Clasificación ABC — Todos los productos",
        color_discrete_map={"A": "#5E2638", "B": "#FF9E0F", "C": "#FFCC99"},
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    st.markdown("#### Tabla Completa")
    st.dataframe(abc, use_container_width=True, hide_index=True)


# ================================================================
# SECCIÓN: ROTACIÓN
# ================================================================
elif menu == "🔄  Rotación":
    st.markdown("### Análisis de Rotación de Productos")
    st.markdown("La rotación diaria indica cuántas unidades se venden por día de cada producto.")

    rotacion = analisis_rotacion(df)

    fig = px.scatter(
        rotacion.head(30),
        x="Rotación_Diaria", y="Ventas_Totales",
        size="Unidades_Vendidas",
        hover_data=["PRODUCTO"],
        title="Rotación vs Ventas (Top 30)",
        color="Ventas_Totales",
        color_continuous_scale=["#FFCC99", "#FF9E0F", "#5E2638"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Tabla de Rotación")
    st.dataframe(rotacion, use_container_width=True, hide_index=True)


# ================================================================
# SECCIÓN: PREDICCIÓN
# ================================================================
elif menu == "🔮  Predicción":
    st.markdown("### Predicción de Demanda con Machine Learning (Prophet)")

    if not PROPHET_DISPONIBLE:
        st.warning("La librería **Prophet** no está instalada todavía. Para instalarla ejecuta en la terminal:")
        st.code("pip install prophet", language="bash")
        if st.button("Verificar de nuevo / Recargar app"):
            st.rerun()
    else:
        productos_lista = ["Todos los productos"] + sorted(df["PRODUCTO"].unique().tolist())

        with st.form("prediccion_form"):
            col1, col2 = st.columns([2, 1])

            with col1:
                producto_sel = st.selectbox("Producto", productos_lista)
                dias = st.slider("Días a predecir", 7, 90, 30)
                agrupacion = st.selectbox("Agrupación", ["diaria", "semanal", "mensual"])

            with col2:
                st.info("Prophet predice la demanda futura basándose en patrones históricos.")
                ejecutar = st.form_submit_button("Generar Predicción")

        if ejecutar:
            with st.spinner("Entrenando modelo Prophet..."):
                serie, forecast, error = predecir_demanda(df, producto_sel, dias, agrupacion)

            if error:
                st.error(error)
            else:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=serie["ds"], y=serie["y"],
                    mode="lines+markers",
                    name="Ventas Reales",
                    line=dict(color="#FF9E0F", width=2),
                ))
                fig.add_trace(go.Scatter(
                    x=forecast["ds"], y=forecast["yhat"],
                    mode="lines",
                    name="Predicción",
                    line=dict(color="#D35400", width=3, dash="dash"),
                ))
                fig.add_trace(go.Scatter(
                    x=forecast["ds"], y=forecast["yhat_upper"],
                    mode="lines", line=dict(width=0),
                    showlegend=False,
                ))
                fig.add_trace(go.Scatter(
                    x=forecast["ds"], y=forecast["yhat_lower"],
                    mode="lines", line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(211, 84, 0, 0.15)",
                    name="Intervalo de confianza",
                ))
                fig.update_layout(
                    title=f"Predicción de demanda: {producto_sel}",
                    xaxis_title="Fecha",
                    yaxis_title="Cantidad",
                    height=520,
                    hovermode="x unified",
                )
                st.plotly_chart(aplicar_tema(fig), use_container_width=True)

                resumen = resumen_prediccion(serie, forecast, dias)
                if resumen:
                    st.markdown("### Resumen de la Predicción")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Demanda total predicha", f"{resumen['demanda_total_predicha']:,} und")
                    c2.metric("Promedio diario", f"{resumen['demanda_promedio_diaria']}")
                    c3.metric("Máximo esperado", f"{resumen['demanda_maxima']}")
                    c4.metric("Variación vs histórico", f"{resumen['variacion_vs_historico']}%")

                futuro = obtener_prediccion_futura(serie, forecast)
                if futuro is not None:
                    st.markdown("### Predicción detallada")
                    st.dataframe(futuro, use_container_width=True, hide_index=True)
        else:
            st.info("Selecciona opciones y presiona 'Generar Predicción' para ver los resultados.")


# ================================================================
# SECCIÓN: REPORTES
# ================================================================
elif menu == "📄  Reportes":
    st.markdown("### Generación de Reporte Ejecutivo")
    st.markdown("Descarga un PDF profesional con todo el análisis del negocio.")

    abc_data = analisis_abc(df)
    resumen_abc_data = resumen_abc(abc_data)
    top_data = top_productos(df, n=10)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Contenido del reporte:")
        st.markdown("""
        - Indicadores clave del negocio (KPIs)
        - Top 10 productos más vendidos
        - Clasificación ABC detallada
        - Resumen del proceso ETL aplicado
        - Fecha de generación
        """)

    with col2:
        st.markdown("#### Acciones")
        if st.button("Generar PDF Ejecutivo", use_container_width=True):
            with st.spinner("Generando reporte PDF..."):
                df_suc_pdf = ventas_por_sucursal(df)
                buffer = generar_pdf_ejecutivo(kpis, top_data, resumen_abc_data,
                                               log_etl=None, df_sucursales=df_suc_pdf)

            st.success("Reporte generado correctamente")
            st.download_button(
                label="⬇️ Descargar Reporte PDF",
                data=buffer,
                file_name=f"Reporte_Holi_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ================================================================
# PIE DE PÁGINA
# ================================================================
st.markdown("""
<div style='text-align: center; color: #9a7050; padding: 24px 0 8px 0; font-size: 0.85rem; font-weight: 500;'>
    Sistema de Predicción de Demanda · Supermercados Holi · 2025
</div>
""", unsafe_allow_html=True)
