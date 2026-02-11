import streamlit as st
from core.config import PREGUNTAS_LIKERT_OPERARIOS, ESCALA_ACUERDO
from components.likert_card_v2 import render_pregunta_v2


def render_satisfaccion(df):
    """
    Renderiza la sección de satisfacción (operarios).
    Cada pregunta Likert se muestra con escala 1–5, sin neutral en gráfico.
    """

    for p in PREGUNTAS_LIKERT_OPERARIOS:
        render_pregunta_v2(
            df=df,
            titulo=p["titulo"],
            col_valor=p["col"],
            escala=ESCALA_ACUERDO,
        )
