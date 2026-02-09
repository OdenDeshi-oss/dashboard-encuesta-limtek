import pandas as pd
import streamlit as st
import plotly.express as px
import re
from collections import Counter


STOPWORDS = {
    "de", "la", "el", "en", "y", "a", "que", "los", "las", "un", "una",
    "es", "por", "su", "del", "se", "con", "no", "lo", "al", "le", "da",
    "nos", "mi", "muy", "más", "para", "como", "sus", "hay", "sin", "son",
    "fue", "ser", "les", "ya", "o", "e", "todo", "esta", "pero", "ha",
    "me", "si", "te", "ni", "otro", "otros", "san", "tan", "cada",
}


def render_pregunta_abierta(df, titulo, col_valor, top_n=10):
    """
    Tarjeta con top palabras clave + tabla con scroll para preguntas abiertas.
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

    # ── Análisis de palabras clave ──
    all_words = []
    for text in serie.str.lower():
        words = re.findall(r"[a-záéíóúñ]+", text)
        all_words.extend([w for w in words if w not in STOPWORDS and len(w) > 2])

    top_words = Counter(all_words).most_common(top_n)

    df_words = pd.DataFrame(top_words, columns=["Palabra", "Frecuencia"])
    df_words["Porcentaje"] = (df_words["Frecuencia"] / total * 100).round(1)
    df_words["LABEL"] = df_words.apply(
        lambda r: f"{r['Frecuencia']}  ({r['Porcentaje']}%)", axis=1
    )

    # Palabra top
    top_palabra = df_words.iloc[0]["Palabra"].capitalize()
    top_freq = int(df_words.iloc[0]["Frecuencia"])
    top_pct = df_words.iloc[0]["Porcentaje"]

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

        # ── KPI ──
        with col_kpi:
            st.markdown(
                f"""
                <div class="likert-kpi">
                    <div class="likert-kpi-value">{total}</div>
                    <div class="likert-kpi-label">Respuestas recibidas</div>
                    <div class="likert-kpi-sub">100%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="multi-top-badge">
                    💬 Palabra más frecuente<br>
                    <b style="font-size:18px;">{top_palabra}</b><br>
                    <span>Mencionada {top_freq} veces ({top_pct}%)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Gráfico top palabras ──
        with col_chart:
            fig = px.bar(
                df_words,
                x="Frecuencia",
                y="Palabra",
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
                height=max(280, top_n * 36),
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
                bargap=0.3,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": True},
            )

        # ── Tabla con scroll ──
        st.markdown(
            f"""
            <div class="scroll-table-header">
                📋 Todas las respuestas ({total})
            </div>
            """,
            unsafe_allow_html=True,
        )

        df_tabla = pd.DataFrame({"Respuesta": serie.values})
        df_tabla.index = range(1, len(df_tabla) + 1)
        df_tabla.index.name = "#"

        st.dataframe(
            df_tabla,
            use_container_width=True,
            height=300,
        )