from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "settings.yaml"


@lru_cache(maxsize=4)
def load_settings(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Load project configuration from YAML."""
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path
