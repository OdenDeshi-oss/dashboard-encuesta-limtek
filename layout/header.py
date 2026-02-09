import streamlit as st


def render_header(
    titulo: str = "Dashboard Encuesta – Personal Operativo",
    subtitulo: str = "#ExpertosapoyandoExpertos",
):
    """
    Header superior del dashboard.
    El diseño se controla desde styles.css
    """

    st.markdown(
        f"""
        <div class="limtek-header">
            <div class="limtek-title">{titulo}</div>
            <div class="limtek-subtitle">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
