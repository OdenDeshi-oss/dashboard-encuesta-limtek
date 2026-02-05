import pandas as pd
import streamlit as st
import plotly.express as px
import os

# ======================
# CONFIGURACIÓN GENERAL
# ======================
st.set_page_config(
    page_title="Dashboard Encuesta Limtek",
    layout="wide"
)

st.title("Dashboard Encuesta – Personal Operativo")
st.write("Preparación y análisis de datos")

# ======================
# FUNCIÓN PARA NORMALIZAR NOMBRES DE COLUMNAS
# ======================
def normalizar_columnas(df):
    """Normaliza nombres de columnas: sin espacios extra, uppercase"""
    df.columns = df.columns.str.strip().str.upper()
    return df

def separador():
    """Separador visual compatible con versiones antiguas de Streamlit"""
    st.markdown("---")

# ======================
# RUTAS DE ARCHIVOS
# ======================
ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_ CIERRE 2026.xlsx"
INVENTARIO_PATH = "data/11. INVENTARIO NOVIEMBRE 2025 - ACTUALIZADO (1).xlsx"

# ======================
# CARGA ENCUESTA CON MANEJO DE ERRORES
# ======================
try:
    if not os.path.exists(ENCUESTA_PATH):
        st.error(f"❌ No se encontró el archivo: {ENCUESTA_PATH}")
        st.stop()
    
    df_encuesta = pd.read_excel(ENCUESTA_PATH)
    df_encuesta = normalizar_columnas(df_encuesta)
    st.success("✅ Encuesta cargada correctamente")
    
    with st.expander("📋 Ver columnas de Encuesta"):
        st.write(df_encuesta.columns.tolist())
        st.write(f"Total de registros: {len(df_encuesta)}")
    
except Exception as e:
    st.error(f"❌ Error al cargar la encuesta: {str(e)}")
    st.stop()

separador()

# ======================
# CARGA INVENTARIO CON MANEJO DE ERRORES
# ======================
try:
    if not os.path.exists(INVENTARIO_PATH):
        st.error(f"❌ No se encontró el archivo: {INVENTARIO_PATH}")
        st.stop()
    
    df_inv = pd.read_excel(INVENTARIO_PATH)
    df_inv = normalizar_columnas(df_inv)
    st.success("✅ Inventario cargado correctamente")
    
    with st.expander("📋 Ver columnas de Inventario"):
        st.write(df_inv.columns.tolist())
        st.write(f"Total de registros: {len(df_inv)}")
    
except Exception as e:
    st.error(f"❌ Error al cargar el inventario: {str(e)}")
    st.stop()

separador()

# ======================
# VERIFICAR COLUMNAS NECESARIAS
# ======================
columnas_requeridas_inv = ["CARGO", "CLIENTE", "UNIDAD"]
columnas_faltantes_inv = [col for col in columnas_requeridas_inv if col not in df_inv.columns]

if columnas_faltantes_inv:
    st.error(f"❌ Columnas faltantes en Inventario: {columnas_faltantes_inv}")
    st.info("💡 Columnas disponibles:")
    st.write(df_inv.columns.tolist())
    st.stop()

# ======================
# LIMPIEZA INVENTARIO
# ======================
CARGO_OPERATIVO = [
    "OPERARIO",
    "OPERARIO PART TIME"
]

# Filtrar con manejo de valores nulos
df_inv_operativo = df_inv[df_inv["CARGO"].fillna("").isin(CARGO_OPERATIVO)].copy()

st.subheader("📊 Inventario filtrado – Solo personal operativo")
st.info(f"✅ Registros operativos encontrados: **{len(df_inv_operativo)}** de {len(df_inv)} totales")

if len(df_inv_operativo) == 0:
    st.warning("⚠️ No se encontraron registros operativos. Verifica los valores en la columna CARGO.")
    st.write("Valores únicos en CARGO:")
    st.write(df_inv["CARGO"].value_counts())
    st.stop()

# ======================
# AGRUPACIÓN INVENTARIO
# ======================
df_inv_resumen = (
    df_inv_operativo
    .groupby(["CLIENTE", "UNIDAD"], dropna=False)
    .size()
    .reset_index(name="TOTAL_OPERARIOS")
)

st.subheader("📈 Resumen Inventario (Operativos por Cliente y Unidad)")
st.dataframe(df_inv_resumen, use_container_width=True)

separador()

# ======================
# PREPARAR ENCUESTA
# ======================
# Buscar las columnas correctas en la encuesta
posibles_cols_cliente = [col for col in df_encuesta.columns if "CLIENTE" in col.upper()]
posibles_cols_unidad = [col for col in df_encuesta.columns if "UNIDAD" in col.upper()]

if not posibles_cols_cliente:
    st.error("❌ No se encontró columna de CLIENTE en la encuesta")
    st.write("Columnas disponibles:", df_encuesta.columns.tolist())
    st.stop()

if not posibles_cols_unidad:
    st.error("❌ No se encontró columna de UNIDAD en la encuesta")
    st.write("Columnas disponibles:", df_encuesta.columns.tolist())
    st.stop()

COL_CLIENTE = posibles_cols_cliente[0]
COL_UNIDAD = posibles_cols_unidad[0]

st.info(f"📌 Usando columnas: Cliente='{COL_CLIENTE}', Unidad='{COL_UNIDAD}'")

df_encuesta_resumen = (
    df_encuesta
    .groupby([COL_CLIENTE, COL_UNIDAD], dropna=False)
    .size()
    .reset_index(name="TOTAL_ENCUESTADOS")
)

st.subheader("📝 Resumen Encuesta (Encuestados por Cliente y Unidad)")
st.dataframe(df_encuesta_resumen, use_container_width=True)

separador()
st.header("🔄 Cruce Encuesta vs Inventario")

# ======================
# FILTROS SIDEBAR
# ======================
st.sidebar.header("🎯 Filtros")

clientes = sorted(df_inv_resumen["CLIENTE"].dropna().unique())
cliente_sel = st.sidebar.selectbox(
    "Cliente",
    options=["Todos"] + list(clientes)
)

if cliente_sel != "Todos":
    df_inv_f = df_inv_resumen[df_inv_resumen["CLIENTE"] == cliente_sel].copy()
else:
    df_inv_f = df_inv_resumen.copy()

unidades = sorted(df_inv_f["UNIDAD"].dropna().unique())
unidad_sel = st.sidebar.selectbox(
    "Unidad",
    options=["Todas"] + list(unidades)
)

if unidad_sel != "Todas":
    df_inv_f = df_inv_f[df_inv_f["UNIDAD"] == unidad_sel].copy()

# ======================
# CRUCE
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
df_cruce["COBERTURA_%"] = (
    (df_cruce["TOTAL_ENCUESTADOS"] / df_cruce["TOTAL_OPERARIOS"] * 100)
    .round(1)
    .fillna(0)
)

st.subheader("📊 Resultado filtrado (Cobertura Operativa)")

# Mostrar tabla con formato condicional
def color_brecha(val):
    """Colorea las celdas según el valor de la brecha"""
    if val > 10:
        return 'background-color: #ffcccc'
    elif val > 5:
        return 'background-color: #fff3cd'
    return ''

# Aplicar estilo si la versión de pandas lo soporta
try:
    st.dataframe(
        df_cruce.style.applymap(color_brecha, subset=['BRECHA']),
        use_container_width=True
    )
except:
    st.dataframe(df_cruce, use_container_width=True)

separador()
st.header("📊 Indicadores clave de cobertura")

# ======================
# KPIs
# ======================
total_operarios = int(df_cruce["TOTAL_OPERARIOS"].sum())
total_encuestados = int(df_cruce["TOTAL_ENCUESTADOS"].sum())
brecha = int(df_cruce["BRECHA"].sum())

participacion = round(
    (total_encuestados / total_operarios) * 100, 1
) if total_operarios > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("👷 Operarios", f"{total_operarios:,}")
col2.metric("📝 Encuestados", f"{total_encuestados:,}")
col3.metric("📉 Brecha", f"{brecha:,}")
col4.metric("📊 Participación", f"{participacion}%")

separador()
st.header("📍 Cobertura por Unidad")

# ======================
# GRAFICO POR UNIDAD
# ======================
if len(df_cruce) > 0:
    df_grafico = (
        df_cruce
        .groupby("UNIDAD", as_index=False, dropna=False)
        .agg({
            "TOTAL_ENCUESTADOS": "sum",
            "TOTAL_OPERARIOS": "sum"
        })
    )
    
    df_grafico["BRECHA"] = df_grafico["TOTAL_OPERARIOS"] - df_grafico["TOTAL_ENCUESTADOS"]
    
    total_encuestados_filtro = df_grafico["TOTAL_ENCUESTADOS"].sum()
    
    df_grafico["PORCENTAJE"] = df_grafico["TOTAL_ENCUESTADOS"].apply(
        lambda x: round((x / total_encuestados_filtro) * 100, 1)
        if total_encuestados_filtro > 0 else 0
    )
    
    df_grafico["COBERTURA_%"] = (
        (df_grafico["TOTAL_ENCUESTADOS"] / df_grafico["TOTAL_OPERARIOS"] * 100)
        .round(1)
        .fillna(0)
    )
    
    df_grafico["LABEL"] = df_grafico.apply(
        lambda r: f"{int(r['TOTAL_ENCUESTADOS'])} ({r['PORCENTAJE']}%)",
        axis=1
    )
    
    fig = px.bar(
        df_grafico,
        x="UNIDAD",
        y="TOTAL_ENCUESTADOS",
        text="LABEL",
        title="Encuestados por Unidad (Cantidad y % del total)",
        labels={
            "TOTAL_ENCUESTADOS": "Cantidad de encuestados",
            "UNIDAD": "Unidad"
        },
        color="COBERTURA_%",
        color_continuous_scale="RdYlGn"
    )
    
    fig.update_traces(textposition="outside")
    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Detalle por Unidad")
    st.dataframe(
        df_grafico[["UNIDAD", "TOTAL_OPERARIOS", "TOTAL_ENCUESTADOS", "BRECHA", "COBERTURA_%"]].sort_values("COBERTURA_%", ascending=False),
        use_container_width=True
    )
else:
    st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados")

separador()
st.header("🏢 Cobertura por Cliente")

# ======================
# GRAFICO POR CLIENTE
# ======================
if len(df_cruce) > 0:
    df_grafico_cliente = (
        df_cruce
        .groupby("CLIENTE", as_index=False, dropna=False)
        .agg({
            "TOTAL_ENCUESTADOS": "sum",
            "TOTAL_OPERARIOS": "sum"
        })
    )
    
    df_grafico_cliente["BRECHA"] = df_grafico_cliente["TOTAL_OPERARIOS"] - df_grafico_cliente["TOTAL_ENCUESTADOS"]
    
    total_encuestados_cliente = df_grafico_cliente["TOTAL_ENCUESTADOS"].sum()
    
    df_grafico_cliente["PORCENTAJE"] = df_grafico_cliente["TOTAL_ENCUESTADOS"].apply(
        lambda x: round((x / total_encuestados_cliente) * 100, 1)
        if total_encuestados_cliente > 0 else 0
    )
    
    df_grafico_cliente["COBERTURA_%"] = (
        (df_grafico_cliente["TOTAL_ENCUESTADOS"] / df_grafico_cliente["TOTAL_OPERARIOS"] * 100)
        .round(1)
        .fillna(0)
    )
    
    df_grafico_cliente["LABEL"] = df_grafico_cliente.apply(
        lambda r: f"{int(r['TOTAL_ENCUESTADOS'])} ({r['PORCENTAJE']}%)",
        axis=1
    )
    
    fig_cliente = px.bar(
        df_grafico_cliente,
        x="CLIENTE",
        y="TOTAL_ENCUESTADOS",
        text="LABEL",
        title="Encuestados por Cliente (Cantidad y % del total)",
        labels={
            "TOTAL_ENCUESTADOS": "Cantidad de encuestados",
            "CLIENTE": "Cliente"
        },
        color="COBERTURA_%",
        color_continuous_scale="RdYlGn"
    )
    
    fig_cliente.update_traces(textposition="outside")
    fig_cliente.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig_cliente, use_container_width=True)
    
    st.subheader("📋 Detalle por Cliente")
    st.dataframe(
        df_grafico_cliente[["CLIENTE", "TOTAL_OPERARIOS", "TOTAL_ENCUESTADOS", "BRECHA", "COBERTURA_%"]].sort_values("COBERTURA_%", ascending=False),
        use_container_width=True
    )
else:
    st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados")

# ======================
# FOOTER
# ======================
separador()
st.caption("📊 Dashboard Encuesta Limtek - Personal Operativo | Desarrollado con Streamlit")
