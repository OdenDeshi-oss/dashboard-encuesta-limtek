import streamlit as st
from core.constants import PREGUNTAS_LIKERT
from components.likert_card import render_pregunta


def render_satisfaccion(df):
    """
    Renderiza la sección de satisfacción.
    Cada pregunta Likert se muestra como un card independiente.
    El diseño se controla únicamente desde styles.css
    """

    for p in PREGUNTAS_LIKERT:
        render_pregunta(
            df=df,
            titulo=p["titulo"],
            col_valor=p["col"]
        )
