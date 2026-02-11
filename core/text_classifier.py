import re
import unicodedata
import pandas as pd


def _normalizar(texto):
    """Lowercase, quitar tildes y símbolos."""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return texto


def classify_open_ended(serie, categorias):
    """
    Clasifica cada respuesta en UNA categoría según palabras clave.

    Parámetros
    ----------
    serie : pd.Series con textos.
    categorias : dict – {nombre_categoria: [lista_de_palabras_clave]}.

    Retorna
    -------
    pd.DataFrame con columnas: Respuesta, Categoria
    """

    resultados = []

    for texto_original in serie:
        texto = _normalizar(texto_original)
        palabras = set(texto.split())

        mejor_cat = "Otros"
        mejor_score = 0

        for cat, keywords in categorias.items():
            if cat == "Otros":
                continue

            # Contar coincidencias
            score = 0
            for kw in keywords:
                kw_norm = _normalizar(kw)
                if " " in kw_norm:
                    # Frase completa
                    if kw_norm in texto:
                        score += 2
                else:
                    # Palabra suelta
                    if kw_norm in palabras:
                        score += 1

            if score > mejor_score:
                mejor_score = score
                mejor_cat = cat

        # Regla especial: "todo está bien" / "nada"
        if mejor_cat == "Todo está bien" or (mejor_score == 0 and texto.strip() in ("nada", "todo", "si", "no", ".", "-", "ninguno")):
            mejor_cat = "Todo está bien"
            if mejor_score == 0:
                mejor_score = 1

        if mejor_score == 0:
            mejor_cat = "Otros"

        resultados.append({
            "Respuesta": str(texto_original).strip(),
            "Categoria": mejor_cat,
        })

    return pd.DataFrame(resultados)
