from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .config import load_settings


def _dt(value: Any) -> datetime:
    if isinstance(value, datetime): return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    d = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def synchronize_packets(a: dict, b: dict, tolerance_seconds: float | None = None) -> dict:
    tolerance = tolerance_seconds or float(load_settings()["sampling"]["synchronization_tolerance_seconds"])
    delta = abs((_dt(a["timestamp"]) - _dt(b["timestamp"])).total_seconds())
    return {"synchronized": delta <= tolerance, "delta_seconds": delta, "quality": max(0.0, 1.0 - delta / max(tolerance, 1e-6))}
