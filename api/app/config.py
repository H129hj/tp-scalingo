from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toute la configuration vient de l'environnement (Twelve-Factor)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(default="", validation_alias="DATABASE_URL")
    scalingo_postgresql_url: str = Field(default="", validation_alias="SCALINGO_POSTGRESQL_URL")
    secret_key: str = Field(default="", validation_alias="SECRET_KEY")
    cors_origins: str = Field(default="http://localhost:5173", validation_alias="CORS_ORIGINS")
    access_token_minutes: int = Field(default=60, validation_alias="ACCESS_TOKEN_MINUTES")

    @property
    def sqlalchemy_url(self) -> str:
        """Priorite a l'addon Scalingo ; normalise le schema pour SQLAlchemy + psycopg 3."""
        url = self.scalingo_postgresql_url or self.database_url
        if not url:
            raise RuntimeError("DATABASE_URL ou SCALINGO_POSTGRESQL_URL est requis")
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
