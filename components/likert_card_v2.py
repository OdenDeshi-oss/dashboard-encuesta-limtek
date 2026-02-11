import pandas as pd
import streamlit as st
import plotly.express as px
from core.config import ESCALA_ACUERDO, NEUTRAL, SCALE_MAX, PREGUNTAS_INVERTIDAS
from core.metrics import compute_likert_metrics


def render_pregunta_v2(df, titulo, col_valor, escala=None, invert=False):
    """
    Tarjeta Likert escala 1–5.
    El valor 3 (neutral) se incluye en cálculos pero NO se grafica.
    """

    if escala is None:
        escala = ESCALA_ACUERDO

    if col_valor not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_valor}")
        return

    # Verificar si la pregunta es invertida
    if col_valor in PREGUNTAS_INVERTIDAS:
        invert = True

    metrics = compute_likert_metrics(df[col_valor], invert=invert)

    if metrics is None:
        st.warning("⚠️ Sin respuestas válidas")
        return

    conteo = metrics["conteo"]
    n = metrics["n"]
    promedio = metrics["promedio"]
    nivel_pct = metrics["nivel_pct"]

    # Construir df para gráfico SIN el valor neutral (3)
    valores_visibles = [v for v in range(1, SCALE_MAX + 1) if v != NEUTRAL]

    df_plot = pd.DataFrame({
        "Etiqueta": [escala[v] for v in valores_visibles],
        "Cantidad": [int(conteo.get(v, 0)) for v in valores_visibles],
    })

    total_visible = df_plot["Cantidad"].sum()
    if total_visible > 0:
        df_plot["Porcentaje"] = (df_plot["Cantidad"] / n * 100).round(1)
    else:
        df_plot["Porcentaje"] = 0.0

    df_plot["LABEL"] = df_plot.apply(
        lambda r: f"{int(r['Cantidad'])} ({r['Porcentaje']}%)", axis=1
    )

    # Color del indicador según promedio
    if promedio >= 4:
        color_estado = "#2e7d32"  # verde
    elif promedio >= 3:
        color_estado = "#f9a825"  # amarillo
    else:
        color_estado = "#c62828"  # rojo

    with st.container():

        st.markdown(
            f"""
            <div class="card-header">
                <b>Detalle</b><br>{titulo}
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_kpi, col_chart = st.columns([1, 3], gap="medium")

        with col_kpi:
            st.markdown(
                f"""
                <div class="likert-kpi">
                    <div class="likert-kpi-value">{promedio}</div>
                    <div class="likert-kpi-label">Promedio (n={n})</div>
                    <div class="likert-kpi-sub">{nivel_pct}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Mini indicadores cumple/no cumple
            st.markdown(
                f"""
                <div class="cumple-badges">
                    <div class="badge-positivo">✅ {metrics['pct_positivo']}% positivo</div>
                    <div class="badge-negativo">⚠️ {metrics['pct_negativo']}% negativo</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_chart:
            # Colores: rojo para 1-2, verde para 4-5
            colores = ["#e53935", "#ff7043", "#43a047", "#2e7d32"]

            fig = px.bar(
                df_plot,
                x="Etiqueta",
                y="Cantidad",
                text="LABEL",
                category_orders={"Etiqueta": [escala[v] for v in valores_visibles]},
            )

            fig.update_traces(
                width=0.5,
                textposition="outside",
                cliponaxis=False,
                textfont=dict(size=14, weight="bold", color="#0b1b6f"),
                marker_color=colores,
            )

            fig.update_layout(
                height=300,
                showlegend=False,
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=False, showticklabels=False, title=""),
                xaxis=dict(
                    title="",
                    tickfont=dict(size=11, color="#333333", weight="bold"),
                    automargin=True,
                ),
                hovermode=False,
                bargap=0.3,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
                key=f"likert_{col_valor}",
            )
