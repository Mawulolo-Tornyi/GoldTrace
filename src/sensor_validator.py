from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any
import numpy as np

from .config import load_settings
from .schemas import SensorHealth


def _parse_time(value: Any) -> datetime:
    if isinstance(value, datetime): return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def validate_packet(packet: dict[str, Any]) -> dict[str, Any]:
    s = load_settings()["sensors"]
    sampling = load_settings()["sampling"]
    issues: list[str] = []
    health = SensorHealth.HEALTHY
    required = ["node_id", "timestamp"]
    for key in required:
        if not packet.get(key): issues.append(f"missing:{key}")
    try:
        age = (datetime.now(timezone.utc) - _parse_time(packet.get("timestamp"))).total_seconds()
        if age > float(sampling["stale_packet_seconds"]): issues.append("stale_timestamp")
    except Exception:
        issues.append("invalid_timestamp")
    turb = packet.get("turbidity_ntu")
    if turb is None: issues.append("missing:turbidity_ntu")
    elif not math.isfinite(float(turb)) or not s["turbidity_min_ntu"] <= float(turb) <= s["turbidity_max_ntu"]: issues.append("invalid:turbidity_ntu")
    temp = packet.get("water_temperature_c")
    if temp is None: issues.append("missing:water_temperature_c")
    elif not math.isfinite(float(temp)) or not s["temperature_min_c"] <= float(temp) <= s["temperature_max_c"]: issues.append("invalid:temperature")
    expected_audio = int(sampling.get("audio_rate", 16000))
    expected_vibration = int(sampling.get("vibration_rate", 1000))
    audio_rate = packet.get("audio_sample_rate")
    vibration_rate = packet.get("vibration_sample_rate")
    if audio_rate is None or int(audio_rate) <= 0: issues.append("invalid:audio_sample_rate")
    elif int(audio_rate) not in {8000, 16000, 22050}: issues.append("unsupported:audio_sample_rate")
    if vibration_rate is None or int(vibration_rate) <= 0: issues.append("invalid:vibration_sample_rate")
    elif int(vibration_rate) > 10000: issues.append("unsupported:vibration_sample_rate")

    for name, max_len in [("audio_samples", s["max_audio_samples"]), ("vibration_samples", s["max_vibration_samples"])]:
        buf = packet.get(name)
        if buf is not None:
            if len(buf) == 0: issues.append(f"empty:{name}")
            elif len(buf) > max_len: issues.append(f"oversized:{name}")
            else:
                arr = np.asarray(buf, dtype=float)
                if not np.isfinite(arr).all(): issues.append(f"invalid:{name}")
                if arr.size > 8 and np.nanstd(arr) < 1e-9: issues.append(f"frozen:{name}")
                if name == "audio_samples" and np.max(np.abs(arr)) >= 0.999: issues.append("audio_clipping")
    battery = packet.get("battery_voltage")
    if battery is not None and float(battery) < float(s["battery_low_voltage"]): issues.append("battery_low")
    rssi = packet.get("lora_rssi")
    if rssi is not None and float(rssi) < float(s["rssi_degraded_dbm"]): issues.append("poor_signal")
    critical = [i for i in issues if i.startswith(("missing:turbidity", "invalid:turbidity", "empty:audio", "empty:vibration"))]
    if critical: health = SensorHealth.FAILED
    elif issues: health = SensorHealth.DEGRADED
    return {"health": health.value, "issues": issues, "valid": health != SensorHealth.FAILED}
