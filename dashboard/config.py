from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "dados f1"

TABELAS_F1 = {
    "results": {
        "arquivo": "results.csv",
        "colunas": [
            "raceId",
            "driverId",
            "constructorId",
            "number",
            "grid",
            "positionOrder",
            "points",
            "laps",
            "milliseconds",
            "statusId",
        ],
    },
    "races": {
        "arquivo": "races.csv",
        "colunas": ["raceId", "year", "round", "circuitId", "name", "date"],
    },
    "drivers": {
        "arquivo": "drivers.csv",
        "colunas": ["driverId", "forename", "surname", "nationality"],
    },
    "constructors": {
        "arquivo": "constructors.csv",
        "colunas": ["constructorId", "name", "nationality"],
    },
    "circuits": {
        "arquivo": "circuits.csv",
        "colunas": ["circuitId", "name", "country", "alt"],
    },
    "status": {"arquivo": "status.csv", "colunas": ["statusId", "status"]},
}

COLUNAS_NUMERICAS_BASE = [
    "grid",
    "number",
    "positionOrder",
    "points",
    "laps",
    "milliseconds",
    "year",
    "round",
    "alt",
]

NACIONALIDADE_PARA_PAIS_PT = {
    "American": "Estados Unidos",
    "American-Italian": "Estados Unidos/Itália",
    "Argentine": "Argentina",
    "Argentine-Italian": "Argentina/Itália",
    "Argentinian": "Argentina",
    "Australian": "Austrália",
    "Austrian": "Áustria",
    "Belgian": "Bélgica",
    "Brazilian": "Brasil",
    "British": "Reino Unido",
    "Canadian": "Canadá",
    "Chilean": "Chile",
    "Chinese": "China",
    "Colombian": "Colômbia",
    "Czech": "Tchéquia",
    "Danish": "Dinamarca",
    "Dutch": "Países Baixos",
    "East German": "Alemanha Oriental",
    "Finnish": "Finlândia",
    "French": "França",
    "German": "Alemanha",
    "Hong Kong": "Hong Kong",
    "Hungarian": "Hungria",
    "Indian": "Índia",
    "Indonesian": "Indonésia",
    "Irish": "Irlanda",
    "Italian": "Itália",
    "Japanese": "Japão",
    "Liechtensteiner": "Liechtenstein",
    "Malaysian": "Malásia",
    "Mexican": "México",
    "Monegasque": "Mônaco",
    "New Zealander": "Nova Zelândia",
    "Polish": "Polônia",
    "Portuguese": "Portugal",
    "Rhodesian": "Rodésia",
    "Russian": "Rússia",
    "South African": "África do Sul",
    "Spanish": "Espanha",
    "Swedish": "Suécia",
    "Swiss": "Suíça",
    "Thai": "Tailândia",
    "Uruguayan": "Uruguai",
    "Venezuelan": "Venezuela",
}

CSS_PERSONALIZADO = """
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
h1, h2, h3 {letter-spacing: -0.01em;}
div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 14px;
    padding: 12px;
    box-shadow: 0 1px 6px rgba(15, 23, 42, 0.06);
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] p,
div[data-testid="stMetric"] div {
    color: var(--text-color) !important;
}
div[data-testid="stMetricLabel"] p {font-size: 0.82rem !important; opacity: 0.85;}
div[data-testid="stMetricValue"] {font-size: 1.35rem; font-weight: 700;}
</style>
"""


def obter_colunas() -> dict[str, str]:
    """Retorna os nomes amigáveis usados no dashboard."""
    return {
        "id_corrida": "ID da corrida",
        "ano": "Ano",
        "rodada": "Rodada",
        "gp": "Grande Prêmio",
        "data": "Data da corrida",
        "piloto": "Piloto",
        "nac_piloto": "País do piloto",
        "equipe": "Equipe",
        "nac_equipe": "País da equipe",
        "circuito": "Circuito",
        "pais_circuito": "País do circuito",
        "numero_piloto": "Número do piloto",
        "altitude": "Altitude do circuito (m)",
        "grid": "Posição de largada",
        "chegada": "Posição final",
        "pontos": "Pontos",
        "voltas": "Voltas completadas",
        "tempo_ms": "Tempo oficial (ms)",
        "status": "Status de chegada",
        "concluiu": "Concluiu a prova",
        "abandono": "Abandono",
        "pontuou": "Pontuou",
        "ganho": "Posições ganhas",
        "mudanca_abs": "Mudança absoluta de posição",
    }
