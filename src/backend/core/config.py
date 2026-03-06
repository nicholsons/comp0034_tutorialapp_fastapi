import secrets
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    db_name: str
    db_driver: str
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str
    access_token_expires: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        return f"{self.db_driver}{BASE_DIR}/src/data/{self.db_name}"


settings = Settings()
