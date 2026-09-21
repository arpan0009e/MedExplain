from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "MedExplain API"
    app_version: str = "0.1.0"
    environment: str = "development"

    mongodb_uri: str
    mongodb_database: str = "medexplain"

    gemini_api_key: str
    gemini_model: str = "gemini-3.6-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()