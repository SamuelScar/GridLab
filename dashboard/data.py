"""Carregamento e preparação da base analítica usada no dashboard.

O módulo lê apenas as tabelas e colunas necessárias do dataset de Fórmula 1,
valida a presença dos arquivos esperados e monta um DataFrame unificado pronto
para exploração visual.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.config import (
    COLUNAS_NUMERICAS_BASE,
    NACIONALIDADE_PARA_PAIS_PT,
    TABELAS_F1,
    obter_colunas,
)


INCIDENT_STATUSES = {"Accident", "Collision", "Spun off"}
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


def _validar_arquivos(pasta_dados: Path) -> None:
    """Valida a presença dos arquivos mínimos exigidos pelo dashboard.

    Args:
        pasta_dados: Diretório onde os arquivos CSV da base F1 devem existir.

    Raises:
        FileNotFoundError: Quando pelo menos um dos arquivos configurados em
            `TABELAS_F1` não está disponível na pasta informada.
    """
    ausentes = [
        config["arquivo"]
        for config in TABELAS_F1.values()
        if not (pasta_dados / config["arquivo"]).exists()
    ]
    if ausentes:
        arquivos = ", ".join(sorted(ausentes))
        raise FileNotFoundError(
            f"Arquivos F1 ausentes em `{pasta_dados}`: {arquivos}."
        )


@st.cache_data
def carregar_tabelas_f1(pasta_dados: Path | str) -> dict[str, pd.DataFrame]:
    """Carrega as tabelas brutas necessárias para montar a base analítica.

    Args:
        pasta_dados: Caminho para a pasta que contém os arquivos CSV do dataset.

    Returns:
        Um dicionário indexado pelo nome lógico de cada tabela, contendo os
        DataFrames lidos com as colunas mínimas usadas pelo dashboard.

    Raises:
        FileNotFoundError: Quando a pasta de dados está incompleta.
        pandas.errors.EmptyDataError: Quando algum CSV existe, mas está vazio.
    """
    pasta = Path(pasta_dados)
    _validar_arquivos(pasta)

    tabelas: dict[str, pd.DataFrame] = {}
    for nome_tabela, config in TABELAS_F1.items():
        caminho = pasta / config["arquivo"]
        tabelas[nome_tabela] = pd.read_csv(
            caminho,
            usecols=config["colunas"],
            na_values=["\\N"],
            low_memory=False,
        )
    return tabelas


def _obter_finais_campeonato(
    tabelas: dict[str, pd.DataFrame], col: dict[str, str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extrai a classificação final de pilotos e equipes em cada temporada."""
    corridas = tabelas["races"][["raceId", "year", "round"]].copy()
    ultima_rodada = corridas.groupby("year", as_index=False)["round"].max()
    corridas_finais = corridas.merge(
        ultima_rodada,
        on=["year", "round"],
        how="inner",
    )[["raceId", "year"]]

    driver_final = (
        tabelas["driver_standings"]
        .merge(corridas_finais, on="raceId", how="inner")
        [["year", "driverId", "points", "position"]]
        .rename(
            columns={
                "points": col["pts_campeonato_piloto"],
                "position": col["pos_campeonato_piloto"],
            }
        )
    )

    constructor_final = (
        tabelas["constructor_standings"]
        .merge(corridas_finais, on="raceId", how="inner")
        [["year", "constructorId", "points", "position"]]
        .rename(
            columns={
                "points": col["pts_campeonato_equipe"],
                "position": col["pos_campeonato_equipe"],
            }
        )
    )

    for coluna in [
        col["pts_campeonato_piloto"],
        col["pos_campeonato_piloto"],
        col["pts_campeonato_equipe"],
        col["pos_campeonato_equipe"],
    ]:
        if coluna in driver_final.columns:
            driver_final[coluna] = pd.to_numeric(driver_final[coluna], errors="coerce")
        if coluna in constructor_final.columns:
            constructor_final[coluna] = pd.to_numeric(
                constructor_final[coluna], errors="coerce"
            )

    return driver_final, constructor_final


@st.cache_data
def carregar_dados(pasta_dados: Path | str) -> pd.DataFrame:
    """Monta a base analítica final consumida pela interface.

    A transformação combina resultados de corrida com metadados de provas,
    pilotos, equipes, circuitos e status finais. Também normaliza tipos,
    traduz nacionalidades, cria colunas derivadas e devolve os dados já
    ordenados para uso direto nos componentes visuais.

    Args:
        pasta_dados: Caminho da pasta que contém os CSVs originais.

    Returns:
        DataFrame consolidado com nomes de colunas amigáveis definidos em
        `obter_colunas()`.

    Raises:
        FileNotFoundError: Quando a pasta de dados não contém todos os arquivos
            exigidos para a consolidação.
    """
    tabelas = carregar_tabelas_f1(pasta_dados)
    col = obter_colunas()
    driver_final, constructor_final = _obter_finais_campeonato(tabelas, col)

    results = tabelas["results"].copy()
    races = tabelas["races"].rename(
        columns={"name": "race_name", "date": "race_date"}
    )
    drivers = tabelas["drivers"].rename(
        columns={
            "forename": "driver_forename",
            "surname": "driver_surname",
            "nationality": "driver_nationality",
        }
    )
    constructors = tabelas["constructors"].rename(
        columns={"name": "constructor_name", "nationality": "constructor_nationality"}
    )
    circuits = tabelas["circuits"].rename(
        columns={
            "name": "circuit_name",
            "country": "circuit_country",
            "alt": "alt",
        }
    )
    status = tabelas["status"].rename(columns={"status": "finish_status"})

    base = (
        results.merge(races, on="raceId", how="left")
        .merge(drivers, on="driverId", how="left")
        .merge(constructors, on="constructorId", how="left")
        .merge(circuits, on="circuitId", how="left")
        .merge(status, on="statusId", how="left")
        .merge(driver_final, on=["year", "driverId"], how="left")
        .merge(constructor_final, on=["year", "constructorId"], how="left")
    )

    for coluna in COLUNAS_NUMERICAS_BASE:
        if coluna in base.columns:
            base[coluna] = pd.to_numeric(base[coluna], errors="coerce")

    base["race_date"] = pd.to_datetime(base["race_date"], errors="coerce")
    base["driver_forename"] = base["driver_forename"].fillna("").astype("string").str.strip()
    base["driver_surname"] = base["driver_surname"].fillna("").astype("string").str.strip()
    base["driver_name"] = (
        base["driver_forename"].str.cat(base["driver_surname"], sep=" ").str.strip()
    )
    base["driver_name"] = base["driver_name"].replace("", "Piloto desconhecido")

    status_texto = base["finish_status"].fillna("").astype("string").str.strip()
    concluiu = status_texto.eq("Finished") | status_texto.str.startswith("+")
    incidente = status_texto.isin(INCIDENT_STATUSES)
    falha_mecanica = status_texto.isin(MECHANICAL_FAILURE_STATUSES)
    outra_nao_conclusao = (~concluiu) & (~incidente) & (~falha_mecanica)
    adversidade = incidente | falha_mecanica | outra_nao_conclusao

    base[col["ganho"]] = (base["grid"] - base["positionOrder"]).where(base["grid"] > 0)
    base[col["mudanca_abs"]] = (
        (base["positionOrder"] - base["grid"]).abs().where(base["grid"] > 0)
    )
    base[col["concluiu"]] = concluiu
    base[col["abandono"]] = ~base[col["concluiu"]]
    base[col["pontuou"]] = base["points"].fillna(0) > 0
    base[col["incidente"]] = incidente
    base[col["falha_mecanica"]] = falha_mecanica
    base[col["outra_nao_conclusao"]] = outra_nao_conclusao
    base[col["adversidade"]] = adversidade

    base_analitica = pd.DataFrame(
        {
            col["id_corrida"]: base["raceId"],
            col["ano"]: base["year"],
            col["rodada"]: base["round"],
            col["gp"]: base["race_name"],
            col["data"]: base["race_date"],
            col["piloto"]: base["driver_name"],
            col["nac_piloto"]: base["driver_nationality"],
            col["equipe"]: base["constructor_name"],
            col["nac_equipe"]: base["constructor_nationality"],
            col["circuito"]: base["circuit_name"],
            col["pais_circuito"]: base["circuit_country"],
            col["numero_piloto"]: base["number"],
            col["altitude"]: base["alt"],
            col["grid"]: base["grid"],
            col["chegada"]: base["positionOrder"],
            col["pontos"]: base["points"],
            col["voltas"]: base["laps"],
            col["tempo_ms"]: base["milliseconds"],
            col["status"]: base["finish_status"],
            col["concluiu"]: base[col["concluiu"]],
            col["abandono"]: base[col["abandono"]],
            col["pontuou"]: base[col["pontuou"]],
            col["ganho"]: base[col["ganho"]],
            col["mudanca_abs"]: base[col["mudanca_abs"]],
            col["incidente"]: base[col["incidente"]],
            col["falha_mecanica"]: base[col["falha_mecanica"]],
            col["outra_nao_conclusao"]: base[col["outra_nao_conclusao"]],
            col["adversidade"]: base[col["adversidade"]],
            col["pos_campeonato_piloto"]: base[col["pos_campeonato_piloto"]],
            col["pts_campeonato_piloto"]: base[col["pts_campeonato_piloto"]],
            col["pos_campeonato_equipe"]: base[col["pos_campeonato_equipe"]],
            col["pts_campeonato_equipe"]: base[col["pts_campeonato_equipe"]],
        }
    )

    for coluna in [col["gp"], col["piloto"], col["equipe"], col["circuito"], col["status"]]:
        base_analitica[coluna] = (
            base_analitica[coluna].fillna("Não informado").astype("string").str.strip()
        )

    for coluna in [col["nac_piloto"], col["nac_equipe"], col["pais_circuito"]]:
        base_analitica[coluna] = (
            base_analitica[coluna].fillna("Não informado").astype("string").str.strip()
        )

    base_analitica[col["numero_piloto"]] = pd.to_numeric(
        base_analitica[col["numero_piloto"]], errors="coerce"
    )

    for coluna in [
        col["pos_campeonato_piloto"],
        col["pts_campeonato_piloto"],
        col["pos_campeonato_equipe"],
        col["pts_campeonato_equipe"],
    ]:
        base_analitica[coluna] = pd.to_numeric(base_analitica[coluna], errors="coerce")

    for coluna in [col["nac_piloto"], col["nac_equipe"]]:
        base_analitica[coluna] = (
            base_analitica[coluna]
            .map(NACIONALIDADE_PARA_PAIS_PT)
            .fillna(base_analitica[coluna])
            .astype("string")
        )

    return base_analitica.sort_values(
        by=[col["ano"], col["rodada"], col["chegada"]],
        ascending=[True, True, True],
    ).reset_index(drop=True)
