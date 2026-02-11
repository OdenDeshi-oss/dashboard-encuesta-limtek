import pandas as pd
import streamlit as st
import plotly.express as px
from core.metrics import compute_likert_metrics


def render_ranking_areas(df, col_area, cols_valor, titulo="Ranking por Área"):
    """
    Muestra ranking de áreas con promedio general, % positivo y % negativo.

    Parámetros
    ----------
    df : DataFrame
    col_area : str – Nombre de la columna de área.
    cols_valor : list[str] – Columnas numéricas Likert a promediar.
    titulo : str
    """

    if col_area not in df.columns:
        st.warning(f"⚠️ No se encontró la columna {col_area}")
        return

    cols_existentes = [c for c in cols_valor if c in df.columns]
    if not cols_existentes:
        st.warning("⚠️ No se encontraron columnas de valor")
        return

    areas = df[col_area].dropna().unique()
    resultados = []

    for area in areas:
        df_area = df[df[col_area] == area]
        promedios = []
        positivos = []
        negativos = []

        for col in cols_existentes:
            m = compute_likert_metrics(df_area[col])
            if m:
                promedios.append(m["promedio"])
                positivos.append(m["pct_positivo"])
                negativos.append(m["pct_negativo"])

        if promedios:
            resultados.append({
                "Área": area,
                "Promedio": round(sum(promedios) / len(promedios), 2),
                "% Positivo": round(sum(positivos) / len(positivos), 1),
                "% Negativo": round(sum(negativos) / len(negativos), 1),
                "n": len(df_area),
            })

    if not resultados:
        st.warning("⚠️ Sin datos para ranking")
        return

    df_rank = pd.DataFrame(resultados).sort_values("Promedio", ascending=False)

    with st.container():

        st.markdown(
            f"""
            <div class="card-header">
                <b>{titulo}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Gráfico de barras horizontales
        fig = px.bar(
            df_rank,
            x="Promedio",
            y="Área",
            text=df_rank.apply(
                lambda r: f"{r['Promedio']}  (✅{r['% Positivo']}% | ⚠️{r['% Negativo']}%)",
                axis=1,
            ),
            orientation="h",
        )

        # Colores según promedio
        colores = []
        for p in df_rank["Promedio"]:
            if p >= 4:
                colores.append("#43a047")
            elif p >= 3:
                colores.append("#ffa726")
            else:
                colores.append("#e53935")

        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=13, weight="bold", color="#0b1b6f"),
            marker_color=colores,
        )

        fig.update_layout(
            height=max(300, len(df_rank) * 45),
            showlegend=False,
            margin=dict(l=10, r=120, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, showticklabels=False, title="", range=[0, 5.5]),
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
