"""Load and expose application configuration from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-6"

    cv_path: Path = Path("data/cv.md")
    vacancy_path: Path = Path("inbox/vacancy.txt")
    chroma_persist_dir: Path = Path("data/chroma")
    db_path: Path = Path("data/jobs.db")


settings = AppSettings()