import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from dashboard.config import TABELAS_F1

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dados f1"
DATASET_SLUG = "jtrotman/formula-1-race-data"
DOTENV_PATH = BASE_DIR / ".env"


def _load_env_file() -> None:
    if DOTENV_PATH.exists():
        try:
            from dotenv import load_dotenv
        except ImportError as exc:
            raise RuntimeError(
                "Dependencia 'python-dotenv' nao instalada. "
                "Rode `python -m pip install -r requirements.txt`."
            ) from exc
        load_dotenv(DOTENV_PATH, override=True)


def _configure_kaggle_auth() -> None:
    token = os.getenv("KAGGLE_API_TOKEN", "").strip()

    if token:
        os.environ["KAGGLE_API_TOKEN"] = token
        return

    raise RuntimeError(
        "Credencial Kaggle nao encontrada. Configure `KAGGLE_API_TOKEN` no `.env`."
    )


def _build_kaggle_api():
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError as exc:
        raise RuntimeError(
            "Dependencia 'kaggle' nao instalada. "
            "Rode `python -m pip install -r requirements.txt`."
        ) from exc

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as exc:
        raise RuntimeError(
            "Falha ao autenticar na Kaggle. Verifique se `KAGGLE_API_TOKEN` no `.env` "
            "esta valido e atualizado."
        ) from exc
    return api


def _find_downloaded_zip(download_dir: Path) -> Path:
    zip_files = sorted(download_dir.glob("*.zip"))
    if not zip_files:
        raise RuntimeError("Nenhum arquivo ZIP foi baixado pela API da Kaggle.")
    return zip_files[0]


def _expected_csv_files() -> set[str]:
    return {config["arquivo"] for config in TABELAS_F1.values()}


def update_f1_data() -> None:
    """Baixa e atualiza os arquivos CSV mais recentes do dataset da Kaggle."""
    _load_env_file()
    _configure_kaggle_auth()

    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Baixando dataset {DATASET_SLUG}...")
    api = _build_kaggle_api()

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir = Path(tmp_dir)
        extracted_dir = temp_dir / "extracted"

        api.dataset_download_files(
            DATASET_SLUG,
            path=str(temp_dir),
            force=True,
            unzip=False,
        )

        zip_filename = _find_downloaded_zip(temp_dir)
        print(f"Extraindo {zip_filename.name}...")
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(extracted_dir)

        arquivos_csv = sorted(extracted_dir.rglob("*.csv"))
        if not arquivos_csv:
            raise RuntimeError("O ZIP baixado nao contem arquivos CSV.")

        for csv_path in arquivos_csv:
            shutil.copy2(csv_path, DATA_DIR / csv_path.name)

    ausentes = sorted(
        arquivo for arquivo in _expected_csv_files() if not (DATA_DIR / arquivo).exists()
    )
    if ausentes:
        raise RuntimeError(
            "Atualizacao incompleta. Arquivos obrigatorios ausentes em `dados f1/`: "
            + ", ".join(ausentes)
        )

    print(
        f"Atualizacao concluida. {len(arquivos_csv)} arquivo(s) CSV foram copiados para "
        f"'{DATA_DIR.name}/'."
    )


if __name__ == "__main__":
    update_f1_data()
