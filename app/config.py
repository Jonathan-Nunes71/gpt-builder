"""Utilities for loading settings from TOML and environment variables."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import tomllib
from pydantic import BaseSettings

from app.models.config import Settings


class EnvironmentSettings(BaseSettings):
    """Environment overrides for runtime behaviour."""

    scrape_rate: float = 0.5
    max_concurrency: int = 8
    output_path: str = "data/output"
    http_proxy: str | None = None
    log_level: str = "INFO"
    database_url: str = "sqlite:///data/scraping.db"

    class Config:
        env_prefix = ""
        case_sensitive = False


def load_settings(path: str | Path | None = None) -> Settings:
    """Load settings from TOML and return the validated configuration."""

    if path is None:
        path = Path("configs/settings.toml")
    else:
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Impossible de lire la configuration: {path!s}")

    with path.open("rb") as handle:
        data: Dict[str, Any] = tomllib.load(handle)

    settings = Settings(**data, settings_path=path)
    return settings


def load_environment() -> EnvironmentSettings:
    """Load environment variables with sensible defaults."""

    return EnvironmentSettings(_env_file=os.environ.get("ENV_FILE"))
