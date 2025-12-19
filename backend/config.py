"""
Configuration management for F1 Sculpture Gallery.
Uses pydantic-settings for environment variable loading and validation.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_worker_concurrency: int = 2

    # FastF1 Configuration
    fastf1_cache_dir: str = "/tmp/fastf1_cache"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:80"]

    # Cache TTL (seconds)
    sculpture_cache_ttl: int = 86400  # 24 hours
    session_cache_ttl: int = 86400    # 24 hours
    task_result_ttl: int = 3600       # 1 hour

    # WebSocket Configuration
    ws_heartbeat_interval: int = 30
    ws_max_connections: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Allow environment variables to override settings
        env_prefix = ""


# Global settings instance
settings = Settings()


def setup_fastf1_cache():
    """Initialize FastF1 cache directory."""
    import fastf1

    cache_dir = settings.fastf1_cache_dir
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)

    return cache_dir
