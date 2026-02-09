import pandas as pd
import streamlit as st
import plotly.express as px


def render_pregunta_categorica(df, titulo, col_valor, orden=None):
    """
    Tarjeta con barras verticales para preguntas categóricas con orden lógico.

    Parámetros
    ----------
    df : DataFrame
    titulo : str – Texto del encabezado azul.
    col_valor : str – Nombre de la columna.
    orden : list[str] | None – Orden de las categorías.
    """

    if col_valor not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_valor}")
        return

    serie = df[col_valor].dropna().astype(str).str.strip()
    serie = serie[serie != ""]
    if serie.empty:
        st.warning("⚠️ Sin respuestas válidas")
        return

    total = len(serie)
    conteo = serie.value_counts()

    if orden:
        conteo = conteo.reindex(orden, fill_value=0)

    df_plot = pd.DataFrame({
        "Categoría": conteo.index,
        "Cantidad": conteo.values,
    })
    df_plot["Porcentaje"] = (df_plot["Cantidad"] / total * 100).round(1)
    df_plot["LABEL"] = df_plot.apply(
        lambda r: f"{int(r['Cantidad'])} ({r['Porcentaje']}%)", axis=1
    )

    # KPI: categoría con más personas
    top_cat = df_plot.iloc[0]["Categoría"]
    top_cant = int(df_plot.iloc[0]["Cantidad"])
    top_pct = df_plot.iloc[0]["Porcentaje"]

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
                    <div class="likert-kpi-value">{top_pct}%</div>
                    <div class="likert-kpi-label">Mayor grupo</div>
                    <div class="likert-kpi-sub">{top_cat}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="multi-top-badge">
                    👥 <b>{top_cant}</b> personas<br>
                    <span>{top_cat}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_chart:
            fig = px.bar(
                df_plot,
                x="Categoría",
                y="Cantidad",
                text="LABEL",
                category_orders={"Categoría": orden} if orden else None,
            )

            fig.update_traces(
                width=0.5,
                textposition="outside",
                cliponaxis=False,
                textfont=dict(size=14, weight="bold", color="#0b1b6f"),
                marker_color="#3b78c2",
            )

            fig.update_layout(
                height=340,
                showlegend=False,
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=False, showticklabels=False, title=""),
                xaxis=dict(
                    title="",
                    tickfont=dict(size=12, color="#333333", weight="bold"),
                    automargin=True,
                ),
                hovermode=False,
                bargap=0.3,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
            )