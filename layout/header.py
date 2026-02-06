import streamlit as st
import base64
from pathlib import Path


def _img_to_base64(img_path: str) -> str:
    """Convierte una imagen a base64 para incrustarla en HTML"""
    img_bytes = Path(img_path).read_bytes()
    return base64.b64encode(img_bytes).decode()


def render_header(
    logo_path: str = "assets/logo_limtek.png",
    titulo: str = "Dashboard Encuesta – Personal Operativo",
    subtitulo: str = "#ExpertosapoyandoExpertos",
):
    """
    Header corporativo Limtek
    - Logo a la izquierda
    - Título y slogan
    - Colores institucionales
    """

    logo_base64 = _img_to_base64(logo_path)

    st.markdown(
        f"""
        <style>
        .limtek-header {{
            background: linear-gradient(90deg, #0b1b6f 0%, #122a8c 100%);
            padding: 16px 24px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .limtek-header-content {{
            display: flex;
            align-items: center;
        }}
        .limtek-logo {{
            height: 60px;
            margin-right: 20px;
        }}
        .limtek-title {{
            color: #ffffff;
            font-size: 26px;
            font-weight: 700;
            line-height: 1.2;
        }}
        .limtek-subtitle {{
            color: #f5c542;
            font-size: 14px;
            font-weight: 500;
            margin-top: 4px;
        }}
        </style>

        <div class="limtek-header">
            <div class="limtek-header-content">
                <img src="data:image/png;base64,{logo_base64}" class="limtek-logo"/>
                <div>
                    <div class="limtek-title">{titulo}</div>
                    <div class="limtek-subtitle">{subtitulo}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
