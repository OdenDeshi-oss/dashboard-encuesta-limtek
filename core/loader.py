import pandas as pd
import streamlit as st
import os
from core.config import MAPA_ACUERDO_LEGACY, MAPA_FRECUENCIA_LEGACY

# ======================
# RUTAS DE ARCHIVOS
# ======================
ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_ CIERRE 2026.xlsx"
INVENTARIO_PATH = "data/11. INVENTARIO NOVIEMBRE 2025 - ACTUALIZADO (1).xlsx"
ADMIN_PATH = "data/Encuesta Personal administrativo 2025.xlsx"
ADMIN_INVENTARIO_PATH = "data/Lista Encuesta clima laboral Adm 2025.xlsx"


def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.upper()
    return df


# ======================
# CARGA ENCUESTA OPERARIOS
# ======================
def cargar_encuesta():
    if not os.path.exists(ENCUESTA_PATH):
        st.error("❌ No se encontró el archivo de encuesta operarios")
        st.stop()

    df = pd.read_excel(ENCUESTA_PATH, engine="openpyxl")
    df = normalizar_columnas(df)

    # Re-mapear valores numéricos legacy (1-4) a escala 1-5
    valor_cols = [c for c in df.columns if c.startswith("VALOR_")]
    for col in valor_cols:
        serie = pd.to_numeric(df[col], errors="coerce")
        # Si max es 4, es escala legacy → remapear
        if serie.max() <= 4:
            # 1→1, 2→2, 3→4, 4→5 (no hay 3 neutral en datos legacy)
            mapa = {1: 1, 2: 2, 3: 4, 4: 5}
            df[col] = serie.map(mapa)

    return df


# ======================
# CARGA INVENTARIO OPERATIVOS
# ======================
def cargar_inventario_operativos():
    if not os.path.exists(INVENTARIO_PATH):
        st.error("❌ No se encontró el archivo de inventario de personal")
        st.stop()

    df_inv = pd.read_excel(INVENTARIO_PATH, engine="openpyxl")
    df_inv = normalizar_columnas(df_inv)

    cargos_operativos = [
        "OPERARIO",
        "OPERARIO PART TIME",
        "OPERARIO INTERMITENTE",
        "OPERARIO POLIVALENTE",
    ]
    df_inv["CARGO"] = df_inv["CARGO"].astype(str).str.strip().str.upper()
    total_operativos = df_inv[df_inv["CARGO"].isin(cargos_operativos)].shape[0]
    return total_operativos


# ======================
# CARGA ENCUESTA ADMINISTRATIVOS
# ======================
def cargar_encuesta_admin():
    if not os.path.exists(ADMIN_PATH):
        st.error("❌ No se encontró el archivo de encuesta administrativos")
        st.stop()

    df = pd.read_excel(ADMIN_PATH, engine="openpyxl")

    # Columnas Likert escala ACUERDO
    cols_acuerdo = [
        "Me siento a gusto con el ambiente de trabajo que se genera en mi equipo.",
        "En mi entorno de trabajo mantenemos una actitud positiva centrándonos en las soluciones más que en los problemas.",
        "Mi jefe directo fomenta el trabajo en equipo y colaboración entre todos.",
        "Mi jefe directo se preocupa por mi bienestar personal.",
        "Me siento motivado a dar lo mejor de mí y hacer un buen trabajo",
        "Mi jefe directo me otorga la confianza para acudir a él ante cualquier problema que afecte mi trabajo.",
        "Mis compañeros están comprometidos a hacer un trabajo de gran calidad.",
        "Cuando lo necesito, el resto de áreas de Limtek me brinda el soporte e información que requiero para hacer bien mi trabajo",
        "Me siento orgulloso de trabajar en Limtek",
        "Recomendaría los servicios que ofrece Limtek",
        "Mi trabajo impacta directa o indirectamente en la satisfacción de nuestros clientes.",
        "Considero a Limtek como un buen lugar para trabajar",
    ]

    # Columnas Likert escala FRECUENCIA
    cols_frecuencia = [
        "Busco innovar y nuevas formas de hacer mejor mi trabajo.",
        "Dialogo con mi jefe directo sobre la calidad de mi trabajo y cómo podría mejorar.",
        "Siento que mi trabajo es reconocido por mi jefe directo.",
        "Mis compañeros de área me dan soporte cuando lo necesito.",
    ]

    for col in cols_acuerdo:
        if col in df.columns:
            valor_col = f"VALOR_{col[:30].strip()}"
            df[valor_col] = df[col].map(MAPA_ACUERDO_LEGACY)

    for col in cols_frecuencia:
        if col in df.columns:
            valor_col = f"VALOR_{col[:30].strip()}"
            df[valor_col] = df[col].map(MAPA_FRECUENCIA_LEGACY)

    df = normalizar_columnas(df)
    return df


# ======================
# CARGA INVENTARIO ADMINISTRATIVOS
# ======================
def cargar_inventario_admin():
    if not os.path.exists(ADMIN_INVENTARIO_PATH):
        return 0

    df_inv = pd.read_excel(ADMIN_INVENTARIO_PATH, engine="openpyxl")
    df_inv = normalizar_columnas(df_inv)
    return len(df_inv)
