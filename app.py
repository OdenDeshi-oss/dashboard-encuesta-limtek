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
# FUNCIÓN SEPARADOR (Reemplaza st.divider)
# ======================
def separador():
    """Separador visual - Compatible con todas las versiones de Streamlit"""
    st.markdown("---")

# ======================
# FUNCIÓN PARA NORMALIZAR NOMBRES DE COLUMNAS
# ======================
def normalizar_columnas(df):
    """Normaliza nombres de columnas: sin espacios extra, uppercase"""
    df.columns = df.columns.str.strip().str.upper()
    return df

# ======================
# RUTAS DE ARCHIVOS
# ======================
ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_ CIERRE 2026.xlsx"
INVENTARIO_PATH = "data/11. INVENTARIO NOVIEMBRE 2025 - ACTUALIZADO (1).xlsx"

# ======================
# DEFINICIÓN DE PREGUNTAS MÚLTIPLES
# ======================
# Estas son las columnas de checkbox/opciones múltiples en la encuesta
PREGUNTAS_MULTIPLES = [
    "SEGURIDAD Y SALUD EN EL TRABAJO",
    "USO DE MAQUINARIAS Y EQUIPOS",
    "USO DE INSUMOS",
    "ATENCIÓN AL CLIENTE",
    "OTRO (ESPECIFIQUE)"
]

# ======================
# CARGA ENCUESTA CON MANEJO DE ERRORES
# ======================
try:
    if not os.path.exists(ENCUESTA_PATH):
        st.error(f"❌ No se encontró el archivo: {ENCUESTA_PATH}")
        st.stop()
    
    # Cargar con engine específico y manejo de encoding
    df_encuesta = pd.read_excel(ENCUESTA_PATH, engine='openpyxl')
    
    # Convertir todas las columnas object a string para evitar errores de encoding
    for col in df_encuesta.select_dtypes(include=['object']).columns:
        df_encuesta[col] = df_encuesta[col].astype(str)
    
    df_encuesta = normalizar_columnas(df_encuesta)
    st.success("✅ Encuesta cargada correctamente")
    
    with st.expander("📋 Ver columnas de Encuesta"):
        st.write(df_encuesta.columns.tolist())
        st.write(f"Total de registros: {len(df_encuesta)}")
    
except Exception as e:
    st.error(f"❌ Error al cargar la encuesta: {str(e)}")
    st.stop()

# Separador compatible
separador()

# ======================
# CARGA INVENTARIO CON MANEJO DE ERRORES
# ======================
try:
    if not os.path.exists(INVENTARIO_PATH):
        st.error(f"❌ No se encontró el archivo: {INVENTARIO_PATH}")
        st.stop()
    
    # Cargar con engine específico y manejo de encoding
    df_inv = pd.read_excel(INVENTARIO_PATH, engine='openpyxl')
    
    # Convertir todas las columnas object a string para evitar errores de encoding
    for col in df_inv.select_dtypes(include=['object']).columns:
        df_inv[col] = df_inv[col].astype(str)
    
    df_inv = normalizar_columnas(df_inv)
    st.success("✅ Inventario cargado correctamente")
    
    with st.expander("📋 Ver columnas de Inventario"):
        st.write(df_inv.columns.tolist())
        st.write(f"Total de registros: {len(df_inv)}")
    
except Exception as e:
    st.error(f"❌ Error al cargar el inventario: {str(e)}")
    st.stop()

# Separador compatible
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

# Filtrar con manejo de valores nulos y nan
df_inv_operativo = df_inv[
    df_inv["CARGO"].fillna("").replace("NAN", "").str.strip().isin(CARGO_OPERATIVO)
].copy()

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

# Separador compatible
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

# Separador compatible
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

# Mostrar DataFrame simple sin estilos (evita errores de encoding)
st.dataframe(df_cruce, use_container_width=True)

# Separador compatible
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

# Separador compatible
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
    
    # Convertir a string para evitar errores de encoding
    df_grafico["UNIDAD"] = df_grafico["UNIDAD"].astype(str)
    
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

# Separador compatible
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
    
    # Convertir a string para evitar errores de encoding
    df_grafico_cliente["CLIENTE"] = df_grafico_cliente["CLIENTE"].astype(str)
    
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

# ============================================================================
# NUEVA SECCIÓN: ANÁLISIS DE PREGUNTAS MÚLTIPLES
# ============================================================================
separador()
st.header("📋 Análisis de Necesidades de Capacitación")
st.write("Áreas en las que el personal operativo indica necesitar capacitación")

# ======================
# APLICAR FILTROS A LA ENCUESTA COMPLETA
# ======================
# Filtramos df_encuesta según los filtros de sidebar para análisis dinámico
df_encuesta_filtrada = df_encuesta.copy()

if cliente_sel != "Todos":
    df_encuesta_filtrada = df_encuesta_filtrada[df_encuesta_filtrada[COL_CLIENTE] == cliente_sel]

if unidad_sel != "Todas":
    df_encuesta_filtrada = df_encuesta_filtrada[df_encuesta_filtrada[COL_UNIDAD] == unidad_sel]

# Total de encuestados después de aplicar filtros
total_encuestados_filtrados = len(df_encuesta_filtrada)

if total_encuestados_filtrados == 0:
    st.warning("⚠️ No hay encuestas para analizar con los filtros seleccionados")
else:
    st.info(f"📊 Analizando respuestas de **{total_encuestados_filtrados}** encuestados (según filtros aplicados)")
    
    # ======================
    # VERIFICAR EXISTENCIA DE COLUMNAS DE PREGUNTAS MÚLTIPLES
    # ======================
    preguntas_encontradas = []
    preguntas_no_encontradas = []
    
    for pregunta in PREGUNTAS_MULTIPLES:
        if pregunta in df_encuesta_filtrada.columns:
            preguntas_encontradas.append(pregunta)
        else:
            preguntas_no_encontradas.append(pregunta)
    
    if preguntas_no_encontradas:
        st.warning(f"⚠️ Columnas no encontradas en la encuesta: {preguntas_no_encontradas}")
        with st.expander("🔍 Ver columnas disponibles que contienen palabras clave"):
            for palabra in ["SEGURIDAD", "MAQUINARIA", "INSUMO", "CLIENTE", "OTRO"]:
                cols = [c for c in df_encuesta_filtrada.columns if palabra in c]
                if cols:
                    st.write(f"**{palabra}:** {cols}")
    
    if not preguntas_encontradas:
        st.error("❌ No se encontraron columnas de preguntas múltiples. Verifica los nombres exactos en el Excel.")
    else:
        # ======================
        # FUNCIÓN PARA DETECTAR SI UNA CELDA ESTÁ MARCADA
        # ======================
        def esta_marcada(valor):
            """
            Detecta si una celda de pregunta múltiple está marcada.
            
            Valores considerados como "marcado":
            - "SÍ", "SI", "X", "1", 1, True
            - Cualquier texto que no sea vacío, "NAN", "0", "NO"
            
            Valores considerados como "no marcado":
            - "", "NAN", "0", "NO", None, 0, False
            """
            if pd.isna(valor):
                return False
            
            valor_str = str(valor).strip().upper()
            
            # Valores que indican "no marcado"
            if valor_str in ["", "NAN", "0", "NO", "NONE"]:
                return False
            
            # Valores que indican "marcado"
            if valor_str in ["SÍ", "SI", "X", "1", "TRUE"]:
                return True
            
            # Si tiene cualquier otro texto, considerarlo marcado
            return len(valor_str) > 0
        
        # ======================
        # PROCESAR CADA PREGUNTA MÚLTIPLE
        # ======================
        resultados = []
        
        for pregunta in preguntas_encontradas:
            # Contar cuántos tienen la pregunta marcada
            marcados = df_encuesta_filtrada[pregunta].apply(esta_marcada).sum()
            
            # Calcular porcentaje sobre el total filtrado
            porcentaje = round((marcados / total_encuestados_filtrados) * 100, 1) if total_encuestados_filtrados > 0 else 0
            
            resultados.append({
                "ÁREA DE CAPACITACIÓN": pregunta,
                "CANTIDAD": int(marcados),
                "PORCENTAJE": porcentaje
            })
        
        # Crear DataFrame con resultados
        df_resultados = pd.DataFrame(resultados).sort_values("CANTIDAD", ascending=False)
        
        # ======================
        # VISUALIZACIÓN: GRÁFICO DE BARRAS
        # ======================
        st.subheader("📊 Áreas de Capacitación Solicitadas")
        
        df_resultados["LABEL"] = df_resultados.apply(
            lambda r: f"{r['CANTIDAD']} ({r['PORCENTAJE']}%)",
            axis=1
        )
        
        fig_capacitacion = px.bar(
            df_resultados,
            x="ÁREA DE CAPACITACIÓN",
            y="CANTIDAD",
            text="LABEL",
            title=f"Necesidades de Capacitación - Personal Operativo ({total_encuestados_filtrados} encuestados)",
            labels={
                "CANTIDAD": "Cantidad de menciones",
                "ÁREA DE CAPACITACIÓN": "Área"
            },
            color="PORCENTAJE",
            color_continuous_scale="Blues"
        )
        
        fig_capacitacion.update_traces(textposition="outside")
        fig_capacitacion.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode="hide",
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        st.plotly_chart(fig_capacitacion, use_container_width=True)
        
        # ======================
        # TABLA DE DETALLE
        # ======================
        st.subheader("📋 Detalle de Necesidades")
        st.dataframe(
            df_resultados[["ÁREA DE CAPACITACIÓN", "CANTIDAD", "PORCENTAJE"]],
            use_container_width=True
        )
        
        # ======================
        # ANÁLISIS POR CLIENTE (si no hay filtro de cliente específico)
        # ======================
        if cliente_sel == "Todos" and len(clientes) > 1:
            separador()
            st.subheader("🏢 Necesidades de Capacitación por Cliente")
            
            resultados_por_cliente = []
            
            for cliente in clientes:
                df_cliente = df_encuesta[df_encuesta[COL_CLIENTE] == cliente]
                total_cliente = len(df_cliente)
                
                if total_cliente > 0:
                    for pregunta in preguntas_encontradas:
                        marcados = df_cliente[pregunta].apply(esta_marcada).sum()
                        porcentaje = round((marcados / total_cliente) * 100, 1)
                        
                        resultados_por_cliente.append({
                            "CLIENTE": cliente,
                            "ÁREA": pregunta,
                            "CANTIDAD": int(marcados),
                            "TOTAL_ENCUESTADOS": total_cliente,
                            "PORCENTAJE": porcentaje
                        })
            
            df_por_cliente = pd.DataFrame(resultados_por_cliente)
            
            # Mostrar solo las 3 áreas más solicitadas por cada cliente
            st.write("**Top 3 necesidades por cliente:**")
            
            for cliente in clientes:
                df_top3 = df_por_cliente[df_por_cliente["CLIENTE"] == cliente].nlargest(3, "CANTIDAD")
                
                if not df_top3.empty:
                    st.write(f"**{cliente}** ({df_top3['TOTAL_ENCUESTADOS'].iloc[0]} encuestados):")
                    
                    for idx, row in df_top3.iterrows():
                        st.write(f"  • {row['ÁREA']}: {row['CANTIDAD']} ({row['PORCENTAJE']}%)")
                    
                    st.write("")
        
        # ======================
        # ANÁLISIS POR UNIDAD (si no hay filtro de unidad específico)
        # ======================
        if unidad_sel == "Todas" and len(unidades) > 1:
            separador()
            st.subheader("📍 Necesidades de Capacitación por Unidad")
            
            # Crear tabla pivote: Unidades en filas, Áreas en columnas
            resultados_por_unidad = []
            
            for unidad in unidades:
                df_unidad = df_encuesta[df_encuesta[COL_UNIDAD] == unidad]
                total_unidad = len(df_unidad)
                
                if total_unidad > 0:
                    fila = {"UNIDAD": unidad, "TOTAL_ENCUESTADOS": total_unidad}
                    
                    for pregunta in preguntas_encontradas:
                        marcados = df_unidad[pregunta].apply(esta_marcada).sum()
                        porcentaje = round((marcados / total_unidad) * 100, 1)
                        fila[pregunta] = f"{marcados} ({porcentaje}%)"
                    
                    resultados_por_unidad.append(fila)
            
            df_por_unidad = pd.DataFrame(resultados_por_unidad)
            
            st.dataframe(df_por_unidad, use_container_width=True)

# ======================
# FOOTER
# ======================
separador()
st.caption("📊 Dashboard Encuesta Limtek - Personal Operativo | Desarrollado con Streamlit")
