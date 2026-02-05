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
st.caption("Resultados de satisfacción – Escala 1 a 4")

# ======================
# UTILIDADES
# ======================
def separador():
    st.markdown("---")

def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.upper()
    return df

# ======================
# RUTA ENCUESTA
# ======================
ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_ CIERRE 2026.xlsx"

if not os.path.exists(ENCUESTA_PATH):
    st.error("❌ No se encontró el archivo de encuesta")
    st.stop()

df = pd.read_excel(ENCUESTA_PATH, engine="openpyxl")
df = normalizar_columnas(df)

# ======================
# DEFINICIÓN DE PREGUNTAS LIKERT
# ======================
PREGUNTAS_LIKERT = [
    {
        "titulo": "Me siento a gusto con el ambiente de trabajo que se genera en mi equipo",
        "col": "VALOR_AMBIENTE_TRABAJO"
    },
    {
        "titulo": "Me siento motivado a dar lo mejor de mí y hacer un buen trabajo",
        "col": "VALOR_MOTIVACIÓN"
    },
    {
        "titulo": "Mi supervisor o jefe directo me otorga el soporte que necesito para afrontar cualquier problema que afecte mi trabajo",
        "col": "VALOR_SOPORTE_JEFE"
    },
    {
        "titulo": "Mi supervisor o jefe directo fomenta que nos apoyemos entre todos en el equipo",
        "col": "VALOR_TRABAJO_EQUIPO"
    },
    {
        "titulo": "Siento que mi trabajo es reconocido por mi supervisor o jefe directo",
        "col": "VALOR_RECONOCIMIENTO"
    },
    {
        "titulo": "Mi supervisor o jefe directo nos brinda charlas de 5 minutos y comunica las novedades relevantes a mi puesto de trabajo",
        "col": "VALOR_COMUNICACIÓN_JEFE"
    },
]

# ======================
# MAPEO ESCALA
# ======================
ESCALA = {
    1: "Totalmente en desacuerdo",
    2: "Parcialmente en desacuerdo",
    3: "Parcialmente de acuerdo",
    4: "Totalmente de acuerdo"
}

# ======================
# FUNCIÓN RENDER PREGUNTA
# ======================
def render_pregunta(df, titulo, col_valor):
    if col_valor not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_valor}")
        return

    serie = pd.to_numeric(df[col_valor], errors="coerce").dropna()
    total = len(serie)

    if total == 0:
        st.warning("⚠️ Sin respuestas válidas")
        return

    conteo = serie.value_counts().reindex([1, 2, 3, 4], fill_value=0)
    porcentaje = round((conteo / total) * 100, 2)

    promedio = round(serie.mean(), 2)
    nivel = round((promedio / 4) * 100, 2)

    df_plot = pd.DataFrame({
        "Nivel": conteo.index,
        "Etiqueta": [ESCALA[i] for i in conteo.index],
        "Cantidad": conteo.values,
        "Porcentaje": porcentaje.values
    })

    df_plot["LABEL"] = df_plot.apply(
        lambda r: f"{r['Cantidad']} ({r['Porcentaje']}%)", axis=1
    )

    # ======================
    # LAYOUT TARJETA
    # ======================
    st.markdown(
        f"""
        <div style="background-color:#3b78c2;padding:12px;border-radius:6px;color:white;">
            <b>Detalle</b><br>{titulo}
        </div>
        """,
        unsafe_allow_html=True
    )

    col_kpi, col_chart = st.columns([1, 3])

    with col_kpi:
        st.markdown(
            f"""
            <div style="background-color:#f5f7fa;padding:20px;border-radius:6px;text-align:center;">
                <h1 style="color:#3b78c2">{promedio}</h1>
                <div style="color:#3b78c2">Nivel alcanzado</div>
                <h3 style="color:#3b78c2">{nivel}%</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_chart:
        fig = px.bar(
            df_plot,
            x="Etiqueta",
            y="Cantidad",
            text="LABEL",
            category_orders={"Etiqueta": list(ESCALA.values())},
            labels={"Cantidad": ""},
        )
        fig.update_traces(marker_color="#1f497d", textposition="outside")
        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            uniformtext_minsize=10,
            uniformtext_mode="hide"
        )
        st.plotly_chart(fig, use_container_width=True)

    separador()

# ======================
# RENDERIZAR TODAS LAS PREGUNTAS
# ======================
for p in PREGUNTAS_LIKERT:
    render_pregunta(df, p["titulo"], p["col"])

# ======================
# FOOTER
# ======================
st.caption("📊 Dashboard Encuesta Limtek – Personal Operativo")
