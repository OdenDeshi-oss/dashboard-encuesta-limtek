import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def render_nps(df, titulo, col_valor):
    """
    Tarjeta con gauge NPS para preguntas de escala 0-10.
    Detractores (0-6), Pasivos (7-8), Promotores (9-10).
    """

    if col_valor not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_valor}")
        return

    serie = pd.to_numeric(df[col_valor], errors="coerce").dropna()
    if serie.empty:
        st.warning("⚠️ Sin respuestas válidas")
        return

    total = len(serie)
    promotores = int((serie >= 9).sum())
    pasivos = int(((serie >= 7) & (serie <= 8)).sum())
    detractores = int((serie <= 6).sum())

    pct_prom = round(promotores / total * 100, 1)
    pct_det = round(detractores / total * 100, 1)
    nps = round(pct_prom - pct_det, 1)

    promedio = round(serie.mean(), 1)

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
            # Color según NPS
            if nps >= 50:
                nps_color = "#2e7d32"
                nps_label = "Excelente"
            elif nps >= 0:
                nps_color = "#3b78c2"
                nps_label = "Bueno"
            else:
                nps_color = "#c62828"
                nps_label = "Necesita mejorar"

            st.markdown(
                f"""
                <div class="likert-kpi">
                    <div class="likert-kpi-value" style="color:{nps_color};">{nps}</div>
                    <div class="likert-kpi-label">NPS Score</div>
                    <div class="likert-kpi-sub">{nps_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="multi-top-badge">
                    ⭐ Promedio: <b>{promedio}/10</b><br>
                    <span>{total} respuestas</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_chart:
            fig = go.Figure()

            categories = ["Detractores<br>(0-6)", "Pasivos<br>(7-8)", "Promotores<br>(9-10)"]
            values = [detractores, pasivos, promotores]
            colors = ["#e53935", "#ffa726", "#43a047"]
            pcts = [
                round(detractores / total * 100, 1),
                round(pasivos / total * 100, 1),
                round(promotores / total * 100, 1),
            ]
            labels = [f"{v} ({p}%)" for v, p in zip(values, pcts)]

            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=values,
                    text=labels,
                    textposition="inside",
                    textangle=0,
                    textfont=dict(size=14, weight="bold", color="#0b1b6f"),
                    marker_color=colors,
                    width=0.5,
                )
            )

            fig.update_layout(
                height=380,
                showlegend=False,
                margin=dict(l=10, r=10, t=50, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=False, showticklabels=False, title=""),
                xaxis=dict(
                    title="",
                    tickfont=dict(size=12, color="#333333", weight="bold"),
                ),
                hovermode=False,
                bargap=0.3,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
            )
