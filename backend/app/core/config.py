from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NIDS Backend API"
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 720
    database_url: str = "sqlite:///./nids.db"
    model_artifact_path: str = "artifacts/nids_model.joblib"
    default_admin_email: str = "admin@nidsdemo.com"
    default_admin_password: str = "admin123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
