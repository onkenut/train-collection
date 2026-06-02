import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
DB_PATH = DATA_DIR / "vault.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
    "application/pdf",
    "text/plain", "text/markdown", "text/csv",
    "application/json",
    "application/zip", "application/x-zip-compressed",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


AI_API_KEY = get_env("AI_API_KEY", "")
AI_BASE_URL = get_env("AI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = get_env("AI_MODEL", "gpt-3.5-turbo")
AI_MONTHLY_BUDGET = int(get_env("AI_MONTHLY_BUDGET", "1000000"))
