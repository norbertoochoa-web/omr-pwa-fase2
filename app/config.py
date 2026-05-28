from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "OMR PWA API - Fase 2"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

    POSTGRES_USER: str = "omr_user"
    POSTGRES_PASSWORD: str = "omr_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "omr_pwa"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "f3a8c9e1b7d24f5690ab12cd34ef56789012abcd3456ef78901234567890abcd"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 12

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "omr@imax.cl"

    DEFAULT_ANSWERS_IN_ORDER: list[str] = [
        "A", "B", "C", "D", "E", "A", "A", "A", "A", "A",
        "A", "A", "A", "A", "A", "A", "A", "A", "A", "A",
        "A", "A", "A", "A", "A", "A", "A", "A", "A", "A",
        "A", "A", "A", "A", "A", "A", "A", "A", "A", "A",
        "A", "A", "A", "A", "A", "A", "A", "A", "A", "A",
        "A", "A", "A", "A", "A", "A", "A", "A", "A", "A",
    ]

    API_V1_PREFIX: str = "/api/v1"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
