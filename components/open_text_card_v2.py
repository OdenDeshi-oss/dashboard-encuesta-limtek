import pandas as pd
import streamlit as st
import plotly.express as px
from core.text_classifier import classify_open_ended


def render_pregunta_abierta_v2(df, titulo, col_valor, categorias):
    """
    Tarjeta de respuestas abiertas con categorización temática.
    Muestra: gráfico de barras por categoría + ejemplos + detalle filtrable.
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

    # Clasificar
    df_clasificado = classify_open_ended(serie, categorias)

    # Conteo por categoría
    conteo = df_clasificado["Categoria"].value_counts()

    df_plot = pd.DataFrame({
        "Categoría": conteo.index,
        "Cantidad": conteo.values,
    })
    df_plot["Porcentaje"] = (df_plot["Cantidad"] / total * 100).round(1)
    df_plot["LABEL"] = df_plot.apply(
        lambda r: f"{int(r['Cantidad'])}  ({r['Porcentaje']}%)", axis=1
    )

    top_cat = df_plot.iloc[0]["Categoría"]
    top_pct = df_plot.iloc[0]["Porcentaje"]
    top_cant = int(df_plot.iloc[0]["Cantidad"])

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
                    <div class="likert-kpi-value">{total}</div>
                    <div class="likert-kpi-label">Respuestas analizadas</div>
                    <div class="likert-kpi-sub">100%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="multi-top-badge">
                    🏆 <b>{top_cat}</b><br>
                    <span>{top_cant} respuestas ({top_pct}%)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_chart:
            fig = px.bar(
                df_plot,
                x="Cantidad",
                y="Categoría",
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
                height=max(250, len(df_plot) * 50),
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

        # ── Ejemplos por categoría (top 3) ──
        st.markdown(
            '<div class="scroll-table-header">📋 Ejemplos por categoría</div>',
            unsafe_allow_html=True,
        )

        # Selector de categoría
        cats_disponibles = df_plot["Categoría"].tolist()
        cat_sel = st.selectbox(
            "Filtrar por categoría",
            options=["Todas"] + cats_disponibles,
            key=f"cat_{col_valor}",
        )

        if cat_sel == "Todas":
            df_mostrar = df_clasificado
        else:
            df_mostrar = df_clasificado[df_clasificado["Categoria"] == cat_sel]

        # Tabla HTML (evita pyarrow)
        filas = df_mostrar.head(200)
        filas_html = ""
        for i, row in enumerate(filas.itertuples(), 1):
            filas_html += (
                f"<tr>"
                f"<td style='padding:6px 10px;color:#888;width:40px;'>{i}</td>"
                f"<td style='padding:6px 10px;color:#0b1b6f;font-weight:600;width:160px;'>{row.Categoria}</td>"
                f"<td style='padding:6px 10px;color:#333;'>{row.Respuesta}</td>"
                f"</tr>"
            )

        st.markdown(
            f"""
            <div style="max-height:300px;overflow-y:auto;background:#fff;border-radius:8px;border:1px solid #e8ecf1;">
                <table style="width:100%;border-collapse:collapse;font-size:13px;">
                    <thead><tr style="background:#f0f4fa;position:sticky;top:0;">
                        <th style="padding:8px 10px;text-align:left;color:#0b1b6f;">#</th>
                        <th style="padding:8px 10px;text-align:left;color:#0b1b6f;">Categoría</th>
                        <th style="padding:8px 10px;text-align:left;color:#0b1b6f;">Respuesta</th>
                    </tr></thead>
                    <tbody>{filas_html}</tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
