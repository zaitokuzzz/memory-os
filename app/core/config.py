from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "memory-os"
    app_env: str = "development"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/memory_os"
    redis_url: str = "redis://redis:6379/0"

    embedding_model: str = "local-stub"
    embedding_dim: int = 1536

    default_max_context_tokens: int = 1200
    default_top_k: int = 5

    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    archive_provider: str = "local"
    archive_bucket: str = "memory-archive"
    archive_endpoint: str = "http://localhost:9000"
    archive_access_key: str = "minioadmin"
    archive_secret_key: str = "minioadmin"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
