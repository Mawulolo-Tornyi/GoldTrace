from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import random
from datetime import datetime, timezone
from typing import Any

import numpy as np

from .config import ROOT, load_settings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def json_safe(value: Any) -> Any:
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def write_json(path: str | Path, payload: Any) -> None:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(json_safe(payload), indent=2), encoding="utf-8")


def setup_logging() -> logging.Logger:
    settings = load_settings()
    cfg = settings.get("logging", {})
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("goldtrace")
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, str(cfg.get("level", "INFO")).upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    for filename, level in [("goldtrace.log", logging.INFO), ("errors.log", logging.ERROR)]:
        handler = RotatingFileHandler(
            log_dir / filename,
            maxBytes=int(cfg.get("max_bytes", 5_000_000)),
            backupCount=int(cfg.get("backup_count", 3)),
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    return logger
