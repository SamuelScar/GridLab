"""Componentes visuais e agregações usadas pelo dashboard.

O módulo combina pequenas rotinas de formatação, cálculos auxiliares e a
renderização dos elementos visuais e gráficos apresentados ao usuário final.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# Paleta base manual para países frequentes nas visualizações.
PAIS_COR_BASE = {
    "Estados Unidos": "#3C3B6E",
    "Itália": "#009246",
    "Áustria": "#ED2939",
    "Suécia": "#006AA7",
    "Suíça": "#D52B1E",
    "Nova Zelândia": "#1E3A8A",
    "Bélgica": "#FFD90C",
    "França": "#0055A4",
    "Argentina": "#6CB4EE",
    "África do Sul": "#2E7D32",
    "Reino Unido": "#1B4BA0",
    "Brasil": "#1E9C3F",
    "Alemanha": "#FFCC00",
    "Países Baixos": "#FF6F00",
    "Espanha": "#AA151B",
    "Canadá": "#D80621",
    "Austrália": "#1976D2",
    "Finlândia": "#1F6FEB",
    "México": "#006847",
    "Japão": "#BC002D",
    "Mônaco": "#CE1126",
    "Portugal": "#046A38",
    "Dinamarca": "#C60C30",
    "Irlanda": "#169B62",
    "Polônia": "#DC143C",
    "Rússia": "#2557A7",
    "Tchéquia": "#11457E",
    "Chile": "#D52B1E",
    "Uruguai": "#2D68C4",
    "Venezuela": "#0038A8",
    "Tailândia": "#A51931",
    "China": "#DE2910",
    "Índia": "#FF9933",
    "Indonésia": "#CE1126",
    "Malásia": "#005AAA",
    "Hong Kong": "#C8102E",
    "Hungria": "#477050",
    "Colômbia": "#FCD116",
    "Liechtenstein": "#002B7F",
    "Alemanha Oriental": "#FDB913",
    "Rodésia": "#4CAF50",
}

# Conjunto de status considerados falhas mecânicas para fins analíticos.
MECHANICAL_FAILURE_STATUSES = {
    "Engine",
    "Gearbox",
    "Transmission",
    "Clutch",
    "Hydraulics",
    "Electrical",
    "Radiator",
    "Suspension",
    "Brakes",
    "Differential",
    "Overheating",
    "Mechanical",
    "Tyre",
    "Puncture",
    "Driveshaft",
    "Fuel pump",
    "Fuel pressure",
    "Oil pressure",
    "Water pressure",
    "Fuel",
    "Throttle",
    "Electronics",
    "Power Unit",
    "ERS",
    "Turbo",
    "CV joint",
    "Wheel",
    "Wheel bearing",
    "Rear wing",
    "Front wing",
    "Technical",
    "Spark plugs",
    "Alternator",
    "Injection",
    "Fuel leak",
    "Exhaust",
    "Oil leak",
    "Halfshaft",
    "Crankshaft",
    "Vibrations",
    "Undertray",
    "Power loss",
    "Ignition",
    "Battery",
    "Distributor",
    "Magneto",
    "Water leak",
}


def _mapear_cores_paises(paises: list[str]) -> dict[str, str]:
    """Mapeia países para cores consistentes nas visualizações.

    Args:
        paises: Lista de países na ordem em que aparecem no gráfico.

    Returns:
        Dicionário de país para cor hexadecimal, usando a paleta base sempre
        que disponível e uma paleta Plotly como fallback.
    """
    fallback = (
        px.colors.qualitative.Safe
        + px.colors.qualitative.Bold
        + px.colors.qualitative.Set2
    )
    mapa: dict[str, str] = {}
    idx_fallback = 0
    for pais in dict.fromkeys(paises):
        if pais in PAIS_COR_BASE:
            mapa[pais] = PAIS_COR_BASE[pais]
        else:
            mapa[pais] = fallback[idx_fallback % len(fallback)]
            idx_fallback += 1
    return mapa


def media_formatada(valor: float, sufixo: str = "") -> str:
    """Formata médias numéricas para exibição textual.

    Args:
        valor: Valor numérico que será exibido.
        sufixo: Texto opcional concatenado ao final do número formatado.

    Returns:
        String formatada com duas casas decimais ou `N/A` para valores ausentes.
    """
    if pd.isna(valor):
        return "N/A"
    return f"{valor:.2f}{sufixo}"


def percentual_formatado(valor: float) -> str:
    """Formata um valor percentual para exibição.

    Args:
        valor: Valor percentual em escala de 0 a 100.

    Returns:
        String formatada com uma casa decimal ou `N/A` para valores ausentes.
    """
    if pd.isna(valor):
        return "N/A"
    return f"{valor:.1f}%"


def ajustar_figura(fig):
    """Aplica o padrão visual compartilhado aos gráficos Plotly.

    Args:
        fig: Figura Plotly já construída.

    Returns:
        A própria figura recebida, após aplicar layout, altura e margens
        padronizadas para o dashboard.
    """
    fig.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=10, r=10, t=60, b=10),
        legend_title_text="",
    )
    return fig


def render_cabecalho() -> None:
    """Renderiza o título principal da aplicação."""
    st.title("Dashboard F1: Insights de Corrida e Performance")


def render_kpis(df_filtrado: pd.DataFrame, col: dict[str, str]) -> None:
    """Exibe os indicadores principais com base no recorte atual.

    Args:
        df_filtrado: Base já filtrada conforme a seleção do usuário.
        col: Mapeamento de nomes amigáveis das colunas.
    """
    st.markdown("### Indicadores principais")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

    pontos_totais = df_filtrado[col["pontos"]].sum(min_count=1)
    if pd.isna(pontos_totais):
        pontos_totais_txt = "N/A"
    else:
        pontos_totais_txt = f"{pontos_totais:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

    kpi1.metric("Resultados filtrados", f"{len(df_filtrado):,}".replace(",", "."))
    kpi2.metric(
        "Corridas únicas",
        f"{df_filtrado[col['id_corrida']].nunique():,}".replace(",", "."),
    )
    kpi3.metric(
        "Pilotos únicos",
        f"{df_filtrado[col['piloto']].nunique():,}".replace(",", "."),
    )
    kpi4.metric(
        "Pontuação total",
        pontos_totais_txt,
    )


def _falha_mecanica_por_nacionalidade(
    df_filtrado: pd.DataFrame, col: dict[str, str]
) -> pd.DataFrame:
    """Resume a incidência de falhas mecânicas por país do piloto.

    Args:
        df_filtrado: Base analítica após aplicação dos filtros.
        col: Mapeamento de nomes amigáveis das colunas.

    Returns:
        DataFrame agregado com participações, falhas mecânicas e taxa de falha
        por país, já limitado ao top 10 com amostra mínima.
    """
    dados = df_filtrado.dropna(
        subset=[col["nac_piloto"], col["status"]]
    )
    dados = dados.copy()
    dados["Falha mecânica"] = dados[col["status"]].isin(MECHANICAL_FAILURE_STATUSES)

    resumo = (
        dados.groupby(col["nac_piloto"], as_index=False)
        .agg(
            Participações=(col["id_corrida"], "count"),
            **{
                "Falhas mecânicas": ("Falha mecânica", "sum"),
                "Taxa de falha mecânica (%)": (
                    "Falha mecânica",
                    lambda serie: serie.mean() * 100,
                ),
            },
        )
        .sort_values("Participações", ascending=False)
    )
    filtrado = resumo[resumo["Participações"] >= 120]
    if filtrado.empty:
        filtrado = resumo[resumo["Participações"] >= 20]
    return filtrado.sort_values("Taxa de falha mecânica (%)", ascending=False).head(10)


def _pilotos_maior_recuperacao(
    df_filtrado: pd.DataFrame, col: dict[str, str]
) -> pd.DataFrame:
    """Identifica pilotos que mais ganham posições ao longo da corrida.

    Args:
        df_filtrado: Base analítica após aplicação dos filtros.
        col: Mapeamento de nomes amigáveis das colunas.

    Returns:
        DataFrame agregado por piloto com média de posições ganhas, taxa de
        abandono e filtro por amostra mínima.
    """
    dados = df_filtrado[df_filtrado[col["grid"]].between(1, 20)].dropna(
        subset=[col["piloto"], col["ganho"], col["abandono"]]
    )
    resumo = (
        dados.groupby(col["piloto"], as_index=False)
        .agg(
            Largadas=(col["id_corrida"], "count"),
            **{
                "Posições ganhas médias": (col["ganho"], "mean"),
                "Taxa de abandono (%)": (col["abandono"], lambda serie: serie.mean() * 100),
            },
        )
        .sort_values("Largadas", ascending=False)
    )
    filtrado = resumo[resumo["Largadas"] >= 40]
    if filtrado.empty:
        filtrado = resumo[resumo["Largadas"] >= 10]
    return filtrado.sort_values("Posições ganhas médias", ascending=False).head(10)


def _desempenho_por_faixa_grid(
    df_filtrado: pd.DataFrame, col: dict[str, str]
) -> pd.DataFrame:
    """Calcula desempenho médio por faixa de posição de largada.

    Args:
        df_filtrado: Base analítica após aplicação dos filtros.
        col: Mapeamento de nomes amigáveis das colunas.

    Returns:
        DataFrame com amostra, taxa de pódio e taxa de pontuação por faixa de
        grid, considerando apenas largadas válidas entre 1 e 20.
    """
    dados = df_filtrado[df_filtrado[col["grid"]].between(1, 20)].dropna(
        subset=[col["grid"], col["chegada"], col["pontos"]]
    )
    dados = dados.copy()
    dados["Faixa do grid"] = pd.cut(
        dados[col["grid"]],
        bins=[0, 5, 10, 15, 20],
        labels=["1-5", "6-10", "11-15", "16-20"],
    )
    dados["pódio"] = dados[col["chegada"]] <= 3
    dados["pontuou_temp"] = dados[col["pontos"]] > 0

    resumo = (
        dados.groupby("Faixa do grid", as_index=False, observed=True)
        .agg(
            Amostra=(col["id_corrida"], "count"),
            **{
                "Taxa de pódio (%)": ("pódio", lambda serie: serie.mean() * 100),
                "Taxa de pontuar (%)": ("pontuou_temp", lambda serie: serie.mean() * 100),
            },
        )
        .sort_values("Faixa do grid")
    )
    return resumo[resumo["Amostra"] >= 30]


def _numero_da_sorte(df_filtrado: pd.DataFrame, col: dict[str, str]) -> pd.DataFrame:
    """Resume o desempenho histórico associado a cada número de piloto.

    Args:
        df_filtrado: Base analítica após aplicação dos filtros.
        col: Mapeamento de nomes amigáveis das colunas.

    Returns:
        DataFrame agregado por número do piloto com volume de corridas,
        vitórias, pontos e métricas percentuais usadas no gráfico temático.
    """
    dados = df_filtrado.dropna(
        subset=[col["numero_piloto"], col["chegada"], col["pontos"]]
    ).copy()
    if dados.empty:
        return pd.DataFrame()

    dados["vitória"] = dados[col["chegada"]] == 1
    resumo = (
        dados.groupby(col["numero_piloto"], as_index=False)
        .agg(
            **{"Corridas com esse número": (col["id_corrida"], "count")},
            **{
                "Vitórias": ("vitória", "sum"),
                "Pontos totais": (col["pontos"], "sum"),
                "Percentual de corridas com pontos (%)": (
                    col["pontuou"],
                    lambda serie: serie.mean() * 100,
                ),
                "Percentual de vitórias (%)": (
                    "vitória",
                    lambda serie: serie.mean() * 100,
                ),
                "Pontos médios": (col["pontos"], "mean"),
            },
        )
        .sort_values("Corridas com esse número", ascending=False)
    )

    resumo = resumo.copy()
    resumo[col["numero_piloto"]] = resumo[col["numero_piloto"]].astype(int)
    resumo["Número"] = "Nº " + resumo[col["numero_piloto"]].astype(str)
    return resumo


def _abandono_por_tamanho_prova(
    df_filtrado: pd.DataFrame, col: dict[str, str]
) -> pd.DataFrame:
    """Mede abandono e ganho médio por tamanho da prova.

    Args:
        df_filtrado: Base analítica após aplicação dos filtros.
        col: Mapeamento de nomes amigáveis das colunas.

    Returns:
        DataFrame resumido por faixa de quantidade de voltas, já com taxa de
        abandono e média de posições ganhas.
    """
    dados = df_filtrado.dropna(
        subset=[col["id_corrida"], col["voltas"], col["abandono"], col["ganho"]]
    ).copy()
    if dados.empty:
        return pd.DataFrame()

    voltas_gp = (
        dados.groupby(col["id_corrida"], as_index=False)[col["voltas"]]
        .max()
        .rename(columns={col["voltas"]: "Voltas da corrida"})
    )
    dados = dados.merge(voltas_gp, on=col["id_corrida"], how="left")
    dados["Faixa de corrida"] = pd.cut(
        dados["Voltas da corrida"],
        bins=[0, 55, 66, float("inf")],
        labels=[
            "Curta (até 55 voltas)",
            "Média (56 a 66 voltas)",
            "Longa (67+ voltas)",
        ],
    )

    resumo = (
        dados.groupby("Faixa de corrida", as_index=False, observed=True)
        .agg(
            Resultados=(col["id_corrida"], "count"),
            **{
                "Taxa de abandono (%)": (col["abandono"], lambda serie: serie.mean() * 100),
                "Posições ganhas médias": (col["ganho"], "mean"),
            },
        )
        .sort_values("Faixa de corrida")
    )
    return resumo[resumo["Resultados"] >= 30]


def render_graficos(df_filtrado: pd.DataFrame, col: dict[str, str]) -> None:
    """Renderiza o conjunto principal de gráficos do dashboard.

    Os quatro gráficos cobrem:
    - falhas mecânicas por país;
    - recuperação média de posições por piloto;
    - desempenho por número do piloto;
    - abandono por faixa de tamanho da corrida.

    Args:
        df_filtrado: Base já filtrada conforme a seleção do usuário.
        col: Mapeamento de nomes amigáveis das colunas.
    """
    st.markdown("### Gráficos principais")

    row1_col1, row1_col2 = st.columns(2, gap="large")
    with row1_col1:
        falhas_nacionalidade = _falha_mecanica_por_nacionalidade(df_filtrado, col)
        if falhas_nacionalidade.empty:
            st.info("Não há dados suficientes para o ranking de falha mecânica por país.")
        else:
            ranking_paises = falhas_nacionalidade.sort_values(
                "Taxa de falha mecânica (%)", ascending=False
            )
            ordem_paises = ranking_paises[col["nac_piloto"]].astype(str).tolist()
            mapa_cores = _mapear_cores_paises(
                ranking_paises[col["nac_piloto"]].astype(str).tolist()
            )
            fig1 = px.bar(
                ranking_paises,
                x="Taxa de falha mecânica (%)",
                y=col["nac_piloto"],
                color=col["nac_piloto"],
                color_discrete_map=mapa_cores,
                category_orders={col["nac_piloto"]: ordem_paises},
                orientation="h",
                title="Top 10 países com maior taxa de falha mecânica",
                hover_data={
                    "Participações": True,
                    "Falhas mecânicas": True,
                    "Taxa de falha mecânica (%)": ":.1f",
                },
            )
            fig1.update_layout(showlegend=False)
            fig1.update_yaxes(
                categoryorder="array",
                categoryarray=ordem_paises,
                autorange="reversed",
            )
            fig1.update_traces(
                marker_line_color="rgba(255, 255, 255, 0.28)",
                marker_line_width=0.8,
            )
            st.plotly_chart(ajustar_figura(fig1), use_container_width=True)

    with row1_col2:
        recuperacao_pilotos = _pilotos_maior_recuperacao(df_filtrado, col)
        if recuperacao_pilotos.empty:
            st.info("Não há dados suficientes para o ranking de recuperação por piloto.")
        else:
            fig2 = px.bar(
                recuperacao_pilotos.sort_values("Posições ganhas médias", ascending=True),
                x="Posições ganhas médias",
                y=col["piloto"],
                orientation="h",
                title="Top 10 pilotos que mais ganham posições na corrida",
                hover_data={
                    "Largadas": True,
                    "Taxa de abandono (%)": ":.1f",
                    "Posições ganhas médias": ":.2f",
                },
            )
            st.plotly_chart(ajustar_figura(fig2), use_container_width=True)

    row2_col1, row2_col2 = st.columns(2, gap="large")
    with row2_col1:
        numero_sorte = _numero_da_sorte(df_filtrado, col)
        if numero_sorte.empty:
            st.info("Não há dados suficientes para o gráfico 'Número da sorte'.")
        else:
            opcoes_metricas = {
                "Vitórias (total)": "Vitórias",
                "Pontos (total acumulado)": "Pontos totais",
                "Corridas em que venceu (%)": "Percentual de vitórias (%)",
            }
            explicacao_metricas = {
                "Vitórias (total)": "Soma de todas as vitórias de pilotos que usaram cada número.",
                "Pontos (total acumulado)": "Soma de todos os pontos marcados por pilotos que usaram cada número.",
                "Corridas em que venceu (%)": "Percentual de corridas vencidas entre as corridas disputadas com cada número.",
            }
            metrica = st.selectbox(
                "Métrica do número da sorte",
                list(opcoes_metricas.keys()),
                key="metrica_numero_sorte",
            )
            metrica_coluna = opcoes_metricas[metrica]
            ranking = numero_sorte.sort_values(metrica_coluna, ascending=False).head(10)
            fig3 = px.bar(
                ranking.sort_values(metrica_coluna, ascending=True),
                x=metrica_coluna,
                y="Número",
                orientation="h",
                title=f"Número da sorte: top 10 por {metrica}",
                hover_data={
                    "Corridas com esse número": True,
                    "Vitórias": True,
                    "Pontos totais": ":.1f",
                    "Percentual de vitórias (%)": ":.1f",
                    "Pontos médios": ":.2f",
                },
            )
            st.plotly_chart(ajustar_figura(fig3), use_container_width=True)
            st.caption(f"Como ler: {explicacao_metricas[metrica]}")
            st.caption(
                "Obs.: inclui números históricos (0 e >99) registrados em corridas antigas."
            )

    with row2_col2:
        tamanho_prova = _abandono_por_tamanho_prova(df_filtrado, col)
        if tamanho_prova.empty:
            st.info("Não há dados suficientes para analisar abandono por tamanho de corrida.")
        else:
            fig4 = px.bar(
                tamanho_prova,
                x="Faixa de corrida",
                y="Taxa de abandono (%)",
                color="Faixa de corrida",
                title="Abandono por tamanho da corrida (faixa de voltas)",
                category_orders={
                    "Faixa de corrida": [
                        "Curta (até 55 voltas)",
                        "Média (56 a 66 voltas)",
                        "Longa (67+ voltas)",
                    ]
                },
                hover_data={
                    "Resultados": True,
                    "Taxa de abandono (%)": ":.1f",
                    "Posições ganhas médias": ":.2f",
                },
            )
            fig4.update_layout(showlegend=False)
            st.plotly_chart(ajustar_figura(fig4), use_container_width=True)
            st.caption("Se uma faixa não aparecer, faltou amostra no recorte atual.")


def render_relacionamento_dinamico(df_filtrado: pd.DataFrame, col: dict[str, str]) -> None:
    """Renderiza uma tabela resumo configurável pelo usuário.

    Args:
        df_filtrado: Base já filtrada conforme a seleção do usuário.
        col: Mapeamento de nomes amigáveis das colunas.
    """
    st.markdown("### Relacionamento dinâmico")
    st.caption(
        "Resumo personalizado: escolha uma coluna para agrupar e outra para calcular."
    )

    opcoes_categoricas = [
        col["ano"],
        col["equipe"],
        col["piloto"],
        col["numero_piloto"],
        col["circuito"],
        col["pais_circuito"],
        col["status"],
        col["nac_piloto"],
        col["nac_equipe"],
    ]
    opcoes_numericas = [
        col["pontos"],
        col["grid"],
        col["chegada"],
        col["ganho"],
        col["mudanca_abs"],
        col["numero_piloto"],
        col["voltas"],
        col["tempo_ms"],
        col["altitude"],
    ]
    opcoes_metricas = {
        "Média": "mean",
        "Mediana": "median",
        "Soma": "sum",
        "Mínimo": "min",
        "Máximo": "max",
        "Desvio padrão": "std",
        "Contagem": "count",
    }

    res1, res2, res3 = st.columns(3, gap="medium")
    agrupador = res1.selectbox("Agrupar por", opcoes_categoricas)
    numerica = res2.selectbox("Calcular sobre", opcoes_numericas)
    metrica_rotulo = res3.selectbox("Operação", list(opcoes_metricas.keys()))

    res4, res5 = st.columns(2, gap="medium")
    ordem = res4.selectbox("Ordenar", ["Decrescente", "Crescente"])
    limite = res5.slider("Quantidade de linhas", min_value=10, max_value=200, value=50, step=10)

    nome_coluna_saida = f"{metrica_rotulo} de {numerica}"
    resumo = (
        df_filtrado.groupby(agrupador, as_index=False)[numerica]
        .agg(opcoes_metricas[metrica_rotulo])
        .rename(columns={numerica: nome_coluna_saida})
        .sort_values(by=nome_coluna_saida, ascending=(ordem == "Crescente"))
        .head(limite)
    )
    st.caption("Tabela resumo gerada com os filtros atuais.")
    st.dataframe(resumo.round(2), use_container_width=True, hide_index=True)


def render_dados_filtrados(df_filtrado: pd.DataFrame, col: dict[str, str]) -> None:
    """Exibe a tabela detalhada de resultados do recorte atual.

    Args:
        df_filtrado: Base já filtrada conforme a seleção do usuário.
        col: Mapeamento de nomes amigáveis das colunas.
    """
    st.divider()
    colunas_exibicao = [
        col["ano"],
        col["rodada"],
        col["gp"],
        col["data"],
        col["piloto"],
        col["equipe"],
        col["circuito"],
        col["grid"],
        col["chegada"],
        col["pontos"],
        col["status"],
        col["ganho"],
    ]
    df_exibicao = df_filtrado[colunas_exibicao].copy().sort_values(
        by=[col["ano"], col["rodada"], col["chegada"]],
        ascending=[False, False, True],
    )
    if pd.api.types.is_datetime64_any_dtype(df_exibicao[col["data"]]):
        df_exibicao[col["data"]] = df_exibicao[col["data"]].dt.date

    with st.expander("Dados filtrados (clique para abrir)", expanded=False):
        st.caption(
            "Cada linha é o resultado de um piloto em uma corrida, considerando os filtros escolhidos."
        )
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
