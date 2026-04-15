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
            "Ative apenas os filtros que quiser usar. Filtros desligados consideram todos os valores."
        )

        ano_min = int(df[col["ano"]].min())
        ano_max = int(df[col["ano"]].max())
        faixa_anos = st.slider(
            "Faixa de temporada",
            min_value=ano_min,
            max_value=ano_max,
            value=(ano_min, ano_max),
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

        circuito_opcoes = sorted(df[col["circuito"]].dropna().unique().tolist())
        circuitos_sel = _filtro_opcional_multiselect(
            rotulo_toggle="Filtrar por circuito",
            rotulo_select="Circuito",
            opcoes=circuito_opcoes,
            chave="circuitos",
        )

        pais_circuito_opcoes = sorted(df[col["pais_circuito"]].dropna().unique().tolist())
        paises_circuito_sel = _filtro_opcional_multiselect(
            rotulo_toggle="Filtrar por país do circuito",
            rotulo_select="País do circuito",
            opcoes=pais_circuito_opcoes,
            chave="paises_circuito",
        )

        status_opcoes = sorted(df[col["status"]].dropna().unique().tolist())
        status_sel = _filtro_opcional_multiselect(
            rotulo_toggle="Filtrar por status de chegada",
            rotulo_select="Status de chegada",
            opcoes=status_opcoes,
            chave="status",
        )

        apenas_concluidas = st.checkbox("Somente provas concluídas", value=False)
        apenas_pontuou = st.checkbox("Somente resultados com pontos", value=False)

        filtros_ativos = sum(
            valor is not None
            for valor in [
                equipes_sel,
                pilotos_sel,
                circuitos_sel,
                paises_circuito_sel,
                status_sel,
            ]
        )
        st.markdown(f"**Filtros ativos:** {filtros_ativos}")

    return {
        "faixa_anos": faixa_anos,
        "equipes": equipes_sel,
        "pilotos": pilotos_sel,
        "circuitos": circuitos_sel,
        "paises_circuito": paises_circuito_sel,
        "status": status_sel,
        "apenas_concluidas": apenas_concluidas,
        "apenas_pontuou": apenas_pontuou,
    }


def aplicar_filtros(
    df: pd.DataFrame, col: dict[str, str], filtros: dict[str, object]
) -> pd.DataFrame:
    """Aplica os filtros escolhidos na sidebar sobre a base analítica.

    A função preserva a semântica da interface:
    - filtros desativados não restringem resultados;
    - filtros ativados sem seleção retornam base vazia;
    - checkboxes adicionais refinam o subconjunto final.

    Args:
        df: Base analítica completa.
        col: Mapeamento de nomes amigáveis das colunas.
        filtros: Estado atual dos controles retornado por `construir_filtros`.

    Returns:
        Novo DataFrame contendo apenas os registros compatíveis com os filtros
        ativos.
    """
    mascara = df[col["ano"]].between(*filtros["faixa_anos"])

    if filtros["equipes"] is not None:
        if not filtros["equipes"]:
            return df.iloc[0:0].copy()
        mascara &= df[col["equipe"]].isin(filtros["equipes"])
    if filtros["pilotos"] is not None:
        if not filtros["pilotos"]:
            return df.iloc[0:0].copy()
        mascara &= df[col["piloto"]].isin(filtros["pilotos"])
    if filtros["circuitos"] is not None:
        if not filtros["circuitos"]:
            return df.iloc[0:0].copy()
        mascara &= df[col["circuito"]].isin(filtros["circuitos"])
    if filtros["paises_circuito"] is not None:
        if not filtros["paises_circuito"]:
            return df.iloc[0:0].copy()
        mascara &= df[col["pais_circuito"]].isin(filtros["paises_circuito"])
    if filtros["status"] is not None:
        if not filtros["status"]:
            return df.iloc[0:0].copy()
        mascara &= df[col["status"]].isin(filtros["status"])
    if filtros["apenas_concluidas"]:
        mascara &= df[col["concluiu"]]
    if filtros["apenas_pontuou"]:
        mascara &= df[col["pontuou"]]

    return df[mascara].copy()
