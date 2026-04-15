"""Ponto de entrada da aplicação.

Este módulo existe para permitir a execução direta do projeto com
`streamlit run app.py`, delegando o fluxo principal para `dashboard.main`.
"""

from dashboard.main import main


if __name__ == "__main__":
    main()
