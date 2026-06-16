import os
from functools import lru_cache
from pathlib import Path


class Settings:
    app_name: str = "Core Banking Lite"
    app_env: str = os.getenv("APP_ENV", "development")
    app_version: str = os.getenv("APP_VERSION", "3.0.0")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
