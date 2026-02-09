import streamlit as st
import base64
from pathlib import Path

# ======================
# CONFIGURACIÓN GENERAL
# ======================
st.set_page_config(
    page_title="Dashboard Encuesta Limtek",
    layout="wide"
)

# ======================
# CARGAR CSS GLOBAL
# ======================
def load_css(path: str):
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/styles.css")

# ======================
# SIDEBAR (LOGO)
# ======================
def render_sidebar_logo(logo_path: str):
    img_bytes = Path(logo_path).read_bytes()
    logo_base64 = base64.b64encode(img_bytes).decode()
    st.sidebar.markdown(
        f"""<div style="display:flex;justify-content:center;margin:16px 0 24px 0;">
        <img src="data:image/png;base64,{logo_base64}" style="width:450px;max-width:100%;opacity:0.95;"></div>""",
        unsafe_allow_html=True
    )

render_sidebar_logo("assets/logo_limtek.png")

# ======================
# SELECTOR DE DASHBOARD
# ======================
dashboard = st.sidebar.radio(
    "📊 Seleccionar Dashboard",
    ["🏭 Personal Operativo", "🏢 Personal Administrativo"],
    index=0,
)

# ============================================================
# DASHBOARD OPERARIOS
# ============================================================
if dashboard == "🏭 Personal Operativo":

    from layout.header import render_header
    from core.loader import cargar_encuesta, cargar_inventario_operativos
    from sections.satisfaccion import render_satisfaccion
    from components.filters import render_filtros
    from components.multi_choice_card import render_pregunta_multiple
    from components.yes_no_card import render_pregunta_si_no
    from components.open_text_card import render_pregunta_abierta
    from components.category_card import render_pregunta_categorica
    from components.likert_card import render_pregunta

    # HEADER
    render_header(
        titulo="Dashboard Encuesta – Personal Operativo",
        subtitulo="#ExpertosapoyandoExpertos"
    )

    # DATA
    df_base = cargar_encuesta()
    df_cliente_unidad, df_general = render_filtros(df_base)

    # KPIs
    total_encuestados = df_general["RESPONDENT_ID"].nunique()
    total_operativos = cargar_inventario_operativos()
    participacion_pct = (total_encuestados / total_operativos) * 100 if total_operativos > 0 else 0

    if participacion_pct < 60:
        participacion_class = "kpi-danger"
    elif participacion_pct < 80:
        participacion_class = "kpi-warning"
    else:
        participacion_class = "kpi-ok"

    # DISTRIBUCIÓN GEOGRÁFICA
    col_departamento = "¿EN QUÉ DEPARTAMENTO TRABAJAS?"
    df_dep = df_cliente_unidad[col_departamento].astype(str).str.upper().str.strip()
    lima_count = (df_dep == "LIMA").sum()
    total_geo = df_dep.shape[0]
    prov_count = total_geo - lima_count
    lima_pct = (lima_count / total_geo) * 100 if total_geo else 0
    prov_pct = (prov_count / total_geo) * 100 if total_geo else 0

    # KPIs SUPERIORES
    colA, colB = st.columns(2, gap="large")

    with colA:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-card-title">Cobertura de la encuesta</div>
            <div class="kpi-row">
            <div class="kpi-item"><div class="kpi-value">{total_encuestados}</div><div class="kpi-label">Encuestados</div></div>
            <div class="kpi-item"><div class="kpi-value {participacion_class}">{participacion_pct:.1f}%</div><div class="kpi-label">Participación</div>
            <div class="kpi-sub">{total_encuestados} / {total_operativos}</div></div>
            </div></div>""",
            unsafe_allow_html=True
        )

    with colB:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-card-title">Distribución geográfica</div>
            <div class="kpi-row">
            <div class="kpi-item"><div class="kpi-value">{lima_pct:.1f}%</div><div class="kpi-label">Lima</div><div class="kpi-sub">{lima_count} personas</div></div>
            <div class="kpi-item"><div class="kpi-value">{prov_pct:.1f}%</div><div class="kpi-label">Provincias</div><div class="kpi-sub">{prov_count} personas</div></div>
            </div></div>""",
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom:32px;'></div>", unsafe_allow_html=True)

    # SATISFACCIÓN (LIKERT)
    render_satisfaccion(df_general)

    # CAPACITACIÓN (MÚLTIPLE)
    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    COLS_CAPACITACION = [
        "SEGURIDAD Y SALUD EN EL TRABAJO",
        "USO DE MAQUINARIAS Y EQUIPOS",
        "USO DE INSUMOS",
        "ATENCIÓN AL CLIENTE",
        "OTRO (ESPECIFIQUE)",
    ]

    render_pregunta_multiple(
        df_general,
        titulo="¿En qué temas te gustaría recibir capacitación?",
        columnas=COLS_CAPACITACION,
    )

    # WHATSAPP
    render_pregunta_si_no(
        df_general,
        titulo="¿Usas WhatsApp en tu vida diaria?",
        col_valor="¿USAS WHATSAPP EN TU VIDA DIARIA?",
    )

    # SATISFACCIÓN GENERAL
    render_pregunta(
        df_general,
        titulo="Considero a Limtek como un buen lugar para trabajar",
        col_valor="VALOR_SATISFACCIÓN",
    )

    # QUÉ DESTACAS
    render_pregunta_abierta(
        df_general,
        titulo="¿Qué destacas de Limtek al considerarlo un buen lugar para trabajar?",
        col_valor="¿QUÉ DESTACAS DE LIMTEK AL CONSIDERARLO UN BUEN LUGAR PARA TRABAJAR?",
    )

    # QUÉ MEJORAR
    render_pregunta_abierta(
        df_general,
        titulo="¿Qué tendría que mejorar Limtek para que lo consideres un buen lugar para trabajar?",
        col_valor="¿QUÉ TENDRÍA QUE MEJORAR LIMTEK PARA QUE LO CONSIDERES UN BUEN LUGAR PARA TRABAJAR?",
    )

    # ANTIGÜEDAD
    ORDEN_ANTIGUEDAD = [
        "De 0 a 6 meses",
        "De 6 meses a 1 año",
        "De 1 a 2 años",
        "De 2 a 3 años",
        "De 3 años a más",
    ]

    render_pregunta_categorica(
        df_general,
        titulo="¿Cuánto tiempo llevas trabajando en Limtek?",
        col_valor="¿CUÁNTO TIEMPO LLEVAS TRABAJANDO EN LIMTEK?",
        orden=ORDEN_ANTIGUEDAD,
    )

    # FOOTER
    st.markdown("---")
    st.caption("📊 Dashboard Encuesta Limtek – Personal Operativo | Área de Gestión Humana")


# ============================================================
# DASHBOARD ADMINISTRATIVOS
# ============================================================
else:

    from layout.header import render_header
    from core.loader import cargar_encuesta_admin
    from core.constants_admin import ESCALA_ACUERDO, ESCALA_FRECUENCIA
    from components.likert_card_admin import render_pregunta_admin
    from components.category_card import render_pregunta_categorica
    from components.multi_sep_card import render_pregunta_multi_separador
    from components.nps_card import render_nps
    from components.open_text_card import render_pregunta_abierta

    # HEADER
    render_header(
        titulo="Dashboard Encuesta – Personal Administrativo",
        subtitulo="#ExpertosapoyandoExpertos"
    )

    # DATA
    df = cargar_encuesta_admin()
    total_encuestados = len(df)

    # KPIs SUPERIORES
    colA, colB = st.columns(2, gap="large")

    with colA:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-card-title">Cobertura de la encuesta</div>
            <div class="kpi-row">
            <div class="kpi-item"><div class="kpi-value">{total_encuestados}</div><div class="kpi-label">Encuestados</div></div>
            <div class="kpi-item"><div class="kpi-value kpi-ok">100%</div><div class="kpi-label">Participación</div>
            <div class="kpi-sub">Personal administrativo</div></div>
            </div></div>""",
            unsafe_allow_html=True
        )

    with colB:
        if "ÁREA" in df.columns:
            areas = df["ÁREA"].nunique()
        else:
            areas = "—"
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-card-title">Distribución</div>
            <div class="kpi-row">
            <div class="kpi-item"><div class="kpi-value">{areas}</div><div class="kpi-label">Áreas participantes</div></div>
            <div class="kpi-item"><div class="kpi-value">{total_encuestados}</div><div class="kpi-label">Colaboradores</div>
            <div class="kpi-sub">Personal administrativo</div></div>
            </div></div>""",
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom:32px;'></div>", unsafe_allow_html=True)

    # CLIMA Y SATISFACCIÓN
    st.markdown("## 🏢 Clima y Satisfacción")

    PREGUNTAS_ACUERDO = [
        ("Me siento a gusto con el ambiente de trabajo que se genera en mi equipo.",
         "VALOR_ME SIENTO A GUSTO CON EL AMBIE"),
        ("En mi entorno de trabajo mantenemos una actitud positiva centrándonos en las soluciones más que en los problemas.",
         "VALOR_EN MI ENTORNO DE TRABAJO MANTE"),
        ("Mi jefe directo fomenta el trabajo en equipo y colaboración entre todos.",
         "VALOR_MI JEFE DIRECTO FOMENTA EL TRA"),
        ("Mi jefe directo se preocupa por mi bienestar personal.",
         "VALOR_MI JEFE DIRECTO SE PREOCUPA PO"),
        ("Me siento motivado a dar lo mejor de mí y hacer un buen trabajo",
         "VALOR_ME SIENTO MOTIVADO A DAR LO ME"),
        ("Mi jefe directo me otorga la confianza para acudir a él ante cualquier problema que afecte mi trabajo.",
         "VALOR_MI JEFE DIRECTO ME OTORGA LA C"),
        ("Mis compañeros están comprometidos a hacer un trabajo de gran calidad.",
         "VALOR_MIS COMPAÑEROS ESTÁN COMPROMET"),
        ("Cuando lo necesito, el resto de áreas de Limtek me brinda el soporte e información que requiero para hacer bien mi trabajo",
         "VALOR_CUANDO LO NECESITO, EL RESTO D"),
        ("Me siento orgulloso de trabajar en Limtek",
         "VALOR_ME SIENTO ORGULLOSO DE TRABAJA"),
        ("Recomendaría los servicios que ofrece Limtek",
         "VALOR_RECOMENDARÍA LOS SERVICIOS QUE"),
        ("Mi trabajo impacta directa o indirectamente en la satisfacción de nuestros clientes.",
         "VALOR_MI TRABAJO IMPACTA DIRECTA O I"),
    ]

    for titulo, col_valor in PREGUNTAS_ACUERDO:
        render_pregunta_admin(df, titulo, col_valor, ESCALA_ACUERDO)

    # DESEMPEÑO
    st.markdown("## 📊 Desempeño y Compromiso")

    PREGUNTAS_FRECUENCIA = [
        ("Busco innovar y nuevas formas de hacer mejor mi trabajo.",
         "VALOR_BUSCO INNOVAR Y NUEVAS FORMAS"),
        ("Dialogo con mi jefe directo sobre la calidad de mi trabajo y cómo podría mejorar.",
         "VALOR_DIALOGO CON MI JEFE DIRECTO SO"),
        ("Siento que mi trabajo es reconocido por mi jefe directo.",
         "VALOR_SIENTO QUE MI TRABAJO ES RECON"),
        ("Mis compañeros de área me dan soporte cuando lo necesito.",
         "VALOR_MIS COMPAÑEROS DE ÁREA ME DAN"),
    ]

    for titulo, col_valor in PREGUNTAS_FRECUENCIA:
        render_pregunta_admin(df, titulo, col_valor, ESCALA_FRECUENCIA)

    # SATISFACCIÓN GENERAL
    st.markdown("## ⭐ Satisfacción General")

    render_pregunta_admin(
        df,
        "Considero a Limtek como un buen lugar para trabajar",
        "VALOR_CONSIDERO A LIMTEK COMO UN BUE",
        ESCALA_ACUERDO,
    )

    # NPS
    render_nps(
        df,
        "¿Qué tan probable es que recomiendes a Limtek como un lugar de trabajo a tus amigos o familiares?",
        "¿QUÉ TAN PROBABLE ES QUE RECOMIENDES A LIMTEK COMO UN LUGAR DE TRABAJO A TUS AMIGOS O FAMILIARES?",
    )

    # COMUNICACIÓN Y FORMACIÓN
    st.markdown("## 📢 Comunicación y Formación")

    render_pregunta_multi_separador(
        df,
        "¿Por cuál medio te gustaría recibir las novedades de Limtek?",
        "¿POR CUAL MEDIO TE GUSTARÍA RECIBIR LAS NOVEDADES DE LIMTEK? MARCA MÁXIMO 2 OPCIONES",
        separador="\n",
    )

    render_pregunta_categorica(
        df,
        "¿Consideras que los talleres del Programa de Formación Transversal han aportado a tu crecimiento profesional?",
        "¿CONSIDERAS QUE LOS TALLERES REALIZADOS EN NUESTRO PROGRAMA DE FORMACIÓN TRANSVERSAL HAN APORTADO A TU CRECIMIENTO PROFESIONAL?POR EJEMPLO: CREATIVIDAD EN MOVIMIENTO, CANVA, TU ALIADO EN PRESENTACIONES, ETC.",
    )

    render_pregunta_categorica(
        df,
        "De los talleres del Programa de Formación, ¿cuál consideras que te ha aportado más?",
        "DE LOS TALLERES DEL PROGRAMA DE FORMACIÓN EN QUE HAS PARTICIPADO, ¿CUÁL CONSIDERAS QUE TE HA APORTADO MÁS?",
    )

    render_pregunta_categorica(
        df,
        "¿Qué tipo de capacitación prefieres o consideras mejor para tu aprendizaje?",
        "¿QUÉ TIPO DE CAPACITACIÓN PREFIERES O CONSIDERAS QUE ES MEJOR PARA TU APRENDIZAJE?",
    )

    # BIENESTAR Y ACTIVIDADES
    st.markdown("## 🎉 Bienestar y Actividades")

    render_pregunta_multi_separador(
        df,
        "¿Cuál ha sido la actividad del programa Vive Bien que más te ha gustado?",
        "¿CUÁL HA SIDO LA ACTIVIDAD DEL PROGRAMA VIVE BIEN, QUE MÁS TE HA GUSTADO? MARCA MÁXIMO 3 OPCIONES",
        separador=";",
    )

    render_pregunta_categorica(
        df,
        "¿Cuál ha sido la actividad que más te ha gustado?",
        "¿CUÁL HA SIDO LA ACTIVIDAD QUE MÁS TE HA GUSTADO?",
    )

    # COMENTARIOS ABIERTOS
    st.markdown("## 💬 Comentarios Abiertos")

    render_pregunta_abierta(
        df,
        "¿Qué destacas de Limtek al considerarlo un buen lugar para trabajar?",
        "¿QUÉ DESTACAS DE LIMTEK AL CONSIDERARLO UN BUEN LUGAR PARA TRABAJAR?",
    )

    render_pregunta_abierta(
        df,
        "¿Qué tendría que mejorar Limtek para que lo consideres un buen lugar para trabajar?",
        "¿QUÉ TENDRÍA QUE MEJORAR LIMTEK PARA QUE LO CONSIDERES UN BUEN LUGAR PARA TRABAJAR?",
    )

    # FOOTER
    st.markdown("---")
    st.caption("📊 Dashboard Encuesta Limtek – Personal Administrativo | Área de Gestión Humana")