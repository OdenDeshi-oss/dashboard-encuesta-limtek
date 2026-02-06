import streamlit as st
from core.loader import cargar_encuesta
from sections.satisfaccion import render_satisfaccion

st.set_page_config(
    page_title="Dashboard Encuesta Limtek",
    layout="wide"
)

st.title("Dashboard Encuesta – Personal Operativo")
st.caption("Resultados de satisfacción – Escala 1 a 4")

df = cargar_encuesta()

render_satisfaccion(df)

st.caption("📊 Dashboard Encuesta Limtek – Personal Operativo")
