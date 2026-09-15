from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
import numpy as np
from .config import ROOT, load_settings


class BaselineManager:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.path = ROOT / "data" / "baselines" / f"{node_id}.json"
        self.values = self._load()

    def _load(self) -> dict:
        if self.path.exists(): return json.loads(self.path.read_text(encoding="utf-8"))
        return {"count": 0, "turbidity_ntu": None, "temperature_c": None, "audio_rms": None, "vibration_rms": None}

    def calibrate(self, records: Iterable[dict]) -> dict:
        records = list(records)
        for key, source in [("turbidity_ntu", "turbidity_ntu"), ("temperature_c", "water_temperature_c"), ("audio_rms", "audio_rms"), ("vibration_rms", "vibration_rms")]:
            vals = [float(r[source]) for r in records if r.get(source) is not None and np.isfinite(float(r[source]))]
            self.values[key] = float(np.median(vals)) if vals else None
        self.values["count"] = len(records)
        self.save(); return self.values

    def guarded_update(self, observation: dict, risk_level: str = "LOW") -> None:
        allowed = load_settings()["baseline"]["guarded_update_max_risk"]
        order = {"LOW":0,"MEDIUM":1,"HIGH":2,"CRITICAL":3,"UNKNOWN":4}
        if order.get(risk_level, 4) > order.get(allowed, 0): return
        alpha = float(load_settings()["baseline"]["alpha"])
        mapping = {"turbidity_ntu":"turbidity_ntu", "temperature_c":"water_temperature_c", "audio_rms":"audio_rms", "vibration_rms":"vibration_rms"}
        for base_key, obs_key in mapping.items():
            value = observation.get(obs_key)
            if value is None: continue
            old = self.values.get(base_key)
            self.values[base_key] = float(value) if old is None else (1-alpha)*float(old)+alpha*float(value)
        self.values["count"] = int(self.values.get("count",0))+1
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.values, indent=2), encoding="utf-8")
