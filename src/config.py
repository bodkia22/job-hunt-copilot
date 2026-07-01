"""Load and expose application configuration from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import SecretStr

class AppSettings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: SecretStr
    anthropic_model: str = "claude-sonnet-4-6"

    cv_path: Path = Path("data/cv.md")
    vacancy_path: Path = Path("inbox/vacancy.txt")
    chroma_persist_dir: Path = Path("data/chroma")
    db_path: Path = Path("data/jobs.db")
    output_cover_letter_path: Path = Path("output/cover_letter.txt")

settings = AppSettings()