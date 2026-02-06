import pandas as pd
import streamlit as st
import os

ENCUESTA_PATH = "data/ENCUESTA OPERARIOS_ CIERRE 2026.xlsx"

def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.upper()
    return df

def cargar_encuesta():
    if not os.path.exists(ENCUESTA_PATH):
        st.error("❌ No se encontró el archivo de encuesta")
        st.stop()

    df = pd.read_excel(ENCUESTA_PATH, engine="openpyxl")
    df = normalizar_columnas(df)

    return df
