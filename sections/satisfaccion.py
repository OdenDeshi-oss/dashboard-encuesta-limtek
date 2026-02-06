from core.constants import PREGUNTAS_LIKERT
from components.likert_card import render_pregunta

def render_satisfaccion(df):
    for p in PREGUNTAS_LIKERT:
        render_pregunta(df, p["titulo"], p["col"])
