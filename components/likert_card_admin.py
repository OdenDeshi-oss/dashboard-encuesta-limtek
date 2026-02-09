import pandas as pd
import streamlit as st
import plotly.express as px


def render_pregunta_admin(df, titulo, col_valor, escala):
    """
    Tarjeta Likert que acepta cualquier escala (acuerdo o frecuencia).

    Parámetros
    ----------
    df : DataFrame
    titulo : str – Texto del encabezado azul.
    col_valor : str – Columna con valores numéricos (1-4).
    escala : dict – Mapeo {1: "label", 2: "label", 3: "label", 4: "label"}.
    """

    if col_valor not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_valor}")
        return

    serie = pd.to_numeric(df[col_valor], errors="coerce").dropna()
    if serie.empty:
        st.warning("⚠️ Sin respuestas válidas")
        return

    conteo = serie.value_counts().reindex([1, 2, 3, 4], fill_value=0)
    total = int(conteo.sum())
    promedio = round(serie.mean(), 2)
    nivel = round((promedio / 4) * 100, 2)
    porcentaje = (conteo / total * 100).round(2)

    df_plot = pd.DataFrame({
        "Etiqueta": [escala[i] for i in conteo.index],
        "Cantidad": conteo.values,
        "Porcentaje": porcentaje.values,
    })
    df_plot["LABEL"] = df_plot.apply(
        lambda r: f"{int(r['Cantidad'])} ({r['Porcentaje']:.1f}%)", axis=1
    )

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
                    <div class="likert-kpi-label">Nivel alcanzado</div>
                    <div class="likert-kpi-sub">{nivel}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_chart:
            fig = px.bar(
                df_plot,
                x="Etiqueta",
                y="Cantidad",
                text=df_plot["LABEL"],
                category_orders={"Etiqueta": list(escala.values())},
            )

            fig.update_traces(
                width=0.5,
                textposition="outside",
                cliponaxis=False,
                textfont=dict(size=14, weight="bold", color="#0b1b6f"),
                marker_color="#3b78c2",
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
                    tickfont=dict(size=13, color="#333333", weight="bold"),
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
