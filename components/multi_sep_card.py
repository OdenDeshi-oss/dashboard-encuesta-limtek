import pandas as pd
import streamlit as st
import plotly.express as px


def render_pregunta_multi_separador(df, titulo, col_valor, separador=";"):
    """
    Tarjeta con barras horizontales para preguntas de selección múltiple
    donde las opciones están en UNA sola columna separadas por un carácter.

    Parámetros
    ----------
    df : DataFrame
    titulo : str – Texto del encabezado azul.
    col_valor : str – Nombre de la columna.
    separador : str – Carácter separador (";" o "\\n").
    """

    if col_valor not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_valor}")
        return

    serie = df[col_valor].dropna().astype(str).str.strip()
    serie = serie[serie != ""]
    if serie.empty:
        st.warning("⚠️ Sin respuestas válidas")
        return

    total_personas = len(serie)

    # Separar y contar cada opción
    todas = []
    for texto in serie:
        opciones = [op.strip() for op in texto.split(separador) if op.strip()]
        todas.extend(opciones)

    conteo = pd.Series(todas).value_counts()

    df_plot = pd.DataFrame({
        "Opción": conteo.index,
        "Cantidad": conteo.values,
    })
    df_plot["Porcentaje"] = (df_plot["Cantidad"] / total_personas * 100).round(1)
    df_plot["LABEL"] = df_plot.apply(
        lambda r: f"{int(r['Cantidad'])}  ({r['Porcentaje']}%)", axis=1
    )

    # KPI
    opcion_top = df_plot.iloc[0]["Opción"]
    top_cantidad = int(df_plot.iloc[0]["Cantidad"])
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
                    <div class="likert-kpi-label">Prioridad #1</div>
                    <div class="likert-kpi-sub">{top_cantidad} de {total_personas}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="multi-top-badge">
                    🏆 <b>{opcion_top}</b><br>
                    <span>{top_pct}% de los encuestados</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_chart:
            fig = px.bar(
                df_plot,
                x="Cantidad",
                y="Opción",
                text="LABEL",
                orientation="h",
            )

            fig.update_traces(
                textposition="outside",
                cliponaxis=False,
                textfont=dict(size=14, weight="bold", color="#0b1b6f"),
                marker_color="#3b78c2",
            )

            fig.update_layout(
                height=max(220, len(df_plot) * 55),
                showlegend=False,
                margin=dict(l=10, r=80, t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, showticklabels=False, title=""),
                yaxis=dict(
                    title="",
                    tickfont=dict(size=12, color="#333333", weight="bold"),
                    autorange="reversed",
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
