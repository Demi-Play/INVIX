from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


base_dir = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5000

    model_config = SettingsConfigDict(
        env_file=base_dir / ".env",
        env_file_encoding="utf_8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
