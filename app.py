import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Encuesta Limtek",
    layout="wide"
)

st.title("Dashboard Encuesta – Personal Operativo")
st.write("Validación inicial de archivos")

# Rutas de archivos
ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_CIERRE 2026.xlsx"
INVENTARIO_PATH = "data/11. INVENTARIO NOVIEMBRE 2025 - ACTUALIZADO (1).xlsx"

# Cargar Encuesta
try:
    df_encuesta = pd.read_excel(ENCUESTA_PATH)
    st.success("✅ Encuesta cargada correctamente")
    st.write("Columnas Encuesta:")
    st.write(df_encuesta.columns.tolist())
except Exception as e:
    st.error(f"❌ Error cargando encuesta: {e}")

st.divider()

# Cargar Inventario
try:
    df_inventario = pd.read_excel(INVENTARIO_PATH)
    st.success("✅ Inventario cargado correctamente")
    st.write("Columnas Inventario:")
    st.write(df_inventario.columns.tolist())
except Exception as e:
    st.error(f"❌ Error cargando inventario: {e}")
