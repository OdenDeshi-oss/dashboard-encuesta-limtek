import streamlit as st
import pandas as pd


def render_filtros(df_base: pd.DataFrame):
    """
    Filtros bidireccionales:
    - Cliente
    - Departamento
    - Unidad

    Todos limitan a los demás según selección.
    Retorna:
    - df_cliente_unidad : Cliente + Unidad (sin efecto de Departamento)
    - df_general        : Cliente + Unidad + Departamento
    """

    col_cliente = "¿EN QUÉ CLIENTE ESTÁS DESTACADO?"
    col_unidad = "¿EN QUÉ UNIDAD ESTÁS DESTACADO?"
    col_departamento = "¿EN QUÉ DEPARTAMENTO TRABAJAS?"

    st.sidebar.markdown("### 🎯 Segmentadores")

    # ======================
    # ESTADO ACTUAL
    # ======================
    cliente_sel = st.session_state.get("filtro_cliente", "Todos")
    depto_sel = st.session_state.get("filtro_departamento", "Todos")
    unidad_sel = st.session_state.get("filtro_unidad", "Todas")

    # ======================
    # DATAFRAME CONTEXTO
    # ======================
    df_ctx = df_base.copy()

    if cliente_sel != "Todos":
        df_ctx = df_ctx[df_ctx[col_cliente] == cliente_sel]

    if depto_sel != "Todos":
        df_ctx = df_ctx[df_ctx[col_departamento] == depto_sel]

    # ======================
    # CLIENTE (opciones dinámicas)
    # ======================
    clientes = (
        df_ctx[col_cliente]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    cliente_sel = st.sidebar.selectbox(
        "¿En qué cliente estás destacado?",
        options=["Todos"] + clientes,
        key="filtro_cliente"
    )

    # ======================
    # DEPARTAMENTO (opciones dinámicas)
    # ======================
    df_ctx_dep = df_base.copy()
    if cliente_sel != "Todos":
        df_ctx_dep = df_ctx_dep[df_ctx_dep[col_cliente] == cliente_sel]

    departamentos = (
        df_ctx_dep[col_departamento]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    depto_sel = st.sidebar.selectbox(
        "¿En qué departamento trabajas?",
        options=["Todos"] + departamentos,
        key="filtro_departamento"
    )

    # ======================
    # UNIDAD (opciones dinámicas)
    # ======================
    df_ctx_uni = df_base.copy()

    if cliente_sel != "Todos":
        df_ctx_uni = df_ctx_uni[df_ctx_uni[col_cliente] == cliente_sel]

    if depto_sel != "Todos":
        df_ctx_uni = df_ctx_uni[df_ctx_uni[col_departamento] == depto_sel]

    unidades = (
        df_ctx_uni[col_unidad]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    unidad_sel = st.sidebar.selectbox(
        "¿En qué unidad estás destacado?",
        options=["Todas"] + unidades,
        key="filtro_unidad"
    )

    # ======================
    # DF GENERAL
    # ======================
    df_general = df_base.copy()

    if cliente_sel != "Todos":
        df_general = df_general[df_general[col_cliente] == cliente_sel]

    if depto_sel != "Todos":
        df_general = df_general[df_general[col_departamento] == depto_sel]

    if unidad_sel != "Todas":
        df_general = df_general[df_general[col_unidad] == unidad_sel]

    # ======================
    # DF PARA GEOGRAFÍA
    # (sin departamento)
    # ======================
    df_cliente_unidad = df_base.copy()

    if cliente_sel != "Todos":
        df_cliente_unidad = df_cliente_unidad[df_cliente_unidad[col_cliente] == cliente_sel]

    if unidad_sel != "Todas":
        df_cliente_unidad = df_cliente_unidad[df_cliente_unidad[col_unidad] == unidad_sel]

    return df_cliente_unidad, df_general
