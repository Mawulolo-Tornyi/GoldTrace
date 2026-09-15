from __future__ import annotations

REQUIRED_LABEL_FIELDS = {
    "event_id", "session_id", "location_id", "node_id", "timestamp", "environment_label",
    "audio_label", "vibration_label", "fusion_label", "verified", "verification_method", "notes",
}


def validate_label_record(record: dict) -> tuple[bool, list[str]]:
    missing = sorted(REQUIRED_LABEL_FIELDS - set(record))
    return (not missing, missing)
