from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str = ""
    mini_app_url: str = ""
    backend_url: str = "http://127.0.0.1:5000"
    log_level: str = "INFO"

    # Telegram user id с доступом к админ-функциям (через запятую — несколько)
    admin_ids: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf_8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def admin_id_set(self) -> set[int]:
        if not self.admin_ids.strip():
            return set()
        return {
            int(part.strip())
            for part in self.admin_ids.split(",")
            if part.strip().isdigit()
        }


settings = Settings()
