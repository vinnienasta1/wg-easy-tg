from typing import List

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tg_bot_token: str = Field(alias="TG_BOT_TOKEN")
    admins: List[int] = Field(default_factory=list, alias="ADMINS")

    wg_easy_base_url: str = Field(alias="WG_EASY_BASE_URL")
    wg_easy_username: str = Field(default="admin", alias="WG_EASY_USERNAME")
    wg_easy_password: str = Field(alias="WG_EASY_PASSWORD")
    wg_easy_verify_ssl: bool = Field(default=True, alias="WG_EASY_VERIFY_SSL")

    db_path: str = Field(default="./data/bot.db", alias="DB_PATH")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    @field_validator("admins", mode="before")
    @classmethod
    def parse_admins(cls, v):
        if isinstance(v, list):
            return [int(x) for x in v]
        if not v:
            return []
        return [int(x.strip()) for x in str(v).split(",") if x.strip()]


def get_settings() -> Settings:
    # Локально подхватим .env, в контейнере переменные придут из env_file
    load_dotenv()
    return Settings()


settings = get_settings()
