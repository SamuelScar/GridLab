"""Orquestra o fluxo principal do Dashboard F1: Insights de Corrida.

O módulo conecta as etapas de configuração visual, carregamento da base
analítica, construção dos filtros e renderização das abas do dashboard.
"""

import streamlit as st

from dashboard.components import (
    filtrar_base_temporada,
    montar_base_temporada,
    preparar_base_principal,
    render_cabecalho,
    render_contexto_analise,
    render_dados_filtrados,
    render_graficos,
    render_kpis,
    render_relacionamento_dinamico,
    render_seletor_visao,
)
from dashboard.config import CSS_PERSONALIZADO, DATA_DIR, obter_colunas
from dashboard.data import carregar_dados
from dashboard.filters import aplicar_filtros, construir_filtros


def configurar_pagina() -> None:
    """Aplica as configurações globais da página da aplicação.

    Define metadados da aba do navegador e injeta o CSS compartilhado para
    manter o padrão visual entre todos os componentes renderizados.
    """
    st.set_page_config(
        page_title="Dashboard F1: Adversidade e Resiliência Competitiva",
        page_icon=":bar_chart:",
        layout="wide",
    )
    st.markdown(CSS_PERSONALIZADO, unsafe_allow_html=True)


def main() -> None:
    """Executa o fluxo principal da aplicação.

    O fluxo segue quatro etapas:
    1. configurar a página e o cabeçalho;
    2. carregar a base analítica consolidada;
    3. coletar e aplicar os filtros escolhidos na sidebar;
    4. renderizar as abas principais do dashboard.

    """
    configurar_pagina()
    render_cabecalho()
    render_contexto_analise()

    visao = render_seletor_visao()
    if visao is None:
        st.stop()

    try:
        df = carregar_dados(DATA_DIR)
    except FileNotFoundError:
        st.error(f"Pasta de dados F1 não encontrada ou incompleta em `{DATA_DIR}`.")
        st.stop()

    col = obter_colunas()
    filtros = construir_filtros(df, col)
    df_filtrado = aplicar_filtros(df, col, filtros)

    base_temporada = montar_base_temporada(df_filtrado, col, visao)
    base_temporada = filtrar_base_temporada(base_temporada, filtros, visao)
    base_principal = preparar_base_principal(base_temporada, visao)

    if base_principal.empty:
        st.warning("Nenhum registro encontrado com os filtros atuais.")
    else:
        render_kpis(base_principal, visao)
        render_graficos(base_principal, visao)
        st.divider()
        render_relacionamento_dinamico(base_principal, visao)
        render_dados_filtrados(base_principal, visao)
