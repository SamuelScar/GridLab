"""Construção e aplicação dos filtros exibidos na sidebar.

O módulo concentra a lógica de interface e filtragem para manter o restante da
aplicação focado em visualização e transformação de dados.
"""

import pandas as pd
import streamlit as st


def _filtro_opcional_multiselect(
    *,
    rotulo_toggle: str,
    rotulo_select: str,
    opcoes: list[str],
    chave: str,
) -> list[str] | None:
    """Renderiza um filtro multiselect que pode ser ligado ou desligado.

    Args:
        rotulo_toggle: Texto do controle que ativa ou desativa o filtro.
        rotulo_select: Texto exibido acima do campo multiselect.
        opcoes: Valores disponíveis para seleção.
        chave: Prefixo usado nas chaves de estado da interface.

    Returns:
        `None` quando o filtro está desativado; caso contrário, a lista de
        valores selecionados, que pode estar vazia.
    """
    ativo = st.toggle(rotulo_toggle, value=False, key=f"{chave}_ativo")
    if not ativo:
        return None

    return st.multiselect(
        rotulo_select,
        opcoes,
        default=[],
        placeholder="Selecione uma ou mais opções",
        key=f"{chave}_valores",
    )


def construir_filtros(df: pd.DataFrame, col: dict[str, str]) -> dict[str, object]:
    """Renderiza a sidebar e coleta os filtros selecionados pelo usuário.

    Args:
        df: Base analítica completa usada para gerar opções e limites.
        col: Mapeamento entre identificadores internos e nomes amigáveis das
            colunas do dashboard.

    Returns:
        Dicionário serializável com o estado atual de todos os filtros da
        interface, pronto para ser consumido por `aplicar_filtros`.
    """
    with st.sidebar:
        st.title("Filtros")
        st.markdown(
            "Use filtros simples de temporada para manter a leitura do campeonato coerente."
        )
        st.caption(
            "Temporadas em andamento podem distorcer a posição final no campeonato."
        )

        ano_min = int(df[col["ano"]].min())
        ano_max = int(df[col["ano"]].max())
        inicio_padrao = 2010 if ano_min <= 2010 <= ano_max else ano_min
        fim_padrao = 2025 if ano_min <= 2025 <= ano_max else ano_max
        if inicio_padrao > fim_padrao:
            inicio_padrao, fim_padrao = ano_min, ano_max
        faixa_anos = st.slider(
            "Faixa de temporada",
            min_value=ano_min,
            max_value=ano_max,
            value=(inicio_padrao, fim_padrao),
        )

        equipe_opcoes = sorted(df[col["equipe"]].dropna().unique().tolist())
        equipes_sel = _filtro_opcional_multiselect(
            rotulo_toggle="Filtrar por equipe",
            rotulo_select="Equipe",
            opcoes=equipe_opcoes,
            chave="equipes",
        )

        piloto_opcoes = sorted(df[col["piloto"]].dropna().unique().tolist())
        pilotos_sel = _filtro_opcional_multiselect(
            rotulo_toggle="Filtrar por piloto",
            rotulo_select="Piloto",
            opcoes=piloto_opcoes,
            chave="pilotos",
        )

        filtros_ativos = sum(
            valor is not None
            for valor in [
                equipes_sel,
                pilotos_sel,
            ]
        )
        st.markdown(f"**Filtros ativos:** {filtros_ativos}")

    return {
        "faixa_anos": faixa_anos,
        "equipes": equipes_sel,
        "pilotos": pilotos_sel,
    }


def aplicar_filtros(
    df: pd.DataFrame, col: dict[str, str], filtros: dict[str, object]
) -> pd.DataFrame:
    """Aplica os filtros escolhidos na sidebar sobre a base analítica.

    Nesta versão do projeto, apenas o recorte temporal é aplicado na base
    corrida a corrida. Os filtros de piloto e equipe são aplicados depois, já
    sobre a base resumida por temporada, para evitar temporadas parciais.

    Args:
        df: Base analítica completa.
        col: Mapeamento de nomes amigáveis das colunas.
        filtros: Estado atual dos controles retornado por `construir_filtros`.

    Returns:
        Novo DataFrame contendo apenas os registros dentro da faixa de anos.
    """
    mascara = df[col["ano"]].between(*filtros["faixa_anos"])

    return df[mascara].copy()
