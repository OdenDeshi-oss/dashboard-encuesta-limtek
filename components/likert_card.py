import pandas as pd
import streamlit as st
import plotly.express as px
from core.constants import ESCALA
from components.utils import separador

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
