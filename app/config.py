from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        protected_namespaces=(),
        extra="ignore",
    )

    database_url: str
    model_path: str
    model_metadata_path: str = "artifacts/model_metadata.json"


settings = Settings()
