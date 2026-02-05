import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Encuesta Limtek",
    layout="wide"
)

st.title("Dashboard Encuesta – Personal Operativo")
st.write("Preparación de datos (sin gráficos)")

# ======================
# RUTAS DE ARCHIVOS
# ======================
ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_CIERRE 2026.xlsx"
INVENTARIO_PATH = "data/11. INVENTARIO NOVIEMBRE 2025 - ACTUALIZADO (1).xlsx"

# ======================
# CARGA ENCUESTA
# ======================
df_encuesta = pd.read_excel(ENCUESTA_PATH)
st.success("✅ Encuesta cargada")
st.write("Columnas Encuesta:")
st.write(df_encuesta.columns.tolist())

st.divider()

# ======================
# CARGA INVENTARIO
# ======================
df_inv = pd.read_excel(INVENTARIO_PATH)
st.success("✅ Inventario cargado")

st.write("Columnas Inventario:")
st.write(df_inv.columns.tolist())

st.divider()

# ======================
# LIMPIEZA INVENTARIO
# ======================
# Ajusta estos nombres SI el Excel usa otros textos
CARGO_OPERATIVO = [
    "OPERARIO",
    "OPERARIO PART TIME"
]

# Filtrar solo personal operativo
df_inv_operativo = df_inv[df_inv["CARGO"].isin(CARGO_OPERATIVO)]

st.subheader("Inventario filtrado – Solo personal operativo")
st.write(f"Registros operativos: {len(df_inv_operativo)}")

# ======================
# AGRUPACIÓN
# ======================
df_inv_resumen = (
    df_inv_operativo
    .groupby(["CLIENTE", "UNIDAD"])
    .size()
    .reset_index(name="TOTAL_OPERARIOS")
)

st.subheader("Resumen Inventario (Operativos por Cliente y Unidad)")
st.dataframe(df_inv_resumen)

st.divider()
st.header("Cruce Encuesta vs Inventario")

# ======================
# PREPARAR ENCUESTA
# ======================
# Ajusta los nombres si el Excel usa otros textos
COL_CLIENTE = "¿En qué cliente estás destacado?"
COL_UNIDAD = "¿En qué unidad estás destacado?"

df_encuesta_resumen = (
    df_encuesta
    .groupby([COL_CLIENTE, COL_UNIDAD])
    .size()
    .reset_index(name="TOTAL_ENCUESTADOS")
)

st.subheader("Resumen Encuesta (Encuestados por Cliente y Unidad)")
st.dataframe(df_encuesta_resumen)

# ======================
# CRUCE CON INVENTARIO
# ======================
df_cruce = pd.merge(
    df_inv_resumen,
    df_encuesta_resumen,
    on=[COL_CLIENTE, COL_UNIDAD],
    how="left"
)

df_cruce["TOTAL_ENCUESTADOS"] = df_cruce["TOTAL_ENCUESTADOS"].fillna(0).astype(int)
df_cruce["BRECHA"] = df_cruce["TOTAL_OPERARIOS"] - df_cruce["TOTAL_ENCUESTADOS"]

st.subheader("Cruce Final (Inventario vs Encuesta)")
st.dataframe(df_cruce)
