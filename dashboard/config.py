"""Configurações centrais compartilhadas pelo dashboard.

Este módulo concentra caminhos, metadados do dataset, mapeamentos de
nacionalidade e nomes amigáveis das colunas para manter a aplicação consistente
e evitar valores literais espalhados pela base.
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "dados f1"

# Tabelas brutas necessárias para construir a base analítica e suas colunas.
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
    "driver_standings": {
        "arquivo": "driver_standings.csv",
        "colunas": ["raceId", "driverId", "points", "position"],
    },
    "constructor_standings": {
        "arquivo": "constructor_standings.csv",
        "colunas": ["raceId", "constructorId", "points", "position"],
    },
}

# Colunas convertidas explicitamente para tipos numéricos na carga inicial.
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

# Traduções de nacionalidade em inglês para país em português exibido na UI.
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

# Ajustes visuais globais aplicados à interface da aplicação.
CSS_PERSONALIZADO = """
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
h1, h2, h3 {letter-spacing: 0;}
h1 {
    font-size: 2.35rem;
    line-height: 1.12;
    margin-bottom: 0.2rem;
}
.analysis-context {
    display: grid;
    grid-template-columns: minmax(0, 0.9fr) minmax(340px, 1.1fr);
    gap: 1.5rem;
    align-items: start;
    margin: 1.55rem 0 0.8rem;
    padding: 1.1rem 0;
    border-top: 1px solid rgba(148, 163, 184, 0.28);
    border-bottom: 1px solid rgba(148, 163, 184, 0.28);
}
.analysis-context__eyebrow {
    margin: 0 0 0.45rem;
    color: #FF4B4B;
    font-size: 0.76rem;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
}
.analysis-context h2 {
    margin: 0;
    font-size: 1.55rem;
    line-height: 1.2;
}
.analysis-context__intro p:not(.analysis-context__eyebrow) {
    margin: 0.65rem 0 0;
    color: var(--text-color);
    font-size: 0.98rem;
    line-height: 1.45;
    opacity: 0.78;
}
.analysis-context__facts {
    display: grid;
    gap: 0.75rem;
}
.analysis-context__fact {
    padding-left: 0.85rem;
    border-left: 3px solid rgba(255, 75, 75, 0.7);
}
.analysis-context__fact span {
    display: block;
    color: #FF4B4B;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
}
.analysis-context__fact p {
    margin: 0.2rem 0 0;
    color: var(--text-color);
    font-size: 0.95rem;
    line-height: 1.4;
    opacity: 0.84;
}
.analysis-choice {
    max-width: 620px;
    margin: 1.25rem auto 0.8rem;
    text-align: center;
}
.analysis-choice__eyebrow {
    margin: 0 0 0.4rem;
    color: #FF4B4B;
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
}
.analysis-choice h2 {
    margin: 0;
    color: var(--text-color);
    font-size: 1.7rem;
    line-height: 1.15;
}
.analysis-choice__subtitle {
    margin: 0.55rem auto 0;
    max-width: 580px;
    color: var(--text-color);
    font-size: 0.98rem;
    line-height: 1.5;
    opacity: 0.68;
}
@media (max-width: 760px) {
    .analysis-context {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
}
div[data-testid="stButtonGroup"] {
    display: flex;
    justify-content: center;
}
div[data-testid="stButtonGroup"] [data-baseweb="button-group"] {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: min(100%, 500px) !important;
    margin: 0 auto !important;
    padding: 0.35rem;
    gap: 0.6rem;
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 8px;
    background: rgba(148, 163, 184, 0.08);
}
div[data-testid="stButtonGroup"] [data-baseweb="button-group"] button {
    width: 100% !important;
    min-height: 3.35rem;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    font-size: 1.08rem !important;
    font-weight: 750 !important;
    color: var(--text-color) !important;
}
div[data-testid="stButtonGroup"] [data-baseweb="button-group"] button[aria-checked="true"] {
    border-color: #FF4B4B !important;
    background: #FF4B4B !important;
    color: #FFFFFF !important;
    box-shadow: 0 8px 20px rgba(255, 75, 75, 0.24);
}
div[data-testid="stButtonGroup"] [data-baseweb="button-group"] button[aria-checked="false"]:hover {
    border-color: rgba(255, 75, 75, 0.45) !important;
    background: rgba(255, 75, 75, 0.08) !important;
}
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
    """Retorna os nomes amigáveis usados na base analítica e na interface.

    Returns:
        Dicionário que padroniza os identificadores lógicos das colunas
        utilizadas ao longo do projeto.
    """
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
        "incidente": "Incidente",
        "falha_mecanica": "Falha mecânica",
        "outra_nao_conclusao": "Outra não conclusão",
        "adversidade": "Adversidade",
        "pos_campeonato_piloto": "Posição final do piloto no campeonato",
        "pts_campeonato_piloto": "Pontos finais do piloto na temporada",
        "pos_campeonato_equipe": "Posição final da equipe no campeonato",
        "pts_campeonato_equipe": "Pontos finais da equipe na temporada",
    }
