"""Componentes visuais e agregações usadas pelo dashboard.

O módulo organiza a interface em torno de uma pergunta central: como
adversidades ao longo da temporada se relacionam com a posição final de pilotos
e equipes no campeonato?
"""

import pandas as pd
import plotly.express as px
import streamlit as st


TOP_FINISH_LIMIT = {"Pilotos": 5, "Equipes": 3}
MIN_PARTICIPATION_PILOTS = 50.0
RATE_BANDS = ["0-10%", "11-20%", "21-30%", "31%+"]
RATE_COLORS = {
    "0-10%": "#CFE8E3",
    "11-20%": "#87BBA2",
    "21-30%": "#55828B",
    "31%+": "#3B6064",
}
POSITION_BAND_COLORS = {
    "Top 5": "#8ECAE6",
    "Top 3": "#8ECAE6",
    "6-10": "#006DAD",
    "4-6": "#006DAD",
    "11-20": "#F2A7A7",
    "7-10": "#F2A7A7",
    "21+": "#D62828",
    "11+": "#D62828",
}
RELATION_COLOR_SCALE = [
    (0.0, "#3E4A5C"),
    (0.35, "#5DA9C9"),
    (0.70, "#F2B84B"),
    (1.0, "#FF4B4B"),
]
SITUATION_COLORS = {
    "Com o problema": "#C1121F",
    "Sem o problema": "#669BBC",
}
BUBBLE_SIZE_MIN = 1.5
BUBBLE_SIZE_MAX = 11
BUBBLE_SIZE_P95 = 0.95


def media_formatada(valor: float, sufixo: str = "") -> str:
    """Formata médias numéricas para exibição textual."""
    if pd.isna(valor):
        return "N/A"
    return f"{valor:.2f}{sufixo}"


def percentual_formatado(valor: float) -> str:
    """Formata um valor percentual para exibição."""
    if pd.isna(valor):
        return "N/A"
    return f"{valor:.1f}%"


def ajustar_figura(fig):
    """Aplica o padrão visual compartilhado aos gráficos Plotly."""
    fig.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=10, r=10, t=60, b=10),
        legend_title_text="",
    )
    return fig


def _juntar_unicos(valores: pd.Series) -> str:
    """Une valores textuais únicos preservando legibilidade."""
    unicos = sorted(
        {
            str(valor).strip()
            for valor in valores.dropna()
            if str(valor).strip() and str(valor).strip() != "Não informado"
        }
    )
    if not unicos:
        return "Não informado"
    return ", ".join(unicos)


def _colunas_visao(visao: str, col: dict[str, str]) -> dict[str, str]:
    """Retorna o conjunto de colunas-base usadas em cada visão."""
    if visao == "Pilotos":
        return {
            "entidade": col["piloto"],
            "apoio": col["equipe"],
            "apoio_rotulo": "Equipe(s) na temporada",
            "pos_campeonato": col["pos_campeonato_piloto"],
            "pts_campeonato": col["pts_campeonato_piloto"],
            "participacoes": "Corridas disputadas",
            "top_label": "Top 5",
        }
    return {
        "entidade": col["equipe"],
        "apoio": col["piloto"],
        "apoio_rotulo": "Pilotos na temporada",
        "pos_campeonato": col["pos_campeonato_equipe"],
        "pts_campeonato": col["pts_campeonato_equipe"],
        "participacoes": "Resultados considerados",
        "top_label": "Top 3",
    }


def _meta_visao(visao: str) -> dict[str, str | int]:
    """Retorna rótulos compartilhados por visão."""
    if visao == "Pilotos":
        return {
            "apoio_rotulo": "Equipe(s) na temporada",
            "participacoes": "Corridas disputadas",
            "top_label": "Top 5",
            "faixas_posicao": ["Top 5", "6-10", "11-20", "21+"],
        }
    return {
        "apoio_rotulo": "Pilotos na temporada",
        "participacoes": "Resultados considerados",
        "top_label": "Top 3",
        "faixas_posicao": ["Top 3", "4-6", "7-10", "11+"],
    }


def _faixa_posicao(valor: float, visao: str) -> str:
    """Classifica a posição final em grupos simples."""
    if pd.isna(valor):
        return "Não informado"
    if visao == "Pilotos":
        if valor <= 5:
            return "Top 5"
        if valor <= 10:
            return "6-10"
        if valor <= 20:
            return "11-20"
        return "21+"
    if valor <= 3:
        return "Top 3"
    if valor <= 6:
        return "4-6"
    if valor <= 10:
        return "7-10"
    return "11+"


def _faixa_taxa_adversidade(valor: float) -> str:
    """Classifica a taxa de adversidade em faixas simples."""
    if pd.isna(valor):
        return "Não informado"
    if valor <= 10:
        return "0-10%"
    if valor <= 20:
        return "11-20%"
    if valor <= 30:
        return "21-30%"
    return "31%+"


def montar_base_temporada(
    df_filtrado: pd.DataFrame, col: dict[str, str], visao: str
) -> pd.DataFrame:
    """Agrega a base corrida a corrida em temporadas de pilotos ou equipes."""
    cfg = _colunas_visao(visao, col)
    dados = df_filtrado.dropna(
        subset=[
            col["ano"],
            cfg["entidade"],
            cfg["pos_campeonato"],
            cfg["pts_campeonato"],
        ]
    ).copy()
    if dados.empty:
        return pd.DataFrame()

    etapas_temporada = (
        df_filtrado.groupby(col["ano"], as_index=False)[col["id_corrida"]]
        .nunique()
        .rename(
            columns={
                col["ano"]: "Ano",
                col["id_corrida"]: "Etapas da temporada",
            }
        )
    )

    resumo = (
        dados.groupby(
            [col["ano"], cfg["entidade"], cfg["pos_campeonato"], cfg["pts_campeonato"]],
            as_index=False,
        )
        .agg(
            **{cfg["participacoes"]: (col["id_corrida"], "count")},
            **{
                cfg["apoio_rotulo"]: (cfg["apoio"], _juntar_unicos),
                "Incidentes": (col["incidente"], "sum"),
                "Falhas mecânicas": (col["falha_mecanica"], "sum"),
                "Outras não conclusões": (col["outra_nao_conclusao"], "sum"),
                "Adversidades": (col["adversidade"], "sum"),
            },
        )
        .rename(
            columns={
                col["ano"]: "Ano",
                cfg["entidade"]: "Entidade",
                cfg["pos_campeonato"]: "Posição final no campeonato",
                cfg["pts_campeonato"]: "Pontos finais na temporada",
            }
        )
    )

    resumo = resumo.merge(etapas_temporada, on="Ano", how="left")
    resumo["Taxa de adversidade (%)"] = (
        resumo["Adversidades"] / resumo[cfg["participacoes"]] * 100
    )
    resumo["Participação na temporada (%)"] = (
        resumo[cfg["participacoes"]] / resumo["Etapas da temporada"] * 100
    )
    resumo["Faixa de taxa de adversidade"] = resumo["Taxa de adversidade (%)"].apply(
        _faixa_taxa_adversidade
    )
    resumo["Faixa de posição final"] = resumo["Posição final no campeonato"].apply(
        lambda valor: _faixa_posicao(valor, visao)
    )
    resumo["Terminou no topo"] = (
        resumo["Posição final no campeonato"] <= TOP_FINISH_LIMIT[visao]
    )
    return resumo.sort_values(
        by=["Ano", "Posição final no campeonato", "Adversidades"],
        ascending=[False, True, False],
    ).reset_index(drop=True)


def preparar_base_principal(
    base_temporada: pd.DataFrame, visao: str
) -> pd.DataFrame:
    """Aplica recortes metodológicos para os gráficos principais."""
    if base_temporada.empty:
        return base_temporada

    if visao == "Pilotos":
        return base_temporada[
            base_temporada["Participação na temporada (%)"] >= MIN_PARTICIPATION_PILOTS
        ].reset_index(drop=True)
    return base_temporada.copy()


def filtrar_base_temporada(
    base_temporada: pd.DataFrame, filtros: dict[str, object], visao: str
) -> pd.DataFrame:
    """Aplica filtros de entidade sobre a base já agregada por temporada."""
    if base_temporada.empty:
        return base_temporada

    meta = _meta_visao(visao)
    filtrado = base_temporada.copy()

    equipes = filtros.get("equipes")
    pilotos = filtros.get("pilotos")

    if visao == "Pilotos":
        if pilotos is not None:
            if not pilotos:
                return filtrado.iloc[0:0].copy()
            filtrado = filtrado[filtrado["Entidade"].isin(pilotos)]
        if equipes is not None:
            if not equipes:
                return filtrado.iloc[0:0].copy()
            mascara = filtrado[meta["apoio_rotulo"]].apply(
                lambda texto: any(equipe in texto for equipe in equipes)
            )
            filtrado = filtrado[mascara]
    else:
        if equipes is not None:
            if not equipes:
                return filtrado.iloc[0:0].copy()
            filtrado = filtrado[filtrado["Entidade"].isin(equipes)]
        if pilotos is not None:
            if not pilotos:
                return filtrado.iloc[0:0].copy()
            mascara = filtrado[meta["apoio_rotulo"]].apply(
                lambda texto: any(piloto in texto for piloto in pilotos)
            )
            filtrado = filtrado[mascara]

    return filtrado.reset_index(drop=True)


def render_cabecalho() -> None:
    """Renderiza o título principal da aplicação."""
    st.title("Dashboard F1: Adversidade e Resiliência Competitiva")
    st.caption(
        "Análise descritiva de como incidentes e não conclusões se relacionam "
        "com a posição final no campeonato."
    )


def render_seletor_visao() -> str | None:
    """Renderiza a escolha inicial entre análise de pilotos ou equipes."""
    st.markdown(
        """
        <section class="analysis-choice">
            <p class="analysis-choice__eyebrow">Visão da análise</p>
            <h2>Escolha o foco do campeonato</h2>
            <p class="analysis-choice__subtitle">
                Selecione uma visão para carregar os filtros, indicadores e gráficos.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    return st.segmented_control(
        "Escolha o foco principal do campeonato",
        ["Pilotos", "Equipes"],
        default=None,
        format_func={
            "Pilotos": ":material/person: Pilotos",
            "Equipes": ":material/groups: Equipes",
        }.get,
        key="visao_analise",
        label_visibility="collapsed",
        width="stretch",
    )


def render_contexto_analise(
    visao: str | None = None, faixa_anos: tuple[int, int] | None = None
) -> None:
    """Apresenta o contexto do problema e a pergunta de pesquisa."""
    cautela_historica = (
        faixa_anos is not None and (faixa_anos[0] < 2010 or faixa_anos[1] > 2025)
    )
    nota_recorte = (
        "Comparações históricas amplas exigem cautela: regras, pontuação e número "
        "de corridas mudaram bastante."
        if cautela_historica
        else "Recorte recomendado: 2010 a 2025, quando as comparações ficam mais homogêneas."
    )

    st.markdown(
        f"""
        <section class="analysis-context">
            <div class="analysis-context__intro">
                <p class="analysis-context__eyebrow">Contexto da análise</p>
                <h2>Adversidade e posição final no campeonato</h2>
                <p>
                    O dashboard observa se temporadas com incidentes, falhas e
                    abandonos tendem a terminar em posições piores no campeonato.
                </p>
            </div>
            <div class="analysis-context__facts">
                <div class="analysis-context__fact">
                    <span>Pergunta</span>
                    <p>Incidentes e não conclusões estão associados à posição final?</p>
                </div>
                <div class="analysis-context__fact">
                    <span>Adversidade</span>
                    <p>Incidentes de pista, problemas mecânicos e outros abandonos.</p>
                </div>
                <div class="analysis-context__fact">
                    <span>Recorte</span>
                    <p>{nota_recorte}</p>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Definições e cuidados metodológicos", expanded=False):
        st.markdown("**O que entra como adversidade**")
        st.markdown(
            "- **Incidentes de pista**: batidas, colisões e saídas de pista."
        )
        st.markdown(
            "- **Problemas mecânicos**: falhas como motor, câmbio, transmissão, "
            "parte elétrica, suspensão e outros defeitos técnicos do carro."
        )
        st.markdown(
            "- **Outros abandonos**: corridas que não foram concluídas e que não se "
            "encaixam claramente nos dois grupos anteriores."
        )
        st.markdown(
            "- **Taxa de adversidade na temporada**: porcentagem de corridas "
            "daquele ano em que o piloto ou a equipe passou por pelo menos uma "
            "dessas situações."
        )
        st.markdown("**Cuidados na interpretação**")
        st.markdown(
            "- Ao comparar décadas diferentes, é preciso considerar mudanças no "
            "número de corridas por temporada, no sistema de pontuação e nas "
            "regras da Fórmula 1."
        )
        st.markdown(
            "- Para comparações mais justas, o recorte de 2010 a 2025 costuma ser "
            "o mais estável."
        )
        if visao == "Pilotos":
            st.markdown(
                "- Na visão de pilotos, os gráficos principais consideram apenas "
                "temporadas em que o piloto disputou pelo menos metade das corridas "
                "do ano. Isso evita comparações distorcidas com participações pontuais."
            )


def render_kpis(base_temporada: pd.DataFrame, visao: str) -> None:
    """Exibe indicadores principais da visão por temporada."""
    st.markdown("### Indicadores principais")

    kpi1, kpi2 = st.columns(2, gap="medium")
    kpi1.metric(
        "Temporadas analisadas",
        f"{len(base_temporada):,}".replace(",", "."),
    )
    kpi2.metric(
        "Adversidades totais",
        f"{int(base_temporada['Adversidades'].sum()):,}".replace(",", "."),
    )

    res1, res2, res3 = st.columns(3, gap="medium")
    res1.metric(
        "Taxa média de adversidade",
        percentual_formatado(base_temporada["Taxa de adversidade (%)"].mean()),
    )
    res2.metric(
        "Média de adversidades por temporada",
        media_formatada(base_temporada["Adversidades"].mean()),
    )
    res3.metric(
        "Pontos médios na temporada",
        media_formatada(base_temporada["Pontos finais na temporada"].mean()),
    )


def _resumo_por_posicao_final(base_temporada: pd.DataFrame) -> pd.DataFrame:
    """Resume a taxa média de adversidade por grupo de posição final."""
    dados = base_temporada.dropna(subset=["Faixa de posição final"]).copy()
    if dados.empty:
        return pd.DataFrame()

    resumo = (
        dados.groupby("Faixa de posição final", as_index=False)
        .agg(
            Temporadas=("Entidade", "count"),
            **{
                "Taxa média de adversidade (%)": (
                    "Taxa de adversidade (%)",
                    "mean",
                ),
            },
        )
    )
    return resumo


def _resumo_topo_por_taxa(base_temporada: pd.DataFrame) -> pd.DataFrame:
    """Resume a presença no topo por faixa de taxa de adversidade."""
    dados = base_temporada.dropna(subset=["Faixa de taxa de adversidade"]).copy()
    if dados.empty:
        return pd.DataFrame()

    resumo = (
        dados.groupby("Faixa de taxa de adversidade", as_index=False)
        .agg(
            Temporadas=("Entidade", "count"),
            **{
                "Taxa no topo (%)": ("Terminou no topo", lambda serie: serie.mean() * 100),
            },
        )
    )
    return resumo


def _comparacao_posicao_por_tipo(base_temporada: pd.DataFrame) -> pd.DataFrame:
    """Compara a posição média final com e sem cada tipo de problema."""
    tipos = [
        ("Incidentes", "Incidentes de pista"),
        ("Falhas mecânicas", "Problemas mecânicos"),
        ("Outras não conclusões", "Outros abandonos"),
    ]
    linhas: list[dict[str, float | str | int]] = []
    ordem_tipos: list[tuple[str, float]] = []

    for coluna, rotulo in tipos:
        com_tipo = base_temporada[base_temporada[coluna] > 0]
        sem_tipo = base_temporada[base_temporada[coluna] == 0]
        if com_tipo.empty or sem_tipo.empty:
            continue

        media_com = com_tipo["Posição final no campeonato"].mean()
        media_sem = sem_tipo["Posição final no campeonato"].mean()
        ordem_tipos.append((rotulo, media_com - media_sem))

        linhas.extend(
            [
                {
                    "Tipo de problema": rotulo,
                    "Situação": "Com o problema",
                    "Posição média final no campeonato": media_com,
                    "Taxa no topo (%)": com_tipo["Terminou no topo"].mean() * 100,
                    "Temporadas": len(com_tipo),
                },
                {
                    "Tipo de problema": rotulo,
                    "Situação": "Sem o problema",
                    "Posição média final no campeonato": media_sem,
                    "Taxa no topo (%)": sem_tipo["Terminou no topo"].mean() * 100,
                    "Temporadas": len(sem_tipo),
                },
            ]
        )

    if not linhas:
        return pd.DataFrame()

    comparacao = pd.DataFrame(linhas)
    ordem = [
        rotulo
        for rotulo, _ in sorted(ordem_tipos, key=lambda item: item[1], reverse=True)
    ]
    comparacao["Tipo de problema"] = pd.Categorical(
        comparacao["Tipo de problema"],
        categories=ordem,
        ordered=True,
    )
    return comparacao.sort_values(["Tipo de problema", "Situação"])


def _ranking_resiliencia(base_temporada: pd.DataFrame) -> pd.DataFrame:
    """Seleciona temporadas no topo com maior taxa de adversidade."""
    ranking = base_temporada[base_temporada["Terminou no topo"]].copy()
    if ranking.empty:
        return pd.DataFrame()

    ranking["Temporada"] = (
        ranking["Entidade"] + " (" + ranking["Ano"].astype(int).astype(str) + ")"
    )
    return ranking.sort_values(
        by=[
            "Taxa de adversidade (%)",
            "Adversidades",
            "Posição final no campeonato",
        ],
        ascending=[False, False, True],
    ).head(10)


def render_graficos(base_temporada: pd.DataFrame, visao: str) -> None:
    """Renderiza quatro gráficos simples alinhados à pergunta de pesquisa."""
    meta = _meta_visao(visao)
    entidade_label = "pilotos" if visao == "Pilotos" else "equipes"
    st.markdown("### Gráficos principais")
    st.caption(
        "Nos gráficos abaixo, cada observação representa uma temporada completa "
        f"de {entidade_label}. Sempre que aparecer a expressão taxa de "
        "adversidade, ela indica a porcentagem de corridas daquela temporada "
        "em que houve incidente de pista, problema mecânico ou outro abandono."
    )

    resumo_posicao = _resumo_por_posicao_final(base_temporada)
    resumo_taxa = _resumo_topo_por_taxa(base_temporada)
    comparacao_tipos = _comparacao_posicao_por_tipo(base_temporada)
    ranking = _ranking_resiliencia(base_temporada)

    row1_col1, row1_col2 = st.columns(2, gap="large")
    with row1_col1:
        if resumo_posicao.empty:
            st.info("Não há dados suficientes para resumir adversidade por posição final.")
        else:
            fig1 = px.bar(
                resumo_posicao,
                x="Faixa de posição final",
                y="Taxa média de adversidade (%)",
                color="Faixa de posição final",
                title=(
                    "Taxa média de adversidade por faixa de posição final "
                    f"no campeonato ({entidade_label})"
                ),
                text_auto=".1f",
                hover_data={"Temporadas": True, "Taxa média de adversidade (%)": ":.1f"},
                category_orders={"Faixa de posição final": meta["faixas_posicao"]},
            )
            fig1.update_layout(showlegend=False)
            fig1.update_xaxes(title="Faixa de posição final no campeonato")
            st.plotly_chart(ajustar_figura(fig1), width="stretch")
            st.caption(
                f"Cada barra resume temporadas de {entidade_label}. A posição "
                "final é a do campeonato, não a de uma corrida isolada."
            )

    with row1_col2:
        if resumo_taxa.empty:
            st.info("Não há dados suficientes para resumir presença no topo por taxa.")
        else:
            fig2 = px.bar(
                resumo_taxa,
                x="Faixa de taxa de adversidade",
                y="Taxa no topo (%)",
                color="Faixa de taxa de adversidade",
                color_discrete_map=RATE_COLORS,
                title=f"Percentual de temporadas no {meta['top_label']} por faixa de taxa de adversidade",
                text_auto=".1f",
                hover_data={"Temporadas": True, "Taxa no topo (%)": ":.1f"},
                category_orders={"Faixa de taxa de adversidade": RATE_BANDS},
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(ajustar_figura(fig2), width="stretch")
            st.caption(
                f"Leitura: cada barra agrupa temporadas de {entidade_label} pela "
                "porcentagem de corridas com adversidade. A altura mostra qual "
                f"parcela dessas temporadas conseguiu terminar no {meta['top_label']} "
                "do campeonato."
            )

    row2_col1, row2_col2 = st.columns(2, gap="large")
    with row2_col1:
        if comparacao_tipos.empty:
            st.info("Não há dados suficientes para comparar o efeito dos tipos de problema.")
        else:
            fig3 = px.bar(
                comparacao_tipos,
                x="Posição média final no campeonato",
                y="Tipo de problema",
                orientation="h",
                color="Situação",
                barmode="group",
                color_discrete_map=SITUATION_COLORS,
                title="Posição média final com e sem cada tipo de problema",
                text_auto=".1f",
                hover_data={
                    "Posição média final no campeonato": ":.2f",
                    "Taxa no topo (%)": ":.1f",
                    "Temporadas": True,
                },
            )
            fig3.update_xaxes(
                title="Posição média final no campeonato (quanto menor, melhor)"
            )
            st.plotly_chart(ajustar_figura(fig3), width="stretch")
            st.caption(
                "Em cada tipo de problema, compare as barras de 'Com o problema' "
                "e 'Sem o problema'. Quanto mais à direita a barra estiver, pior "
                "foi a posição média final no campeonato."
            )

    with row2_col2:
        if ranking.empty:
            st.info("Não há temporadas resilientes suficientes no recorte atual.")
        else:
            fig4 = px.bar(
                ranking.sort_values("Taxa de adversidade (%)"),
                x="Taxa de adversidade (%)",
                y="Temporada",
                orientation="h",
                title=f"Temporadas no {meta['top_label']} com maior taxa de adversidade",
                hover_data={
                    "Posição final no campeonato": True,
                    "Pontos finais na temporada": ":.1f",
                    "Adversidades": True,
                    "Incidentes": True,
                    "Falhas mecânicas": True,
                    "Outras não conclusões": True,
                },
            )
            st.plotly_chart(ajustar_figura(fig4), width="stretch")
            st.caption(
                "Aviso: Ao incluir décadas antigas, compare com "
                "cautela. A F1 mudou bastante em regras, sistema de pontuação, "
                "confiabilidade e número de corridas por temporada."
            )


def _adicionar_resultado_visual(dados: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Cria um eixo visual em que valores maiores representam melhor resultado."""
    analisado = dados.copy()
    analisado["Temporada"] = (
        analisado["Entidade"] + " (" + analisado["Ano"].astype(int).astype(str) + ")"
    )
    analisado["Relação adversidade/posição"] = (
        analisado["Taxa de adversidade (%)"] / analisado["Posição final no campeonato"]
    )
    relacao_suavizada = analisado["Relação adversidade/posição"].pow(0.5)
    limite_superior = relacao_suavizada.quantile(BUBBLE_SIZE_P95)
    if pd.isna(limite_superior) or limite_superior <= 0:
        analisado["Tamanho visual da bolha"] = BUBBLE_SIZE_MIN
        analisado["Intensidade da relação (%)"] = 0.0
    else:
        relacao_limitada = relacao_suavizada.clip(upper=limite_superior)
        maximo = relacao_limitada.max()
        if pd.isna(maximo) or maximo <= 0:
            analisado["Tamanho visual da bolha"] = BUBBLE_SIZE_MIN
            analisado["Intensidade da relação (%)"] = 0.0
        else:
            analisado["Tamanho visual da bolha"] = (
                BUBBLE_SIZE_MIN
                + (relacao_limitada / maximo)
                * (BUBBLE_SIZE_MAX - BUBBLE_SIZE_MIN)
            )
            analisado["Intensidade da relação (%)"] = relacao_limitada / maximo * 100
    pior_posicao = int(analisado["Posição final no campeonato"].max())
    analisado["Resultado final visual"] = (
        pior_posicao + 1 - analisado["Posição final no campeonato"]
    )
    return analisado, pior_posicao


def _ticks_resultado_visual(pior_posicao: int) -> tuple[list[float], list[str]]:
    """Monta rótulos do eixo visual usando a posição real no campeonato."""
    candidatos = [1, 3, 5, 10, 15, 20, 25, 30]
    posicoes = [pos for pos in candidatos if pos <= pior_posicao]
    if pior_posicao not in posicoes:
        posicoes.append(pior_posicao)

    ticks = [
        (pior_posicao + 1 - posicao, f"{posicao}º" + (" (melhor)" if posicao == 1 else ""))
        for posicao in sorted(set(posicoes))
    ]
    ticks_ordenados = sorted(ticks, key=lambda item: item[0])
    return [valor for valor, _ in ticks_ordenados], [rotulo for _, rotulo in ticks_ordenados]


def render_relacionamento_dinamico(base_temporada: pd.DataFrame, visao: str) -> None:
    """Renderiza uma análise direcionada da relação adversidade x resultado."""
    entidade_label = "pilotos" if visao == "Pilotos" else "equipes"
    st.markdown("### Adversidade x resultado")
    st.caption(
        "Cada ponto representa uma temporada. A leitura principal é simples: "
        "quanto mais à direita, maior foi a taxa de adversidade; quanto mais alto, "
        "melhor foi o resultado final no campeonato."
    )
    st.caption(
        "A relação usada no tamanho e na cor das bolhas é: taxa de adversidade "
        "dividida pela posição final. Ela fica maior quando uma temporada combina "
        "muita adversidade com uma boa colocação no campeonato."
    )

    dados = base_temporada.dropna(
        subset=["Taxa de adversidade (%)", "Posição final no campeonato"]
    ).copy()
    if dados.empty:
        st.info("Ajuste os filtros para gerar a análise de associação.")
        return

    dados, pior_posicao = _adicionar_resultado_visual(dados)
    y_ticks, y_tick_labels = _ticks_resultado_visual(pior_posicao)
    fig = px.scatter(
        dados,
        x="Taxa de adversidade (%)",
        y="Resultado final visual",
        size="Tamanho visual da bolha",
        color="Intensidade da relação (%)",
        color_continuous_scale=RELATION_COLOR_SCALE,
        hover_name="Temporada",
        hover_data={
            "Resultado final visual": False,
            "Ano": True,
            "Entidade": False,
            "Faixa de posição final": True,
            "Posição final no campeonato": ":.0f",
            "Pontos finais na temporada": ":.1f",
            "Adversidades": True,
            "Incidentes": True,
            "Falhas mecânicas": True,
            "Outras não conclusões": True,
            "Relação adversidade/posição": ":.2f",
            "Tamanho visual da bolha": False,
            "Intensidade da relação (%)": False,
        },
        title=f"Adversidade e resultado final por temporada ({entidade_label})",
        size_max=BUBBLE_SIZE_MAX,
        opacity=0.78,
    )
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Adversidade<br>com boa<br>posição",
            tickvals=[0, 50, 100],
            ticktext=["Baixo", "Médio", "Alto"],
        )
    )
    fig.update_xaxes(title="Taxa de adversidade na temporada (%)")
    fig.update_yaxes(
        title="Resultado final (mais alto = melhor)",
        tickmode="array",
        tickvals=y_ticks,
        ticktext=y_tick_labels,
        range=[0.4, pior_posicao + 1.8],
    )
    st.plotly_chart(ajustar_figura(fig), width="stretch")
    st.caption(
        "Bolhas maiores e cores mais fortes indicam maior taxa de adversidade em "
        "relação à posição final. A cor é uma escala relativa do recorte atual: "
        "baixo, médio ou alto destaque para temporadas que combinaram muita "
        "adversidade com bom resultado no campeonato."
    )


def render_dados_filtrados(base_temporada: pd.DataFrame, visao: str) -> None:
    """Exibe a tabela detalhada já resumida por temporada."""
    st.divider()
    if base_temporada.empty:
        st.info("Não há temporadas para exibir com os filtros atuais.")
        return

    meta = _meta_visao(visao)
    df_exibicao = base_temporada[
        [
            "Ano",
            "Entidade",
            meta["apoio_rotulo"],
            "Posição final no campeonato",
            "Pontos finais na temporada",
            meta["participacoes"],
            "Incidentes",
            "Falhas mecânicas",
            "Outras não conclusões",
            "Adversidades",
            "Taxa de adversidade (%)",
            "Participação na temporada (%)",
            "Faixa de posição final",
            "Faixa de taxa de adversidade",
        ]
    ].copy()

    with st.expander("Dados consolidados por temporada (clique para abrir)", expanded=False):
        st.caption(
            "Cada linha representa uma temporada completa de piloto ou equipe, "
            "considerando os filtros atuais."
        )
        st.dataframe(
            df_exibicao.round(2),
            width="stretch",
            hide_index=True,
        )
