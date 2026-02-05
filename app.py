import os
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Dashboard Encuesta Limtek", layout="wide")

ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_ CIERRE 2026.xlsx"
INVENTARIO_PATH = "data/11. INVENTARIO NOVIEMBRE 2025 - ACTUALIZADO (1).xlsx"

# Preguntas múltiples (tal cual en tu Excel)
PREGUNTAS_MULTIPLES = [
    "Seguridad y Salud en el Trabajo",
    "Uso de maquinarias y equipos",
    "Uso de insumos",
    "Atención al cliente",
    "Otro (especifique)",
]

COL_CLIENTE = "¿En qué cliente estás destacado?"
COL_UNIDAD = "¿En qué unidad estás destacado?"

CARGO_OPERATIVO = ["OPERARIO", "OPERARIO PART TIME"]

# =========================================================
# HELPERS
# =========================================================
def separador():
    st.markdown("---")


def normalizar_columnas_inventario(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df


@st.cache_data(show_spinner=False)
def cargar_encuesta(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    df = pd.read_excel(path, engine="openpyxl")
    # Limpieza leve sin romper nombres con tildes
    df.columns = df.columns.astype(str).str.strip()
    return df


@st.cache_data(show_spinner=False)
def cargar_inventario(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    df = pd.read_excel(path, engine="openpyxl")
    # Convertimos a string columnas object para evitar rarezas
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)
    df = normalizar_columnas_inventario(df)
    return df


def detectar_pares_likert(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    En tu Excel cada pregunta Likert viene como:
    - Columna de texto con la pregunta (respuestas tipo "Totalmente de acuerdo", etc.)
    - Columna numérica que comienza con "Valor_"
    Tomamos el texto como la columna anterior a Valor_*.
    """
    cols = list(df.columns)
    pares = []
    for i, c in enumerate(cols):
        if isinstance(c, str) and c.startswith("Valor_") and i > 0:
            col_valor = c
            col_texto = cols[i - 1]
            pares.append({"texto": col_texto, "valor": col_valor})
    return pares


def labels_por_valor(df: pd.DataFrame, col_texto: str, col_valor: str) -> Dict[int, str]:
    """
    Mapea 1..4 -> etiqueta real (según el texto observado en tu Excel),
    evitando suposiciones como "Nunca" vs "Totalmente en desacuerdo".
    """
    tmp = df[[col_texto, col_valor]].dropna()
    if tmp.empty:
        return {1: "1", 2: "2", 3: "3", 4: "4"}

    tmp[col_valor] = pd.to_numeric(tmp[col_valor], errors="coerce")
    tmp = tmp.dropna(subset=[col_valor])
    tmp[col_valor] = tmp[col_valor].astype(int)

    mapping = {}
    for v in [1, 2, 3, 4]:
        s = tmp[tmp[col_valor] == v][col_texto].astype(str).str.strip()
        if s.empty:
            mapping[v] = str(v)
        else:
            mapping[v] = s.value_counts().index[0]
    return mapping


def resumen_likert(df: pd.DataFrame, col_valor: str) -> Tuple[pd.DataFrame, float, float]:
    """
    Devuelve:
    - df_res: columnas [VALOR, CANTIDAD, PORCENTAJE]
    - promedio
    - nivel_alcanzado (%): promedio/4*100
    """
    s = pd.to_numeric(df[col_valor], errors="coerce").dropna()
    if s.empty:
        df_res = pd.DataFrame({"VALOR": [1, 2, 3, 4], "CANTIDAD": [0, 0, 0, 0], "PORCENTAJE": [0, 0, 0, 0]})
        return df_res, 0.0, 0.0

    counts = s.value_counts().reindex([1, 2, 3, 4], fill_value=0).astype(int)
    total = int(counts.sum())
    porcentajes = (counts / total * 100).round(2)

    df_res = pd.DataFrame({
        "VALOR": [1, 2, 3, 4],
        "CANTIDAD": counts.values,
        "PORCENTAJE": porcentajes.values,
    })

    promedio = float(s.mean())
    nivel = round((promedio / 4) * 100, 2)
    return df_res, round(promedio, 2), nivel


def esta_marcada(valor) -> bool:
    """Detector robusto para checks/múltiple selección."""
    if pd.isna(valor):
        return False
    v = str(valor).strip().upper()
    if v in ["", "NAN", "0", "NO", "NONE", "FALSE"]:
        return False
    if v in ["SÍ", "SI", "X", "1", "TRUE"]:
        return True
    # cualquier otro texto => marcado
    return len(v) > 0


def css_cards():
    st.markdown(
        """
        <style>
          .dash-wrap { background: #0e1117; }
          .kpi-card {
            background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
            border-radius: 14px;
            padding: 18px 18px;
            color: white;
            box-shadow: 0 6px 16px rgba(0,0,0,.25);
            height: 120px;
          }
          .kpi-title { font-size: 14px; opacity: .95; margin-bottom: 6px; }
          .kpi-value { font-size: 46px; font-weight: 800; line-height: 1.0; }
          .kpi-sub { margin-top: 8px; font-size: 16px; opacity: .95; }
          .q-card {
            background: #1b2230;
            border: 1px solid rgba(255,255,255,.06);
            border-radius: 14px;
            padding: 14px 14px;
            box-shadow: 0 6px 16px rgba(0,0,0,.18);
          }
          .q-title {
            color: white;
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 10px;
          }
          .q-left {
            background: #0f172a;
            border-radius: 12px;
            padding: 14px;
            border: 1px solid rgba(255,255,255,.06);
          }
          .q-num { color: white; font-size: 44px; font-weight: 800; line-height: 1.0; }
          .q-sub { color: #cbd5e1; font-size: 14px; margin-top: 10px; }
          .q-pct { color: #e2e8f0; font-size: 22px; font-weight: 800; margin-top: 2px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(title: str, value_big: str, sub: str):
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value_big}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LOAD DATA
# =========================================================
css_cards()
st.title("Dashboard Encuesta – Personal Operativo")

try:
    df_encuesta = cargar_encuesta(ENCUESTA_PATH)
except Exception as e:
    st.error(f"❌ Error cargando encuesta: {e}")
    st.stop()

try:
    df_inv = cargar_inventario(INVENTARIO_PATH)
except Exception as e:
    st.error(f"❌ Error cargando inventario: {e}")
    st.stop()

# Validación mínima
for c in [COL_CLIENTE, COL_UNIDAD]:
    if c not in df_encuesta.columns:
        st.error(f"❌ No se encontró la columna en encuesta: {c}")
        st.write("Columnas disponibles:", list(df_encuesta.columns))
        st.stop()

for c in ["CARGO", "CLIENTE", "UNIDAD"]:
    if c not in df_inv.columns:
        st.error(f"❌ No se encontró la columna en inventario: {c}")
        st.write("Columnas disponibles:", list(df_inv.columns))
        st.stop()

# =========================================================
# SIDEBAR FILTERS (cliente/unidad)
# =========================================================
st.sidebar.header("🎯 Filtros")

clientes = sorted(df_encuesta[COL_CLIENTE].dropna().astype(str).str.strip().unique())
cliente_sel = st.sidebar.selectbox("Cliente", ["Todos"] + clientes)

df_enc_fil = df_encuesta.copy()
if cliente_sel != "Todos":
    df_enc_fil = df_enc_fil[df_enc_fil[COL_CLIENTE].astype(str).str.strip() == cliente_sel]

unidades = sorted(df_enc_fil[COL_UNIDAD].dropna().astype(str).str.strip().unique())
unidad_sel = st.sidebar.selectbox("Unidad", ["Todas"] + unidades)

if unidad_sel != "Todas":
    df_enc_fil = df_enc_fil[df_enc_fil[COL_UNIDAD].astype(str).str.strip() == unidad_sel]

debug = st.sidebar.checkbox("🔧 Modo debug (mostrar tablas)", value=False)

# =========================================================
# INVENTARIO: SOLO PARA MÉTRICA DE COBERTURA (NO GRÁFICOS)
# =========================================================
df_inv_oper = df_inv[df_inv["CARGO"].fillna("").str.strip().isin(CARGO_OPERATIVO)].copy()

if cliente_sel != "Todos":
    df_inv_oper = df_inv_oper[df_inv_oper["CLIENTE"].astype(str).str.strip() == cliente_sel]
if unidad_sel != "Todas":
    df_inv_oper = df_inv_oper[df_inv_oper["UNIDAD"].astype(str).str.strip() == unidad_sel]

total_operarios = int(len(df_inv_oper))
total_encuestados = int(len(df_enc_fil))
participacion = round((total_encuestados / total_operarios) * 100, 2) if total_operarios > 0 else 0.0

# =========================================================
# TOP KPIS (tipo Excel)
# - Prom Satisfacción (Valor_Satisfacción)
# - Nivel alcanzado (Satisfacción)
# - Participación (Encuesta/Inventario)
# =========================================================
pares_likert = detectar_pares_likert(df_encuesta)
val_cols = [p["valor"] for p in pares_likert]
if "Valor_Satisfacción" in val_cols:
    col_satisf_val = "Valor_Satisfacción"
else:
    # fallback: primera Valor_* si por algo cambia (pero en tu Excel existe)
    col_satisf_val = val_cols[0] if val_cols else None

prom_sat = 0.0
nivel_sat = 0.0
if col_satisf_val:
    _, prom_sat, nivel_sat = resumen_likert(df_enc_fil, col_satisf_val)

c1, c2, c3 = st.columns(3)
with c1:
    render_kpi("Prom Satisfacción", f"{prom_sat:.2f}", f"Nivel alcanzado: {nivel_sat:.2f}%")
with c2:
    render_kpi("Encuestados", f"{total_encuestados:,}", f"Operarios (inventario): {total_operarios:,}")
with c3:
    render_kpi("Participación", f"{participacion:.2f}%", "Encuesta vs inventario (filtros aplicados)")

separador()

# =========================================================
# BLOQUES POR PREGUNTA LIKERT (TODAS)
# =========================================================
st.subheader("Detalle por pregunta (escala 1–4)")

for p in pares_likert:
    col_texto = p["texto"]
    col_valor = p["valor"]

    # Saltar si no existe (por seguridad)
    if col_valor not in df_enc_fil.columns or col_texto not in df_enc_fil.columns:
        continue

    # Resumen
    df_res, prom, nivel = resumen_likert(df_enc_fil, col_valor)
    mapping = labels_por_valor(df_enc_fil, col_texto, col_valor)

    # Construir labels ordenados por valor
    df_plot = df_res.copy()
    df_plot["ETIQUETA"] = df_plot["VALOR"].map(mapping)
    df_plot["LABEL"] = df_plot.apply(lambda r: f"{int(r['CANTIDAD'])} ({r['PORCENTAJE']:.2f}%)", axis=1)

    # Card layout
    st.markdown('<div class="q-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="q-title">{col_texto}</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 3], vertical_alignment="top")

    with left:
        st.markdown(
            f"""
            <div class="q-left">
              <div class="q-num">{prom:.2f}</div>
              <div class="q-sub">Nivel alcanzado:</div>
              <div class="q-pct">{nivel:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        # Plotly (sin gráficos por cliente/unidad)
        fig = px.bar(
            df_plot,
            x="ETIQUETA",
            y="CANTIDAD",
            text="LABEL",
            title=None,
            labels={"ETIQUETA": "", "CANTIDAD": "Cantidad"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            uniformtext_minsize=10,
            uniformtext_mode="hide",
            xaxis_tickangle=0,
        )
        st.plotly_chart(fig, use_container_width=True)

        if debug:
            st.dataframe(df_plot[["VALOR", "ETIQUETA", "CANTIDAD", "PORCENTAJE"]], use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

separador()

# =========================================================
# PREGUNTAS MÚLTIPLES (CAPACITACIÓN)
# =========================================================
st.subheader("📋 Necesidades de capacitación (selección múltiple)")

# Verificar columnas existentes (sin normalizar por mayúsculas para no romper tildes)
preguntas_encontradas = [c for c in PREGUNTAS_MULTIPLES if c in df_enc_fil.columns]
preguntas_faltantes = [c for c in PREGUNTAS_MULTIPLES if c not in df_enc_fil.columns]

if preguntas_faltantes and debug:
    st.warning(f"Columnas no encontradas (múltiple): {preguntas_faltantes}")

if total_encuestados == 0:
    st.warning("⚠️ No hay encuestas para analizar con los filtros seleccionados.")
else:
    resultados = []
    for pregunta in preguntas_encontradas:
        marcados = int(df_enc_fil[pregunta].apply(esta_marcada).sum())
        pct = round((marcados / total_encuestados) * 100, 2) if total_encuestados > 0 else 0.0
        resultados.append({"ÁREA": pregunta, "CANTIDAD": marcados, "PORCENTAJE": pct})

    df_multi = pd.DataFrame(resultados).sort_values("CANTIDAD", ascending=False)
    df_multi["LABEL"] = df_multi.apply(lambda r: f"{int(r['CANTIDAD'])} ({r['PORCENTAJE']:.2f}%)", axis=1)

    fig_multi = px.bar(
        df_multi,
        x="ÁREA",
        y="CANTIDAD",
        text="LABEL",
        labels={"ÁREA": "", "CANTIDAD": "Cantidad"},
        title=None,
    )
    fig_multi.update_traces(textposition="outside")
    fig_multi.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        xaxis_tickangle=-35,
    )
    st.plotly_chart(fig_multi, use_container_width=True)

    # Tabla (esta sí puede quedar, es corta)
    st.dataframe(df_multi[["ÁREA", "CANTIDAD", "PORCENTAJE"]], use_container_width=True)

separador()
st.caption("📊 Dashboard Encuesta Limtek - Personal Operativo | Streamlit")
