from __future__ import annotations

import math

from typing import (
    Any,
)


EDGE_RUNTIME = (
    "edge_summary_heuristic"
)


class HardwareFeatureError(
    ValueError
):
    pass


def _finite_float(
    features: dict[str, Any],
    key: str,
) -> float:
    if key not in features:
        raise HardwareFeatureError(
            f"Missing hardware feature: {key}"
        )


    try:
        value = float(
            features[key]
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise HardwareFeatureError(
            f"Invalid hardware feature: {key}"
        ) from exc


    if not math.isfinite(
        value
    ):
        raise HardwareFeatureError(
            f"Non-finite hardware feature: {key}"
        )


    return value


def _baseline_value(
    baseline: dict[str, Any] | None,
    key: str,
) -> float | None:
    if not baseline:
        return None


    value = baseline.get(
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
    ):
        return None


    if (
        not math.isfinite(
            number
        )
        or number <= 0.0
    ):
        return None


    return number


def _ratio_score(
    current: float,
    baseline: float,
    *,
    start_ratio: float,
    full_ratio: float,
) -> float:
    ratio = (
        current /
        max(
            baseline,
            1e-12,
        )
    )


    if (
        ratio <= start_ratio
    ):
        return 0.0


    if (
        ratio >= full_ratio
    ):
        return 1.0


    return (
        ratio -
        start_ratio
    ) / (
        full_ratio -
        start_ratio
    )


def is_summary_packet(
    packet: dict[str, Any],
) -> bool:
    features = packet.get(
        "precomputed_features"
    )


    if not isinstance(
        features,
        dict,
    ):
        return False


    audio_samples = packet.get(
        "audio_samples"
    )


    vibration_samples = packet.get(
        "vibration_samples"
    )


    return (
        audio_samples is None
        and vibration_samples is None
    )


def predict_audio_summary(
    features: dict[str, Any],
    baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    rms = _finite_float(
        features,
        "audio_rms",
    )


    peak = _finite_float(
        features,
        "audio_peak",
    )


    zcr = _finite_float(
        features,
        "audio_zero_crossing_rate",
    )


    base_rms = _baseline_value(
        baseline,
        "audio_rms",
    )


    result_features = {
        "audio_rms":
            rms,

        "audio_peak":
            peak,

        "audio_zero_crossing_rate":
            zcr,
    }


    if base_rms is None:
        return {
            "audio_class":
                "UNKNOWN_AUDIO",

            "confidence":
                0.20,

            "machine_probability":
                0.0,

            "probabilities": {
                "UNKNOWN_AUDIO":
                    1.0,
            },

            "features":
                result_features,

            "runtime":
                EDGE_RUNTIME,

            "baseline_ready":
                False,
        }


    score = _ratio_score(
        rms,
        base_rms,
        start_ratio=1.5,
        full_ratio=4.5,
    )



    if (
        score >= 0.65
    ):
        label = (
            "UNKNOWN_MACHINE"
        )
    else:
        label = (
            "NORMAL_ENVIRONMENT"
        )


    # Summary telemetry contains much less evidence
    # than a complete waveform.
    #
    # Confidence is deliberately capped so this path
    # cannot masquerade as full signal classification.

    confidence = min(
        0.60,
        0.40 +
        abs(
            score -
            0.5
        ) *
        0.30,
    )


    return {
        "audio_class":
            label,

        "confidence":
            float(
                confidence
            ),

        "machine_probability":
            float(
                score
            ),

        "probabilities": {
            label:
                float(
                    confidence
                ),
        },

        "features":
            result_features,

        "runtime":
            EDGE_RUNTIME,

        "baseline_ready":
            True,
    }


def predict_vibration_summary(
    features: dict[str, Any],
    baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    rms = _finite_float(
        features,
        "vibration_rms",
    )


    peak = _finite_float(
        features,
        "vibration_peak",
    )


    base_rms = _baseline_value(
        baseline,
        "vibration_rms",
    )


    result_features = {
        "vibration_rms":
            rms,

        "vibration_peak":
            peak,
    }


    if base_rms is None:
        return {
            "vibration_class":
                "UNKNOWN_VIBRATION",

            "confidence":
                0.20,

            "machinery_probability":
                0.0,

            "probabilities": {
                "UNKNOWN_VIBRATION":
                    1.0,
            },

            "features":
                result_features,

            "runtime":
                EDGE_RUNTIME,

            "baseline_ready":
                False,
        }


    score = _ratio_score(
        rms,
        base_rms,
        start_ratio=1.5,
        full_ratio=5.0,
    )


    if (
        score >= 0.65
    ):
        label = (
            "HEAVY_MACHINERY"
        )
    else:
        label = (
            "NORMAL_GROUND"
        )


    confidence = min(
        0.60,
        0.40 +
        abs(
            score -
            0.5
        ) *
        0.30,
    )


    return {
        "vibration_class":
            label,

        "confidence":
            float(
                confidence
            ),

        "machinery_probability":
            float(
                score
            ),

        "probabilities": {
            label:
                float(
                    confidence
                ),
        },

        "features":
            result_features,

        "runtime":
            EDGE_RUNTIME,

        "baseline_ready":
            True,
    }
