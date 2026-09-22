from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MedExplain API"
    app_version: str = "0.1.0"
    environment: str = "development"

    # MongoDB
    mongodb_uri: str
    mongodb_database: str = "medexplain"

    # Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-3.6-flash"

    # OpenRouter
    openrouter_api_key: str
    openrouter_model: str = "google/gemma-4-31b-it:free"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()