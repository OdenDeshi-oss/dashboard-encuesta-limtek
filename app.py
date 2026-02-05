import pandas as pd
import streamlit as st
import plotly.express as px


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
# FILTROS SIDEBAR
# ======================
st.sidebar.header("Filtros")

# Obtener valores únicos
clientes = sorted(df_inv_resumen["CLIENTE"].dropna().unique())
cliente_sel = st.sidebar.selectbox(
    "Cliente",
    options=["Todos"] + clientes
)

# Filtrar por cliente
if cliente_sel != "Todos":
    df_inv_f = df_inv_resumen[df_inv_resumen["CLIENTE"] == cliente_sel]
else:
    df_inv_f = df_inv_resumen.copy()

# Unidades según cliente
unidades = sorted(df_inv_f["UNIDAD"].dropna().unique())
unidad_sel = st.sidebar.selectbox(
    "Unidad",
    options=["Todas"] + unidades
)

# Filtro final inventario
if unidad_sel != "Todas":
    df_inv_f = df_inv_f[df_inv_f["UNIDAD"] == unidad_sel]


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
    df_inv_f,
    df_encuesta_resumen,
    left_on=["CLIENTE", "UNIDAD"],
    right_on=[COL_CLIENTE, COL_UNIDAD],
    how="left"
)


df_cruce["TOTAL_ENCUESTADOS"] = df_cruce["TOTAL_ENCUESTADOS"].fillna(0).astype(int)
df_cruce["BRECHA"] = df_cruce["TOTAL_OPERARIOS"] - df_cruce["TOTAL_ENCUESTADOS"]

st.subheader("Resultado filtrado (Cobertura Operativa)")
st.dataframe(df_cruce)

st.divider()
st.header("Indicadores clave de cobertura")

# ======================
# KPIs
# ======================
total_operarios = int(df_cruce["TOTAL_OPERARIOS"].sum())
total_encuestados = int(df_cruce["TOTAL_ENCUESTADOS"].sum())
brecha = int(df_cruce["BRECHA"].sum())

if total_operarios > 0:
    participacion = round((total_encuestados / total_operarios) * 100, 1)
else:
    participacion = 0.0

# ======================
# MOSTRAR KPIs
# ======================
col1, col2, col3, col4 = st.columns(4)

col1.metric("👷 Operarios", total_operarios)
col2.metric("📝 Encuestados", total_encuestados)
col3.metric("📉 Brecha", brecha)
col4.metric("📊 Participación", f"{participacion}%")

st.divider()
st.header("Cobertura por Unidad")

# ======================
# PREPARAR DATA PARA GRAFICO
# ======================
df_grafico = (
    df_cruce
    .groupby("UNIDAD", as_index=False)
    .agg({
        "TOTAL_ENCUESTADOS": "sum",
        "TOTAL_OPERARIOS": "sum"
    })
)

# Total dinámico según filtros
total_encuestados_filtro = df_grafico["TOTAL_ENCUESTADOS"].sum()

# Calcular porcentaje dinámico
df_grafico["PORCENTAJE"] = df_grafico["TOTAL_ENCUESTADOS"].apply(
    lambda x: round((x / total_encuestados_filtro) * 100, 1) if total_encuestados_filtro > 0 else 0
)

# Etiqueta combinada: Cantidad (Porcentaje)
df_grafico["LABEL"] = df_grafico.apply(
    lambda r: f"{int(r['TOTAL_ENCUESTADOS'])} ({r['PORCENTAJE']}%)",
    axis=1
)

# ======================
# GRAFICO
# ======================
fig = px.bar(
    df_grafico,
    x="UNIDAD",
    y="TOTAL_ENCUESTADOS",
    text_auto=True,
    title="Encuestados por Unidad (Cantidad y % del total)",
    labels={
        "TOTAL_ENCUESTADOS": "Cantidad de encuestados",
        "UNIDAD": "Unidad"
    }
)



st.plotly_chart(fig, use_container_width=True)

st.divider()
st.header("Cobertura por Cliente")

st.subheader("Detalle por Unidad (Cantidad y %)")
st.dataframe(
    df_grafico[["UNIDAD", "TOTAL_ENCUESTADOS", "PORCENTAJE"]],
    use_container_width=True
)


# ======================
# PREPARAR DATA PARA GRAFICO
# ======================
df_grafico_cliente = (
    df_cruce
    .groupby("CLIENTE", as_index=False)
    .agg({
        "TOTAL_ENCUESTADOS": "sum",
        "TOTAL_OPERARIOS": "sum"
    })
)

# Total dinámico según filtros
total_encuestados_filtro_cliente = df_grafico_cliente["TOTAL_ENCUESTADOS"].sum()

# Calcular porcentaje dinámico
df_grafico_cliente["PORCENTAJE"] = df_grafico_cliente["TOTAL_ENCUESTADOS"].apply(
    lambda x: round((x / total_encuestados_filtro_cliente) * 100, 1) if total_encuestados_filtro_cliente > 0 else 0
)

# Etiqueta combinada: Cantidad (Porcentaje)
df_grafico_cliente["LABEL"] = df_grafico_cliente.apply(
    lambda r: f"{int(r['TOTAL_ENCUESTADOS'])} ({r['PORCENTAJE']}%)",
    axis=1
)

# ======================
# GRAFICO
# ======================
fig_cliente = px.bar(
    df_grafico_cliente,
    x="CLIENTE",
    y="TOTAL_ENCUESTADOS",
    text="LABEL",
    title="Encuestados por Cliente (Cantidad y % del total)",
    labels={
        "TOTAL_ENCUESTADOS": "Cantidad de encuestados",
        "CLIENTE": "Cliente"
    }
)

fig_cliente.update_traces(textposition="outside")
fig_cliente.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")

st.plotly_chart(fig_cliente, use_container_width=True)



