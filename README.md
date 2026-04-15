# Dashboard F1: Insights de Corrida

Aplicação web para análise exploratória da Fórmula 1 com filtros interativos, KPIs, gráficos focados em insights de impacto e uma aba dedicada para relacionamento dinâmico entre variáveis.

## Estrutura do projeto

- `app.py`: ponto de entrada da aplicação.
- `dashboard/config.py`: caminhos, esquema mínimo dos CSVs F1 e CSS.
- `dashboard/data.py`: leitura das tabelas F1, junções e criação da base analítica.
- `dashboard/filters.py`: filtros da sidebar e aplicação dos filtros.
- `dashboard/components.py`: seções visuais (KPIs, 4 gráficos, relacionamento e tabela final).
- `dashboard/main.py`: orquestração do fluxo principal.
- `dados f1/`: arquivos CSV da base de Fórmula 1.

## Pré-requisitos

- Python 3.10+ (recomendado)
- Suporte a `venv` habilitado no Python
- Internet para instalar dependências (na primeira execução)

## Execução no Windows (PowerShell/CMD)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Execução no Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Observações

- O app lê os arquivos da pasta `dados f1` automaticamente.
- Nesta versão inicial, o dashboard usa as tabelas centrais: `results`, `races`, `drivers`, `constructors`, `circuits` e `status`.
- A aba principal mostra KPIs, 4 gráficos de impacto e os dados filtrados.
- A aba "Relacionamento dinâmico" mantém a análise agregada personalizável.
- Se `streamlit` não for reconhecido como comando, use sempre `python -m streamlit`.
- Se o `venv` não estiver disponível no Linux, instale o pacote equivalente da sua distribuição, como `python3-venv`.
