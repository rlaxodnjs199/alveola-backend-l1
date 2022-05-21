import os
from functools import lru_cache
from pathlib import Path
from pydantic import BaseSettings, Field, PostgresDsn


class Config(BaseSettings):
    service_account_file: str = Field(..., env="SERVICE_ACCOUNT_FILE")
    qctworksheet_id: str = Field(..., env="QCTWORKSHEET_ID")
    p_drive_path_prefix: Path = Field(..., env="PDRIVE_PATH_PREFIX")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevelopmentConfig(Config):
    postgres_dsn: PostgresDsn = Field(..., env="DEV_POSTGRES_URL")


class ProductionConfig(Config):
    postgres_dsn: PostgresDsn = Field(..., env="PROD_POSTGRES_URL")


@lru_cache
def get_config() -> Config:
    env = os.getenv("ENV", "development")
    config_type = {"development": DevelopmentConfig(), "production": ProductionConfig()}

    return config_type[env]


config = get_config()
