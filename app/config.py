from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    service_account_file: str = Field(..., env="SERVICE_ACCOUNT_FILE")
    spreadsheetId: str = Field(..., env="SPREADSHEET_ID")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()
