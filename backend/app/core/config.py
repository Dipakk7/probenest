from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Probenest environment and application configuration."""

    APP_NAME: str = "Probenest"
    APP_ENV: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./probenest.db"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
