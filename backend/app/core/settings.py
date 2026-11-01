from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

base_dir = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5000

    pg_url: str | None = None
    pg_host: str
    pg_port: int
    pg_user: str
    pg_password: str
    pg_db: str

    @property
    def database_url(self) -> str:
        if self.pg_url:
            return self.pg_url
        return URL.create(
            "postgresql+psycopg2",
            username=self.pg_user,
            password=self.pg_password or None,
            host=self.pg_host,
            port=self.pg_port,
            database=self.pg_db,
        ).render_as_string(hide_password=False)

    # origins для CORS через запятую или "*"
    cors_origins: str = "http://127.0.0.1:5000, http://localhost:5000"

    @property
    def cors_origin_list(self) -> list[str]:
        raw = self.cors_origins.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    # MinIO / S3
    # endpoint, по которому backend ходит в MinIO (внутри docker-сети)
    minio_endpoint: str = "localhost:9000"
    # endpoint, который доступен браузеру; используется только для presigned URL
    minio_public_base_url: str = "http://localhost:3000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = "invix"
    minio_region: str = "us-east-1"
    minio_secure: bool = False
    minio_presign_expires_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=base_dir / ".env",
        env_file_encoding="utf_8",
        case_sensitive=False,
        extra="ignore",
    )


# обязательные поля PG_ приходят из env, а не из аргументов конструктора
settings = Settings.settings_cached()
