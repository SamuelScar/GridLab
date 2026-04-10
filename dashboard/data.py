from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.config import (
    COLUNAS_NUMERICAS_BASE,
    NACIONALIDADE_PARA_PAIS_PT,
    TABELAS_F1,
    obter_colunas,
)


def _validar_arquivos(pasta_dados: Path) -> None:
    """Valida se os arquivos essenciais da base F1 existem na pasta esperada."""
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
    """Carrega apenas as tabelas e colunas necessárias para o dashboard inicial."""
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


@st.cache_data
def carregar_dados(pasta_dados: Path | str) -> pd.DataFrame:
    """Monta uma base analítica unificada com dados de corrida, piloto e equipe."""
    tabelas = carregar_tabelas_f1(pasta_dados)
    col = obter_colunas()

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

    base[col["ganho"]] = (base["grid"] - base["positionOrder"]).where(base["grid"] > 0)
    base[col["mudanca_abs"]] = (
        (base["positionOrder"] - base["grid"]).abs().where(base["grid"] > 0)
    )
    base[col["concluiu"]] = concluiu
    base[col["abandono"]] = ~base[col["concluiu"]]
    base[col["pontuou"]] = base["points"].fillna(0) > 0

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
