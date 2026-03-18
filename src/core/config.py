from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./model_registry.db"
    storage_path: str = "./artifact_storage"
    api_prefix: str = "/api/v1"

    model_config = {"env_prefix": "REGISTRY_", "env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
