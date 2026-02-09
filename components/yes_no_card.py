import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def render_pregunta_si_no(df, titulo, col_valor):
    """
    Tarjeta con donut chart para preguntas de Sí/No.
    """

    if col_valor not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_valor}")
        return

    serie = df[col_valor].dropna().astype(str).str.strip().str.upper()
    if serie.empty:
        st.warning("⚠️ Sin respuestas válidas")
        return

    total = len(serie)
    si_count = int((serie == "SÍ").sum() + (serie == "SI").sum())
    no_count = total - si_count

    si_pct = round(si_count / total * 100, 1)
    no_pct = round(no_count / total * 100, 1)

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
                    <div class="likert-kpi-value">{si_pct}%</div>
                    <div class="likert-kpi-label">Respondieron Sí</div>
                    <div class="likert-kpi-sub">{si_count} de {total}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_chart:
            colors = ["#3b78c2", "#c8d6e5"]

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=["Sí", "No"],
                        values=[si_count, no_count],
                        hole=0.55,
                        marker=dict(colors=colors, line=dict(color="#ffffff", width=3)),
                        textinfo="label+percent",
                        textfont=dict(size=16, color="#0b1b6f", weight="bold"),
                        hoverinfo="skip",
                    )
                ]
            )

            fig.update_layout(
                height=300,
                showlegend=False,
                margin=dict(l=10, r=10, t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        text=f"<b>{si_pct}%</b><br>Sí",
                        x=0.5,
                        y=0.5,
                        font=dict(size=28, color="#0b1b6f"),
                        showarrow=False,
                    )
                ],
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
            )