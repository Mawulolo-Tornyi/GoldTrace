from __future__ import annotations
from pathlib import Path
from typing import Any
import os
import yaml
from .config import ROOT, load_settings


class AgencyRegistry:
    def __init__(self, path: str | Path | None = None):
        cfg = load_settings().get('agency_alerts', {})
        p = Path(path or cfg.get('agencies_file', 'config/agencies.example.yaml'))
        self.path = p if p.is_absolute() else ROOT / p

    def list(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        with self.path.open('r', encoding='utf-8') as f:
            agencies = (yaml.safe_load(f) or {}).get('agencies', [])
        out = []
        for a in agencies:
            item = dict(a)
            env_name = f"GOLDTRACE_{str(item.get('id','')).upper()}_PHONE"
            if os.getenv(env_name):
                item['phone'] = os.getenv(env_name)
            if enabled_only and not item.get('enabled', False):
                continue
            out.append(item)
        return out

    def get(self, agency_id: str) -> dict[str, Any] | None:
        for item in self.list(False):
            if item.get('id') == agency_id:
                return item
        return None
