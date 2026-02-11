import streamlit as st
import pandas as pd
import base64
from pathlib import Path

st.set_page_config(page_title="Dashboard Encuesta Limtek – Administrativo", layout="wide")

def load_css(path: str):
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/styles.css")

from layout.header import render_header
from core.loader import cargar_encuesta_admin, cargar_inventario_admin
from core.config import (
    ESCALA_ACUERDO, ESCALA_FRECUENCIA,
    PREGUNTAS_ACUERDO_ADMIN, PREGUNTAS_FRECUENCIA_ADMIN,
    CATEGORIAS_POSITIVAS, CATEGORIAS_MEJORA,
)
from core.metrics import compute_likert_metrics
from sections.metodologia import render_metodologia
from components.likert_card_v2 import render_pregunta_v2
from components.category_card import render_pregunta_categorica
from components.multi_sep_card import render_pregunta_multi_separador
from components.nps_card import render_nps
from components.open_text_card_v2 import render_pregunta_abierta_v2

# ── SIDEBAR LOGO ──
def render_sidebar_logo(logo_path: str):
    img_bytes = Path(logo_path).read_bytes()
    logo_base64 = base64.b64encode(img_bytes).decode()
    st.sidebar.markdown(
        f"""<div style="display:flex;justify-content:center;margin:16px 0 24px 0;">
        <img src="data:image/png;base64,{logo_base64}" style="width:450px;max-width:100%;opacity:0.95;"></div>""",
        unsafe_allow_html=True,
    )

render_sidebar_logo("assets/logo_limtek.png")

# ══════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════
df_raw = cargar_encuesta_admin()

col_area = "ÁREA"
col_jefe = "JEFE INMEDIATO"

# ══════════════════════════════════════════
# FILTROS SIDEBAR
# ══════════════════════════════════════════
st.sidebar.markdown("### 🎯 Segmentadores")

if col_area in df_raw.columns:
    areas = sorted(df_raw[col_area].dropna().astype(str).str.strip().unique().tolist())
    area_sel = st.sidebar.selectbox("Área", ["Todas"] + areas, key="filtro_area_admin")
else:
    area_sel = "Todas"

df_ctx = df_raw.copy()
if area_sel != "Todas" and col_area in df_ctx.columns:
    df_ctx = df_ctx[df_ctx[col_area] == area_sel]

if col_jefe in df_raw.columns:
    jefes = sorted(df_ctx[col_jefe].dropna().astype(str).str.strip().unique().tolist())
    jefe_sel = st.sidebar.selectbox("Jefe Inmediato", ["Todos"] + jefes, key="filtro_jefe_admin")
else:
    jefe_sel = "Todos"

df = df_raw.copy()
if area_sel != "Todas" and col_area in df.columns:
    df = df[df[col_area] == area_sel]
if jefe_sel != "Todos" and col_jefe in df.columns:
    df = df[df[col_jefe] == jefe_sel]

# ══════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════
render_header(
    titulo="Dashboard Encuesta – Personal Administrativo",
    subtitulo="#ExpertosapoyandoExpertos",
)

# ══════════════════════════════════════════
# KPIs SUPERIORES
# ══════════════════════════════════════════
total_encuestados = len(df)
total_inventario = cargar_inventario_admin()
participacion_pct = round(total_encuestados / total_inventario * 100, 1) if total_inventario > 0 else 0

colA, colB = st.columns(2, gap="large")

with colA:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-card-title">Cobertura de la encuesta</div>
        <div class="kpi-row">
        <div class="kpi-item"><div class="kpi-value">{total_encuestados}</div><div class="kpi-label">Encuestados</div></div>
        <div class="kpi-item"><div class="kpi-value kpi-ok">{participacion_pct}%</div><div class="kpi-label">Participación</div>
        <div class="kpi-sub">{total_encuestados} / {total_inventario}</div></div>
        </div></div>""",
        unsafe_allow_html=True,
    )

with colB:
    n_areas = df[col_area].nunique() if col_area in df.columns else "—"
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-card-title">Distribución</div>
        <div class="kpi-row">
        <div class="kpi-item"><div class="kpi-value">{n_areas}</div><div class="kpi-label">Áreas participantes</div></div>
        <div class="kpi-item"><div class="kpi-value">{total_encuestados}</div><div class="kpi-label">Colaboradores</div>
        <div class="kpi-sub">Personal administrativo</div></div>
        </div></div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom:32px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# METODOLOGÍA
# ══════════════════════════════════════════
render_metodologia()

# ══════════════════════════════════════════
# CUMPLIMIENTO POR ÁREA (siempre usa df_raw)
# ══════════════════════════════════════════
st.markdown("## 📊 Cumplimiento por Área")

cols_valor_admin = [c for c in df_raw.columns if c.startswith("VALOR_")]

if col_area in df_raw.columns and cols_valor_admin:
    areas_todas = df_raw[col_area].dropna().unique()
    resultados = []

    for area in areas_todas:
        df_area = df_raw[df_raw[col_area] == area]
        n_area = len(df_area)
        promedios = []
        positivos = []
        negativos = []

        for col in cols_valor_admin:
            m = compute_likert_metrics(df_area[col])
            if m:
                promedios.append(m["promedio"])
                positivos.append(m["pct_positivo"])
                negativos.append(m["pct_negativo"])

        if promedios:
            resultados.append({
                "Área": area,
                "Colaboradores": n_area,
                "Promedio": round(sum(promedios) / len(promedios), 2),
                "% Positivo (4-5)": round(sum(positivos) / len(positivos), 1),
                "% Negativo (1-2)": round(sum(negativos) / len(negativos), 1),
            })

    if resultados:
        df_rank = pd.DataFrame(resultados).sort_values("Promedio", ascending=False)

        filas_html = ""
        for _, r in df_rank.iterrows():
            color_prom = "#2e7d32" if r["Promedio"] >= 4 else "#f9a825" if r["Promedio"] >= 3 else "#c62828"
            filas_html += f"""<tr>
                <td style="padding:10px 12px;font-weight:600;color:#0b1b6f;">{r['Área']}</td>
                <td style="padding:10px 12px;text-align:center;">{int(r['Colaboradores'])}</td>
                <td style="padding:10px 12px;text-align:center;font-weight:700;color:{color_prom};">{r['Promedio']}</td>
                <td style="padding:10px 12px;text-align:center;color:#2e7d32;font-weight:600;">{r['% Positivo (4-5)']}%</td>
                <td style="padding:10px 12px;text-align:center;color:#c62828;font-weight:600;">{r['% Negativo (1-2)']}%</td>
            </tr>"""

        with st.container():
            st.markdown(
                """
                <div class="card-header">
                    <b>Cumplimiento general por Área</b><br>
                    Promedio de todas las preguntas Likert · Escala 1–5
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style="background:#fff;border-radius:10px;border:1px solid #e8ecf1;overflow:hidden;">
                    <table style="width:100%;border-collapse:collapse;font-size:13px;">
                        <thead><tr style="background:#f0f4fa;">
                            <th style="padding:10px 12px;text-align:left;color:#0b1b6f;">Área</th>
                            <th style="padding:10px 12px;text-align:center;color:#0b1b6f;">n</th>
                            <th style="padding:10px 12px;text-align:center;color:#0b1b6f;">Promedio</th>
                            <th style="padding:10px 12px;text-align:center;color:#2e7d32;">% Positivo</th>
                            <th style="padding:10px 12px;text-align:center;color:#c62828;">% Negativo</th>
                        </tr></thead>
                        <tbody>{filas_html}</tbody>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════
# CLIMA Y SATISFACCIÓN
# ══════════════════════════════════════════
st.markdown("## 🏢 Clima y Satisfacción")

for titulo_preg, tipo in PREGUNTAS_ACUERDO_ADMIN:
    col_valor = f"VALOR_{titulo_preg[:30].strip()}".upper()
    render_pregunta_v2(df, titulo_preg, col_valor, ESCALA_ACUERDO)

# ══════════════════════════════════════════
# DESEMPEÑO Y COMPROMISO
# ══════════════════════════════════════════
st.markdown("## 📊 Desempeño y Compromiso")

for titulo_preg, tipo in PREGUNTAS_FRECUENCIA_ADMIN:
    col_valor = f"VALOR_{titulo_preg[:30].strip()}".upper()
    render_pregunta_v2(df, titulo_preg, col_valor, ESCALA_FRECUENCIA)

# ══════════════════════════════════════════
# NPS
# ══════════════════════════════════════════
st.markdown("## ⭐ Satisfacción General")

render_nps(
    df,
    "¿Qué tan probable es que recomiendes a Limtek como un lugar de trabajo a tus amigos o familiares?",
    "¿QUÉ TAN PROBABLE ES QUE RECOMIENDES A LIMTEK COMO UN LUGAR DE TRABAJO A TUS AMIGOS O FAMILIARES?",
)

# ══════════════════════════════════════════
# COMUNICACIÓN Y FORMACIÓN
# ══════════════════════════════════════════
st.markdown("## 📢 Comunicación y Formación")

render_pregunta_multi_separador(
    df,
    "¿Por cuál medio te gustaría recibir las novedades de Limtek?",
    "¿POR CUAL MEDIO TE GUSTARÍA RECIBIR LAS NOVEDADES DE LIMTEK? MARCA MÁXIMO 2 OPCIONES",
    separador="\n",
)

render_pregunta_categorica(
    df,
    "¿Consideras que los talleres del Programa de Formación Transversal han aportado a tu crecimiento profesional?",
    "¿CONSIDERAS QUE LOS TALLERES REALIZADOS EN NUESTRO PROGRAMA DE FORMACIÓN TRANSVERSAL HAN APORTADO A TU CRECIMIENTO PROFESIONAL?POR EJEMPLO: CREATIVIDAD EN MOVIMIENTO, CANVA, TU ALIADO EN PRESENTACIONES, ETC.",
)

render_pregunta_categorica(
    df,
    "De los talleres del Programa de Formación, ¿cuál consideras que te ha aportado más?",
    "DE LOS TALLERES DEL PROGRAMA DE FORMACIÓN EN QUE HAS PARTICIPADO, ¿CUÁL CONSIDERAS QUE TE HA APORTADO MÁS?",
)

render_pregunta_categorica(
    df,
    "¿Qué tipo de capacitación prefieres o consideras mejor para tu aprendizaje?",
    "¿QUÉ TIPO DE CAPACITACIÓN PREFIERES O CONSIDERAS QUE ES MEJOR PARA TU APRENDIZAJE?",
)

# ══════════════════════════════════════════
# BIENESTAR Y ACTIVIDADES
# ══════════════════════════════════════════
st.markdown("## 🎉 Bienestar y Actividades")

render_pregunta_multi_separador(
    df,
    "¿Cuál ha sido la actividad del programa Vive Bien que más te ha gustado?",
    "¿CUÁL HA SIDO LA ACTIVIDAD DEL PROGRAMA VIVE BIEN, QUE MÁS TE HA GUSTADO? MARCA MÁXIMO 3 OPCIONES",
    separador=";",
)

render_pregunta_categorica(
    df,
    "¿Cuál ha sido la actividad que más te ha gustado?",
    "¿CUÁL HA SIDO LA ACTIVIDAD QUE MÁS TE HA GUSTADO?",
)

# ══════════════════════════════════════════
# COMENTARIOS ABIERTOS
# ══════════════════════════════════════════
st.markdown("## 💬 Comentarios Abiertos")

render_pregunta_abierta_v2(
    df,
    "¿Qué destacas de Limtek al considerarlo un buen lugar para trabajar?",
    "¿QUÉ DESTACAS DE LIMTEK AL CONSIDERARLO UN BUEN LUGAR PARA TRABAJAR?",
    categorias=CATEGORIAS_POSITIVAS,
)

render_pregunta_abierta_v2(
    df,
    "¿Qué tendría que mejorar Limtek para que lo consideres un buen lugar para trabajar?",
    "¿QUÉ TENDRÍA QUE MEJORAR LIMTEK PARA QUE LO CONSIDERES UN BUEN LUGAR PARA TRABAJAR?",
    categorias=CATEGORIAS_MEJORA,
)

# ══════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════
st.markdown("---")
st.caption("📊 Dashboard Encuesta Limtek – Personal Administrativo | Área de Gestión Humana")