import pandas as pd
from core.config import SCALE_MAX, NEUTRAL


def compute_likert_metrics(serie, scale_max=SCALE_MAX, neutral=NEUTRAL, invert=False):
    """
    Calcula métricas Likert sobre una serie numérica 1–5.

    Parámetros
    ----------
    serie : pd.Series con valores numéricos.
    scale_max : int – Valor máximo de la escala (5).
    neutral : int – Valor neutral (3), se calcula pero no se grafica.
    invert : bool – Si True, aplica inversión: x → (scale_max + 1 - x).

    Retorna
    -------
    dict con:
        promedio, nivel_pct, n, conteo, pct_positivo, pct_negativo, pct_neutral
    """

    serie = pd.to_numeric(serie, errors="coerce").dropna()

    if serie.empty:
        return None

    # Filtrar solo valores válidos en rango
    serie = serie[(serie >= 1) & (serie <= scale_max)]

    if serie.empty:
        return None

    # Inversión si aplica
    if invert:
        serie = (scale_max + 1) - serie

    n = len(serie)
    promedio = round(serie.mean(), 2)
    nivel_pct = round((promedio / scale_max) * 100, 2)

    # Conteo por valor (todos los de la escala)
    conteo = serie.value_counts().reindex(range(1, scale_max + 1), fill_value=0)

    # Clasificación
    positivo = int(serie[serie >= 4].count())
    negativo = int(serie[serie <= 2].count())
    neutral_count = int(serie[serie == neutral].count())

    pct_positivo = round(positivo / n * 100, 1)
    pct_negativo = round(negativo / n * 100, 1)
    pct_neutral = round(neutral_count / n * 100, 1)

    return {
        "promedio": promedio,
        "nivel_pct": nivel_pct,
        "n": n,
        "conteo": conteo,
        "positivo": positivo,
        "negativo": negativo,
        "neutral_count": neutral_count,
        "pct_positivo": pct_positivo,
        "pct_negativo": pct_negativo,
        "pct_neutral": pct_neutral,
    }
