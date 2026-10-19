from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: Literal["demo", "full"] = "demo"
    app_host: str = "127.0.0.1"
    app_port: int = 8103
    database_url: str = "sqlite:///./data/finetuning_demo.db"
    data_dir: Path = Path("data")
    output_dir: Path = Path("outputs")


@lru_cache
def get_settings() -> Settings:
    return Settings()
