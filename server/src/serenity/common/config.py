from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---------------------------------------------------
    # Redis
    # ---------------------------------------------------
    redis_host: str = "localhost"
    redis_port: int = 6379

    # ---------------------------------------------------
    # Travel
    # ---------------------------------------------------
    travel_tick_seconds: float = 1

    # ---------------------------------------------------
    # Paths
    # ---------------------------------------------------
    package_dir: Path = Path(__file__).parents[1]
    planetary_config_path: Path = package_dir / "defaults/planet_graph.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
