import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "SuperJoin Fact Knowledge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # LLM Settings (Gemini)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'data' / 'fact_knowledge.db'}"
    )

    # Directories
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    STARTER_DATASET_DIR: Path = BASE_DIR / "data" / "starter-datasets"

    # Processing Limits
    MAX_PAGES_TO_PROCESS: int = int(os.getenv("MAX_PAGES_TO_PROCESS", "50"))
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150



settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
