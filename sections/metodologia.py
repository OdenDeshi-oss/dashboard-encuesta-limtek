import streamlit as st


def render_metodologia():
    """
    Sección de metodología: breve, institucional, enfocada a interpretación.
    """

    with st.container():
        st.markdown(
            """
            <div class="card-header">
                <b>📐 Nota Metodológica</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="metodologia-box">
                <table class="metodologia-tabla">
                    <tr>
                        <td class="met-label">Escala de medición</td>
                        <td>Likert de 5 puntos: 1 (Totalmente en desacuerdo) a 5 (Totalmente de acuerdo)</td>
                    </tr>
                    <tr>
                        <td class="met-label">Punto medio</td>
                        <td>El valor 3 ("Ni de acuerdo ni en desacuerdo") se incluye en todos los cálculos estadísticos. No se visualiza en gráficos de distribución para priorizar la lectura de posiciones definidas.</td>
                    </tr>
                    <tr>
                        <td class="met-label">Promedio</td>
                        <td>Promedio simple: suma de respuestas válidas / total de respuestas válidas (n). No se aplica ponderación, priorizando transparencia y replicabilidad.</td>
                    </tr>
                    <tr>
                        <td class="met-label">Clasificación</td>
                        <td><b>Positivo (4–5)</b> · Neutral (3) · <b>Negativo (1–2)</b></td>
                    </tr>
                    <tr>
                        <td class="met-label">Nivel alcanzado</td>
                        <td>Promedio / 5 × 100. Indicador porcentual del nivel de favorabilidad.</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
