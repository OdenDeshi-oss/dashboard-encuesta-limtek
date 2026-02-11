import streamlit as st
import base64
from pathlib import Path

st.set_page_config(page_title="Dashboard Encuesta Limtek – Operativo", layout="wide")

def load_css(path: str):
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/styles.css")

from layout.header import render_header
from core.loader import cargar_encuesta, cargar_inventario_operativos
from core.config import (
    ESCALA_ACUERDO, CATEGORIAS_POSITIVAS, CATEGORIAS_MEJORA,
)
from sections.satisfaccion import render_satisfaccion
from sections.metodologia import render_metodologia
from components.filters import render_filtros
from components.multi_choice_card import render_pregunta_multiple
from components.yes_no_card import render_pregunta_si_no
from components.open_text_card_v2 import render_pregunta_abierta_v2
from components.category_card import render_pregunta_categorica
from components.likert_card_v2 import render_pregunta_v2

# ── SIDEBAR ──
def render_sidebar_logo(logo_path: str):
    img_bytes = Path(logo_path).read_bytes()
    logo_base64 = base64.b64encode(img_bytes).decode()
    st.sidebar.markdown(
        f"""<div style="display:flex;justify-content:center;margin:16px 0 24px 0;">
        <img src="data:image/png;base64,{logo_base64}" style="width:450px;max-width:100%;opacity:0.95;"></div>""",
        unsafe_allow_html=True,
    )

render_sidebar_logo("assets/logo_limtek.png")

# ── HEADER ──
render_header(
    titulo="Dashboard Encuesta – Personal Operativo",
    subtitulo="#ExpertosapoyandoExpertos",
)

# ── DATA ──
df_base = cargar_encuesta()
df_cliente_unidad, df_general = render_filtros(df_base)

# ── KPIs ──
total_encuestados = df_general["RESPONDENT_ID"].nunique()
total_operativos = cargar_inventario_operativos()
participacion_pct = (total_encuestados / total_operativos) * 100 if total_operativos > 0 else 0

if participacion_pct < 60:
    participacion_class = "kpi-danger"
elif participacion_pct < 80:
    participacion_class = "kpi-warning"
else:
    participacion_class = "kpi-ok"

col_departamento = "¿EN QUÉ DEPARTAMENTO TRABAJAS?"
df_dep = df_cliente_unidad[col_departamento].astype(str).str.upper().str.strip()
lima_count = (df_dep == "LIMA").sum()
total_geo = df_dep.shape[0]
prov_count = total_geo - lima_count
lima_pct = (lima_count / total_geo) * 100 if total_geo else 0
prov_pct = (prov_count / total_geo) * 100 if total_geo else 0

colA, colB = st.columns(2, gap="large")

with colA:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-card-title">Cobertura de la encuesta</div>
        <div class="kpi-row">
        <div class="kpi-item"><div class="kpi-value">{total_encuestados}</div><div class="kpi-label">Encuestados</div></div>
        <div class="kpi-item"><div class="kpi-value {participacion_class}">{participacion_pct:.1f}%</div><div class="kpi-label">Participación</div>
        <div class="kpi-sub">{total_encuestados} / {total_operativos}</div></div>
        </div></div>""",
        unsafe_allow_html=True,
    )

with colB:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-card-title">Distribución geográfica</div>
        <div class="kpi-row">
        <div class="kpi-item"><div class="kpi-value">{lima_pct:.1f}%</div><div class="kpi-label">Lima</div><div class="kpi-sub">{lima_count} personas</div></div>
        <div class="kpi-item"><div class="kpi-value">{prov_pct:.1f}%</div><div class="kpi-label">Provincias</div><div class="kpi-sub">{prov_count} personas</div></div>
        </div></div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom:32px;'></div>", unsafe_allow_html=True)

# ── METODOLOGÍA ──
render_metodologia()

# ── SATISFACCIÓN LIKERT ──
render_satisfaccion(df_general)

# ── SATISFACCIÓN GENERAL ──
render_pregunta_v2(
    df_general,
    titulo="Considero a Limtek como un buen lugar para trabajar",
    col_valor="VALOR_SATISFACCIÓN",
    escala=ESCALA_ACUERDO,
)

# ── CAPACITACIÓN ──
COLS_CAPACITACION = [
    "SEGURIDAD Y SALUD EN EL TRABAJO",
    "USO DE MAQUINARIAS Y EQUIPOS",
    "USO DE INSUMOS",
    "ATENCIÓN AL CLIENTE",
    "OTRO (ESPECIFIQUE)",
]
render_pregunta_multiple(
    df_general,
    titulo="¿En qué temas te gustaría recibir capacitación?",
    columnas=COLS_CAPACITACION,
)

# ── WHATSAPP ──
render_pregunta_si_no(
    df_general,
    titulo="¿Usas WhatsApp en tu vida diaria?",
    col_valor="¿USAS WHATSAPP EN TU VIDA DIARIA?",
)

# ── QUÉ DESTACAS ──
render_pregunta_abierta_v2(
    df_general,
    titulo="¿Qué destacas de Limtek al considerarlo un buen lugar para trabajar?",
    col_valor="¿QUÉ DESTACAS DE LIMTEK AL CONSIDERARLO UN BUEN LUGAR PARA TRABAJAR?",
    categorias=CATEGORIAS_POSITIVAS,
)

# ── QUÉ MEJORAR ──
render_pregunta_abierta_v2(
    df_general,
    titulo="¿Qué tendría que mejorar Limtek para que lo consideres un buen lugar para trabajar?",
    col_valor="¿QUÉ TENDRÍA QUE MEJORAR LIMTEK PARA QUE LO CONSIDERES UN BUEN LUGAR PARA TRABAJAR?",
    categorias=CATEGORIAS_MEJORA,
)

# ── ANTIGÜEDAD ──
ORDEN_ANTIGUEDAD = [
    "De 0 a 6 meses",
    "De 6 meses a 1 año",
    "De 1 a 2 años",
    "De 2 a 3 años",
    "De 3 años a más",
]
render_pregunta_categorica(
    df_general,
    titulo="¿Cuánto tiempo llevas trabajando en Limtek?",
    col_valor="¿CUÁNTO TIEMPO LLEVAS TRABAJANDO EN LIMTEK?",
    orden=ORDEN_ANTIGUEDAD,
)

# ── FOOTER ──
st.markdown("---")
st.caption("📊 Dashboard Encuesta Limtek – Personal Operativo | Área de Gestión Humana")
