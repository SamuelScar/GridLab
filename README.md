# Dashboard F1: Insights de Corrida

Aplicação web para análise exploratória da Fórmula 1 com filtros interativos, KPIs, gráficos focados em insights de impacto e uma aba dedicada para relacionamento dinâmico entre variáveis.

## Pré-requisitos

- Python 3.11+
- Suporte a `venv` habilitado no Python
- Internet para instalar dependências (na primeira execução)

## Atualização automática dos dados

Esse fluxo é opcional. As dependências dele já ficam no `requirements.txt`, mesmo
que você não use a atualização automática logo de início.

Este projeto pode baixar os arquivos CSV mais recentes diretamente do dataset
`jtrotman/formula-1-race-data` no Kaggle.

Passos básicos:

1. Instale as dependências do projeto:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Configure sua autenticação Kaggle usando o arquivo de exemplo:
   - Copie o arquivo de exemplo para `.env`:
     ```bash
     cp .env.example .env
     ```
   - Abra `.env` e substitua `KGAT_<seu_token>` pelo seu token real do Kaggle.
   - O script dá prioridade ao `.env` da raiz do projeto.
3. Execute o script de atualização:
   ```bash
   python update_data.py
   ```

Isso usa a API do Kaggle e copia os CSVs mais recentes para a pasta `dados f1/`.

### Se você não quiser usar o Kaggle automaticamente

Nesse caso, baixe o ZIP manualmente do dataset no Kaggle e extraia o conteúdo de CSV para `dados f1/`.

## Execução no Windows (PowerShell)

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

## Limpeza para rodar do zero

Use os comandos abaixo se quiser recriar o ambiente do projeto do zero.
Eles removem o ambiente virtual e arquivos temporários de Python, mas não apagam a pasta `dados f1`.

### Windows (PowerShell)

```powershell
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }
Get-ChildItem -Directory -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -File -Recurse -Include *.pyc,*.pyo | Remove-Item -Force
```

### Linux

```bash
rm -rf .venv
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
```

## Observações

- O app lê os arquivos da pasta `dados f1` automaticamente.
- `update_data.py` é opcional, mas as dependências dele já fazem parte de `requirements.txt`.
- Nesta versão inicial, o dashboard usa as tabelas centrais: `results`, `races`, `drivers`, `constructors`, `circuits` e `status`.
- A aba principal mostra KPIs, 4 gráficos de impacto e os dados filtrados.
- A aba "Relacionamento dinâmico" mantém a análise agregada personalizável.
- Se `streamlit` não for reconhecido como comando, use sempre `python -m streamlit`.
- Se o `venv` não estiver disponível no Linux, instale o pacote equivalente da sua distribuição, como `python3-venv`.
