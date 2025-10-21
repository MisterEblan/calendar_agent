"""Конфигурация приложения"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    """Конфигурация приложения"""
    database_url: str
    telegram_bot_token: str
    my_username: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

app_config = AppSettings()
