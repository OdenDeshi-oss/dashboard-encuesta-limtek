import pandas as pd
import streamlit as st
import plotly.express as px


def render_pregunta_multiple(df, titulo, columnas, etiquetas=None):
    """
    Tarjeta con barras horizontales para preguntas de selección múltiple (checkbox).
    """

    cols_validas = [c for c in columnas if c in df.columns]
    if not cols_validas:
        st.warning(f"⚠️ No se encontraron las columnas: {columnas}")
        return

    total = len(df)
    if total == 0:
        st.warning("⚠️ Sin respuestas válidas")
        return

    conteos = {}
    for col in cols_validas:
        label = etiquetas[col] if etiquetas and col in etiquetas else col
        conteos[label] = int(df[col].notna().sum())

    conteos = dict(sorted(conteos.items(), key=lambda x: x[1], reverse=True))

    df_plot = pd.DataFrame({
        "Opción": list(conteos.keys()),
        "Cantidad": list(conteos.values()),
    })
    df_plot["Porcentaje"] = (df_plot["Cantidad"] / total * 100).round(1)
    df_plot["LABEL"] = df_plot.apply(
        lambda r: f"{int(r['Cantidad'])}  ({r['Porcentaje']}%)", axis=1
    )

    # KPI: dato top
    opcion_top = df_plot.iloc[0]["Opción"]
    top_cantidad = int(df_plot.iloc[0]["Cantidad"])
    top_pct = df_plot.iloc[0]["Porcentaje"]

    # Nombre corto para el top
    nombres_cortos = {
        "SEGURIDAD Y SALUD EN EL TRABAJO": "SST",
        "USO DE MAQUINARIAS Y EQUIPOS": "Maquinarias",
        "USO DE INSUMOS": "Insumos",
        "ATENCIÓN AL CLIENTE": "Atención al cliente",
        "OTRO (ESPECIFIQUE)": "Otro",
    }
    top_corto = nombres_cortos.get(opcion_top, opcion_top)

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
                    <div class="likert-kpi-label">Prioridad #1: {top_corto}</div>
                    <div class="likert-kpi-sub">{top_cantidad} de {total}</div>
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
                height=max(220, len(df_plot) * 60),
                showlegend=False,
                margin=dict(l=10, r=80, t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, showticklabels=False, title=""),
                yaxis=dict(
                    title="",
                    tickfont=dict(size=13, color="#333333", weight="bold"),
                    autorange="reversed",
                    automargin=True,
                ),
                hovermode=False,
                bargap=0.35,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
            )
