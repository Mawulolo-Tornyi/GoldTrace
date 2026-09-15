from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
import math


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class PredictionClass(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS_ENVIRONMENTAL_CHANGE = "SUSPICIOUS_ENVIRONMENTAL_CHANGE"
    MACHINERY_ACTIVITY = "MACHINERY_ACTIVITY"
    POSSIBLE_MINING_ACTIVITY = "POSSIBLE_MINING_ACTIVITY"
    HIGH_RISK_MINING_ACTIVITY = "HIGH_RISK_MINING_ACTIVITY"
    SYSTEM_UNCERTAIN = "SYSTEM_UNCERTAIN"


class SensorHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class NodePacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: str
    timestamp: datetime
    turbidity_raw: float | None = None
    turbidity_ntu: float | None = None
    water_temperature_c: float | None = None
    audio_samples: list[float] | None = None
    audio_sample_rate: int | None = None
    vibration_samples: list[float] | None = None
    vibration_sample_rate: int | None = None
    battery_voltage: float | None = None
    lora_rssi: float | None = None
    lora_snr: float | None = None
    precomputed_features: dict[str, float] | None = None

    @field_validator("audio_samples", "vibration_samples")
    @classmethod
    def finite_buffers(cls, value: list[float] | None) -> list[float] | None:
        if value is None:
            return value
        if any(not math.isfinite(float(x)) for x in value):
            raise ValueError("signal buffer contains NaN or infinity")
        return value


class NodeResult(BaseModel):
    environment: str
    audio: str
    vibration: str
    audio_machine_probability: float = 0.0
    vibration_machinery_probability: float = 0.0
    health: SensorHealth = SensorHealth.UNKNOWN
    turbidity_ntu: float | None = None


class PredictionResult(BaseModel):
    event_id: str | None = None
    timestamp: str
    prediction: PredictionClass
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    suspected_zone: str
    node_results: dict[str, NodeResult]
    evidence: dict[str, Any] = Field(default_factory=dict)
    top_factors: list[dict[str, Any]] = Field(default_factory=list)
    recommendation: str = "Continue monitoring."
