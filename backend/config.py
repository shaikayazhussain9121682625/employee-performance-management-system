import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "data"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-only-change-before-production"
    )

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{(DATABASE_DIR / 'employee_performance.db').as_posix()}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False