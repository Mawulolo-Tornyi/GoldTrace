from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Any


# ============================================================
# SENSOR HEALTH BITS
# ============================================================

HEALTH_ADS1115 = 1 << 0
HEALTH_AUDIO = 1 << 1
HEALTH_VIBRATION = 1 << 2
HEALTH_TEMPERATURE = 1 << 3
HEALTH_GPS = 1 << 4
HEALTH_BATTERY = 1 << 5


# ============================================================
# ERROR
# ============================================================

class SensorPacketAdapterError(
    ValueError
):
    pass


# ============================================================
# ADAPTED RESULT
# ============================================================

@dataclass(frozen=True)
class AdaptedSensorPacket:
    backend_payload: dict[str, Any]

    field_metadata: dict[str, Any]


# ============================================================
# HELPERS
# ============================================================

def _required_string(
    packet: dict[str, Any],
    key: str,
) -> str:
    value = packet.get(
        key
    )


    if value is None:
        raise SensorPacketAdapterError(
            f"Missing required field: {key}"
        )


    text = str(
        value
    ).strip()


    if not text:
        raise SensorPacketAdapterError(
            f"Empty required field: {key}"
        )


    return text


def _required_int(
    packet: dict[str, Any],
    key: str,
) -> int:
    value = packet.get(
        key
    )


    if isinstance(
        value,
        bool,
    ):
        raise SensorPacketAdapterError(
            f"Invalid integer field: {key}"
        )


    try:
        converted = int(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SensorPacketAdapterError(
            f"Invalid integer field: {key}"
        ) from exc


    return converted


def _optional_float(
    packet: dict[str, Any],
    key: str,
) -> float | None:
    value = packet.get(
        key
    )


    if value is None:
        return None


    try:
        number = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SensorPacketAdapterError(
            f"Invalid numeric field: {key}"
        ) from exc


    if not math.isfinite(
        number
    ):
        raise SensorPacketAdapterError(
            f"Non-finite numeric field: {key}"
        )


    return number


def _optional_positive_int(
    packet: dict[str, Any],
    key: str,
) -> int | None:
    value = packet.get(
        key
    )


    if value is None:
        return None


    if isinstance(
        value,
        bool,
    ):
        raise SensorPacketAdapterError(
            f"Invalid positive integer field: {key}"
        )


    try:
        number = int(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SensorPacketAdapterError(
            f"Invalid positive integer field: {key}"
        ) from exc


    if number <= 0:
        raise SensorPacketAdapterError(
            f"Invalid positive integer field: {key}"
        )


    return number


# ============================================================
# HEALTH MASK
# ============================================================

def decode_sensor_health(
    mask: int,
) -> dict[str, bool]:
    return {
        "ads1115":
            bool(
                mask &
                HEALTH_ADS1115
            ),

        "audio":
            bool(
                mask &
                HEALTH_AUDIO
            ),

        "vibration":
            bool(
                mask &
                HEALTH_VIBRATION
            ),

        "temperature":
            bool(
                mask &
                HEALTH_TEMPERATURE
            ),

        "gps":
            bool(
                mask &
                HEALTH_GPS
            ),

        "battery":
            bool(
                mask &
                HEALTH_BATTERY
            ),
    }


# ============================================================
# PACKET ADAPTER
# ============================================================

def adapt_authenticated_packet(
    packet: dict[str, Any],
    *,
    received_at: datetime | None = None,
    lora_rssi: float | None = None,
    lora_snr: float | None = None,
) -> AdaptedSensorPacket:
    if not isinstance(
        packet,
        dict,
    ):
        raise SensorPacketAdapterError(
            "Authenticated packet must be a dictionary."
        )


    # --------------------------------------------------------
    # PROTOCOL
    # --------------------------------------------------------

    protocol_version = _required_int(
        packet,
        "v",
    )


    if protocol_version != 1:
        raise SensorPacketAdapterError(
            "Unsupported GoldTrace protocol version: "
            f"{protocol_version}"
        )


    # --------------------------------------------------------
    # NODE IDENTITY
    # --------------------------------------------------------

    node_id = _required_string(
        packet,
        "id",
    )


    if node_id not in {
        "NODE_A",
        "NODE_B",
    }:
        raise SensorPacketAdapterError(
            f"Unknown GoldTrace node: {node_id}"
        )


    boot_id = _required_int(
        packet,
        "b",
    )


    sequence_number = _required_int(
        packet,
        "seq",
    )


    uptime_ms = _required_int(
        packet,
        "up",
    )


    if (
        boot_id < 0
        or sequence_number < 0
        or uptime_ms < 0
    ):
        raise SensorPacketAdapterError(
            "Boot, sequence and uptime values cannot be negative."
        )


    # --------------------------------------------------------
    # GATEWAY TIMESTAMP
    # --------------------------------------------------------

    timestamp = (
        received_at
        if received_at is not None
        else datetime.now(
            timezone.utc
        )
    )


    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(
            tzinfo=timezone.utc
        )


    timestamp = timestamp.astimezone(
        timezone.utc
    )


    # --------------------------------------------------------
    # PRIMARY WATER SENSOR
    # --------------------------------------------------------

    turbidity_ntu = _optional_float(
        packet,
        "tu",
    )


    turbidity_voltage = _optional_float(
        packet,
        "tv",
    )


    # --------------------------------------------------------
    # AUDIO FEATURES
    # --------------------------------------------------------

    audio_rms = _optional_float(
        packet,
        "ar",
    )


    audio_peak = _optional_float(
        packet,
        "ap",
    )


    audio_zcr = _optional_float(
        packet,
        "az",
    )


    audio_sample_rate = _optional_positive_int(
        packet,
        "asr",
    )


    # --------------------------------------------------------
    # VIBRATION FEATURES
    # --------------------------------------------------------

    vibration_rms = _optional_float(
        packet,
        "vr",
    )


    vibration_peak = _optional_float(
        packet,
        "vp",
    )


    vibration_sample_rate = _optional_positive_int(
        packet,
        "vsr",
    )


    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    temperature_c = _optional_float(
        packet,
        "tc",
    )


    # --------------------------------------------------------
    # BATTERY
    # --------------------------------------------------------

    battery_voltage = _optional_float(
        packet,
        "bv",
    )


    battery_percent = _optional_float(
        packet,
        "bp",
    )


    if (
        battery_percent is not None
        and not (
            0.0 <=
            battery_percent <=
            100.0
        )
    ):
        raise SensorPacketAdapterError(
            "Battery percentage must be between 0 and 100."
        )


    # --------------------------------------------------------
    # GPS
    # --------------------------------------------------------

    latitude = _optional_float(
        packet,
        "lat",
    )


    longitude = _optional_float(
        packet,
        "lon",
    )


    satellites = _optional_positive_int(
        packet,
        "sat",
    )


    hdop = _optional_float(
        packet,
        "hd",
    )


    if (
        latitude is not None
        and not (
            -90.0 <=
            latitude <=
            90.0
        )
    ):
        raise SensorPacketAdapterError(
            "GPS latitude is outside valid range."
        )


    if (
        longitude is not None
        and not (
            -180.0 <=
            longitude <=
            180.0
        )
    ):
        raise SensorPacketAdapterError(
            "GPS longitude is outside valid range."
        )


    # --------------------------------------------------------
    # HARDWARE HEALTH
    # --------------------------------------------------------

    health_mask = _required_int(
        packet,
        "sh",
    )


    if not (
        0 <=
        health_mask <=
        255
    ):
        raise SensorPacketAdapterError(
            "Sensor health mask is outside valid range."
        )


    health = decode_sensor_health(
        health_mask
    )


    # --------------------------------------------------------
    # PRECOMPUTED SENSOR FEATURES
    # --------------------------------------------------------

    precomputed_features: dict[str, float] = {}


    if audio_rms is not None:
        precomputed_features[
            "audio_rms"
        ] = audio_rms


    if audio_peak is not None:
        precomputed_features[
            "audio_peak"
        ] = audio_peak


    if audio_zcr is not None:
        precomputed_features[
            "audio_zero_crossing_rate"
        ] = audio_zcr


    if vibration_rms is not None:
        precomputed_features[
            "vibration_rms"
        ] = vibration_rms


    if vibration_peak is not None:
        precomputed_features[
            "vibration_peak"
        ] = vibration_peak


    # --------------------------------------------------------
    # BACKEND PAYLOAD
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # We DO NOT manufacture audio_samples or
    # vibration_samples.
    #
    # The ESP32 transmitted compact measurements only.
    #

    backend_payload: dict[str, Any] = {
        "node_id":
            node_id,

        "timestamp":
            timestamp.isoformat(),

        "turbidity_ntu":
            turbidity_ntu,

        "water_temperature_c":
            temperature_c,

        "audio_sample_rate":
            audio_sample_rate,

        "vibration_sample_rate":
            vibration_sample_rate,

        "audio_samples":
            None,

        "vibration_samples":
            None,

        "battery_voltage":
            battery_voltage,

        "lora_rssi":
            (
                float(
                    lora_rssi
                )
                if lora_rssi is not None
                else None
            ),

        "lora_snr":
            (
                float(
                    lora_snr
                )
                if lora_snr is not None
                else None
            ),

        "precomputed_features":
            precomputed_features,
    }


    # --------------------------------------------------------
    # FIELD / AUDIT METADATA
    # --------------------------------------------------------

    field_metadata: dict[str, Any] = {
        "source":
            "FIELD",

        "simulated":
            False,

        "protocol_version":
            protocol_version,

        "node_id":
            node_id,

        "boot_id":
            boot_id,

        "sequence_number":
            sequence_number,

        "uptime_ms":
            uptime_ms,

        "received_at":
            timestamp.isoformat(),

        "sensor_health_mask":
            health_mask,

        "sensor_health":
            health,

        "turbidity_voltage":
            turbidity_voltage,

        "battery_percent":
            battery_percent,

        "gps": {
            "latitude":
                latitude,

            "longitude":
                longitude,

            "satellites":
                satellites,

            "hdop":
                hdop,
        },
    }


    return AdaptedSensorPacket(
        backend_payload=backend_payload,
        field_metadata=field_metadata,
    )
