from pathlib import Path

from app.common.config import settings

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent
DOC_DIR = PROJECT_ROOT_DIR / "doc"
LOG_DIR: Path = PROJECT_ROOT_DIR / "logs"

APP_NAME = settings.APPLICATION_NAME
