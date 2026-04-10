import streamlit as st

from dashboard.components import (
    render_cabecalho,
    render_dados_filtrados,
    render_graficos,
    render_kpis,
    render_relacionamento_dinamico,
)
from dashboard.config import CSS_PERSONALIZADO, DATA_DIR, obter_colunas
from dashboard.data import carregar_dados
from dashboard.filters import aplicar_filtros, construir_filtros


def configurar_pagina() -> None:
    """Define configuração inicial e estilo visual da aplicação."""
    st.set_page_config(
        page_title="Dashboard F1: Insights de Corrida",
        page_icon=":bar_chart:",
        layout="wide",
    )
    st.markdown(CSS_PERSONALIZADO, unsafe_allow_html=True)


def main() -> None:
    """Executa o fluxo principal da aplicação Streamlit."""
    configurar_pagina()
    render_cabecalho()

    try:
        df = carregar_dados(DATA_DIR)
    except FileNotFoundError:
        st.error(f"Pasta de dados F1 não encontrada ou incompleta em `{DATA_DIR}`.")
        st.stop()

    col = obter_colunas()
    filtros = construir_filtros(df, col)
    df_filtrado = aplicar_filtros(df, col, filtros)

    aba_principal, aba_relacoes = st.tabs(
        ["Visão principal", "Relacionamento dinâmico"]
    )

    with aba_principal:
        render_kpis(df_filtrado, col)
        if df_filtrado.empty:
            st.warning("Nenhum registro encontrado com os filtros atuais.")
        else:
            render_graficos(df_filtrado, col)
            render_dados_filtrados(df_filtrado, col)

    with aba_relacoes:
        if df_filtrado.empty:
            st.info("Ajuste os filtros para gerar a análise dinâmica.")
        else:
            render_relacionamento_dinamico(df_filtrado, col)
