# ============================================================
# CONFIGURACIÓN CENTRAL DEL DASHBOARD
# ============================================================

# ── ESCALA LIKERT 1–5 ──
ESCALA_ACUERDO = {
    1: "Totalmente en desacuerdo",
    2: "Parcialmente en desacuerdo",
    3: "Ni de acuerdo ni en desacuerdo",
    4: "Parcialmente de acuerdo",
    5: "Totalmente de acuerdo",
}

ESCALA_FRECUENCIA = {
    1: "Nunca",
    2: "Casi nunca",
    3: "A veces",
    4: "Casi siempre",
    5: "Siempre",
}

# Valor neutral (se calcula pero NO se grafica)
NEUTRAL = 3
SCALE_MAX = 5

# Clasificación
# Positivo / Cumple: 4–5
# Neutral: 3
# Negativo / No cumple: 1–2

# ── MAPEO TEXTO → VALOR NUMÉRICO ──
MAPA_ACUERDO = {
    "Totalmente en desacuerdo": 1,
    "Parcialmente en desacuerdo": 2,
    "Ni de acuerdo ni en desacuerdo": 3,
    "Parcialmente de acuerdo": 4,
    "Totalmente de acuerdo": 5,
}

# Mapeo legacy 1-4 → 1-5 (para datos existentes sin valor 3)
MAPA_ACUERDO_LEGACY = {
    "Totalmente en desacuerdo": 1,
    "Parcialmente en desacuerdo": 2,
    "Parcialmente de acuerdo": 4,
    "Totalmente de acuerdo": 5,
}

MAPA_FRECUENCIA = {
    "Nunca": 1,
    "Casi nunca": 2,
    "A veces": 3,
    "Casi siempre": 4,
    "Siempre": 5,
}

MAPA_FRECUENCIA_LEGACY = {
    "Nunca": 1,
    "Casi nunca": 2,
    "Casi siempre": 4,
    "Siempre": 5,
}

# ── PREGUNTAS CON ESCALA INVERTIDA (admin) ──
# Si una pregunta está en esta lista, se aplica: x → (SCALE_MAX + 1 - x)
PREGUNTAS_INVERTIDAS = []  # Vacío por ahora, configurable

# ── PREGUNTAS LIKERT OPERARIOS ──
PREGUNTAS_LIKERT_OPERARIOS = [
    {
        "titulo": "Me siento a gusto con el ambiente de trabajo que se genera en mi equipo",
        "col": "VALOR_AMBIENTE_TRABAJO",
    },
    {
        "titulo": "Me siento motivado a dar lo mejor de mí y hacer un buen trabajo",
        "col": "VALOR_MOTIVACIÓN",
    },
    {
        "titulo": "Mi supervisor o jefe directo me otorga el soporte que necesito para afrontar cualquier problema que afecte mi trabajo",
        "col": "VALOR_SOPORTE_JEFE",
    },
    {
        "titulo": "Mi supervisor o jefe directo fomenta que nos apoyemos entre todos en el equipo",
        "col": "VALOR_TRABAJO_EQUIPO",
    },
    {
        "titulo": "Siento que mi trabajo es reconocido por mi supervisor o jefe directo",
        "col": "VALOR_RECONOCIMIENTO",
    },
    {
        "titulo": "Mi supervisor o jefe directo nos brinda charlas de 5 minutos y comunica las novedades relevantes a mi puesto de trabajo",
        "col": "VALOR_COMUNICACIÓN_JEFE",
    },
]

# ── PREGUNTAS LIKERT ADMINISTRATIVOS ──
PREGUNTAS_ACUERDO_ADMIN = [
    ("Me siento a gusto con el ambiente de trabajo que se genera en mi equipo.", "acuerdo"),
    ("En mi entorno de trabajo mantenemos una actitud positiva centrándonos en las soluciones más que en los problemas.", "acuerdo"),
    ("Mi jefe directo fomenta el trabajo en equipo y colaboración entre todos.", "acuerdo"),
    ("Mi jefe directo se preocupa por mi bienestar personal.", "acuerdo"),
    ("Me siento motivado a dar lo mejor de mí y hacer un buen trabajo", "acuerdo"),
    ("Mi jefe directo me otorga la confianza para acudir a él ante cualquier problema que afecte mi trabajo.", "acuerdo"),
    ("Mis compañeros están comprometidos a hacer un trabajo de gran calidad.", "acuerdo"),
    ("Cuando lo necesito, el resto de áreas de Limtek me brinda el soporte e información que requiero para hacer bien mi trabajo", "acuerdo"),
    ("Me siento orgulloso de trabajar en Limtek", "acuerdo"),
    ("Recomendaría los servicios que ofrece Limtek", "acuerdo"),
    ("Mi trabajo impacta directa o indirectamente en la satisfacción de nuestros clientes.", "acuerdo"),
    ("Considero a Limtek como un buen lugar para trabajar", "acuerdo"),
]

PREGUNTAS_FRECUENCIA_ADMIN = [
    ("Busco innovar y nuevas formas de hacer mejor mi trabajo.", "frecuencia"),
    ("Dialogo con mi jefe directo sobre la calidad de mi trabajo y cómo podría mejorar.", "frecuencia"),
    ("Siento que mi trabajo es reconocido por mi jefe directo.", "frecuencia"),
    ("Mis compañeros de área me dan soporte cuando lo necesito.", "frecuencia"),
]

# ── CATEGORÍAS PARA RESPUESTAS ABIERTAS ──
CATEGORIAS_POSITIVAS = {
    "Pagos y puntualidad": [
        "pago", "pagos", "puntual", "puntuales", "puntualidad",
        "sueldo", "salario", "remuneracion", "remunera", "mensual",
    ],
    "Clima laboral": [
        "ambiente", "clima", "laboral", "compañerismo", "equipo",
        "compañeros", "armonia", "convivencia", "familia", "union",
    ],
    "Liderazgo y trato": [
        "trato", "jefe", "supervisor", "lider", "apoyo",
        "confianza", "respeto", "comprension", "soporte",
    ],
    "Beneficios y capacitación": [
        "beneficio", "beneficios", "capacitacion", "capacitaciones",
        "formacion", "crecimiento", "oportunidad", "talleres",
    ],
    "Seguridad y condiciones": [
        "seguridad", "epp", "condiciones", "implementos",
        "equipos", "proteccion", "salud",
    ],
    "Estabilidad y organización": [
        "estabilidad", "estable", "organizacion", "orden",
        "responsable", "formal", "serio", "empresa",
    ],
    "Otros": [],
}

CATEGORIAS_MEJORA = {
    "Remuneraciones y beneficios": [
        "sueldo", "salario", "pago", "pagos", "aumento",
        "bono", "beneficio", "beneficios", "incentivo", "canasta",
    ],
    "Comunicación": [
        "comunicacion", "informacion", "charla", "charlas",
        "aviso", "comunicar", "dialogo",
    ],
    "Materiales y equipos": [
        "materiales", "material", "equipos", "herramientas",
        "insumos", "implementos",
    ],
    "Capacitación y formación": [
        "capacitacion", "capacitaciones", "formacion",
        "talleres", "cursos", "entrenar",
    ],
    "Liderazgo y supervisión": [
        "jefe", "supervisor", "lider", "trato", "supervision",
        "coordinacion", "coordinador",
    ],
    "Carga laboral y horarios": [
        "horario", "horarios", "descanso", "turno", "turnos",
        "horas", "carga", "sobrecarga", "vacaciones",
    ],
    "Todo está bien": [
        "nada", "ninguno", "conforme", "todo bien",
    ],
    "Otros": [],
}
