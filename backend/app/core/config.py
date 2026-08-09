from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Application
    app_name: str = "Synestra Unified Backend"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    # Frontend origins
    allowed_origins: list[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database and generated files
    synestra_db_path: str | None = None
    generated_files_dir: str | None = None
    separated_files_dir: str | None = None

    # JWT authentication
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "synestra-ai"
    access_token_expire_minutes: int = 60 * 24

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None

    # Password reset
    password_reset_debug: bool = False
    reset_code_expire_minutes: int = 10
    reset_code_cooldown_seconds: int = 60
    reset_code_max_attempts: int = 5

    # Celery & Redis (Composer)
    redis_url: str = "redis://localhost:6379/0"
    celery_task_time_limit: int = 1800
    celery_task_soft_time_limit: int = 1700
    moonbeam_output_dir: str | None = None

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def data_dir(self) -> Path:
        return BACKEND_DIR / "data"

    @property
    def database_path(self) -> Path:
        if self.synestra_db_path:
            path = Path(self.synestra_db_path).expanduser()

            if not path.is_absolute():
                path = BACKEND_DIR / path

            return path.resolve()

        return (self.data_dir / "synestra.db").resolve()

    @property
    def generated_dir(self) -> Path:
        if self.generated_files_dir:
            path = Path(
                self.generated_files_dir
            ).expanduser()

            if not path.is_absolute():
                path = BACKEND_DIR / path

            return path.resolve()

        return (BACKEND_DIR / "generated").resolve()

    @property
    def separated_dir(self) -> Path:
        if self.separated_files_dir:
            path = Path(
                self.separated_files_dir
            ).expanduser()

            if not path.is_absolute():
                path = BACKEND_DIR / path

            return path.resolve()

        return (BACKEND_DIR / "separated").resolve()

    @property
    def composer_output_dir(self) -> Path:
        if self.moonbeam_output_dir:
            path = Path(self.moonbeam_output_dir).expanduser()
            if not path.is_absolute():
                path = BACKEND_DIR / path
            return path.resolve()
        return (BACKEND_DIR / "composer_outputs").resolve()

    @property
    def email_from_address(self) -> str | None:
        return self.smtp_from_email or self.smtp_username


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()