import logging
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---------------------------------------------------
    # Startup parameters
    # ---------------------------------------------------
    restore_persisted_state: bool = False
    log_level: int = logging.DEBUG

    # ---------------------------------------------------
    # CORS
    # ---------------------------------------------------
    cors_origins: list = ["*"]

    # ---------------------------------------------------
    # Redis
    # ---------------------------------------------------
    redis_host: str = "localhost"
    redis_port: int = 6379

    # ---------------------------------------------------
    # Travel
    # ---------------------------------------------------
    travel_tick_seconds: float = 0.3

    # ---------------------------------------------------
    # Paths
    # ---------------------------------------------------
    package_dir: Path = Path(__file__).parents[1]
    planetary_config_path: Path = package_dir / "defaults/planet_graph.json"

    class Config:
        env_prefix = "serenity_"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
