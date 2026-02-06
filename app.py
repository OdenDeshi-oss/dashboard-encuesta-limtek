import streamlit as st

# Layout
from layout.header import render_header

# Core
from core.loader import cargar_encuesta

# Sections
from sections.satisfaccion import render_satisfaccion


# ======================
# CONFIGURACIÓN GENERAL
# ======================
st.set_page_config(
    page_title="Dashboard Encuesta Limtek",
    layout="wide"
)

# ======================
# HEADER CORPORATIVO
# ======================
render_header(
    logo_path="assets/logo_limtek.png",
    titulo="Dashboard Encuesta – Personal Operativo",
    subtitulo="#ExpertosapoyandoExpertos"
)

# ======================
# CARGA DE DATOS
# ======================
df = cargar_encuesta()

# ======================
# SECCIÓN: SATISFACCIÓN (LIKERT 1–4)
# ======================
render_satisfaccion(df)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.caption("📊 Dashboard Encuesta Limtek – Personal Operativo | Área de Bienestar Social")
