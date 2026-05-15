"""Application configuration loaded from .env."""

from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


load_dotenv(ENV_PATH)


def build_path(raw_path):
    """Return absolute path from .env value or relative project path."""
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return BASE_DIR / path


def get_config():
    """Return application settings as a dictionary."""
    db_path = build_path(os.getenv("DB_PATH", "data/collectlog.sqlite"))
    backup_dir = build_path(os.getenv("BACKUP_DIR", "backups"))
    export_dir = build_path(os.getenv("EXPORT_DIR", "exports"))
    log_file = build_path(os.getenv("LOG_FILE", "app.log"))
    currency = os.getenv("DEFAULT_CURRENCY", "RUB")

    return {
        "db_path": db_path,
        "backup_dir": backup_dir,
        "export_dir": export_dir,
        "log_file": log_file,
        "currency": currency,
    }


def ensure_directories(config):
    """Create required application directories."""
    config["db_path"].parent.mkdir(parents=True, exist_ok=True)
    config["backup_dir"].mkdir(parents=True, exist_ok=True)
    config["export_dir"].mkdir(parents=True, exist_ok=True)
    config["log_file"].parent.mkdir(parents=True, exist_ok=True)
