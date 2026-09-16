from src.config import load_settings
from src.risk_engine import assess_risk


def _strong_features(
    persistence_seconds: float,
) -> dict:

    cfg = load_settings()["risk"]

    return {
        "turbidity_difference":
            float(
                cfg[
                    "turbidity_difference_critical"
                ]
            ) + 10.0,

        "turbidity_a":
            18.0,

        "turbidity_b":
            95.0,

        "audio_machine_probability_b":
            min(
                1.0,
                float(
                    cfg[
                        "machine_probability_high"
                    ]
                ) + 0.1,
            ),

        "vibration_machinery_probability_b":
            min(
                1.0,
                float(
                    cfg[
                        "vibration_probability_high"
                    ]
                ) + 0.1,
            ),

        "multi_sensor_confirmation_score":
            1.0,

        "persistence_seconds":
            persistence_seconds,
    }


def test_strong_evidence_without_persistence_is_not_critical():
    cfg = load_settings()["risk"]

    result = assess_risk(
        fusion_class=
            "HIGH_RISK_MINING_ACTIVITY",

        confidence=
            max(
                0.95,
                float(
                    cfg[
                        "confidence_minimum"
                    ]
                ),
            ),

        features=
            _strong_features(0.0),

        sensor_health=[
            "HEALTHY",
            "HEALTHY",
        ],
    )

    assert result["risk_level"] == "HIGH"
    assert (
        result["prediction"]
        == "POSSIBLE_MINING_ACTIVITY"
    )
    assert result["persistence_met"] is False


def test_strong_persistent_evidence_can_be_critical():
    cfg = load_settings()["risk"]

    required = float(
        cfg[
            "critical_persistence_seconds"
        ]
    )

    result = assess_risk(
        fusion_class=
            "HIGH_RISK_MINING_ACTIVITY",

        confidence=
            max(
                0.95,
                float(
                    cfg[
                        "confidence_minimum"
                    ]
                ),
            ),

        features=
            _strong_features(
                required + 1.0
            ),

        sensor_health=[
            "HEALTHY",
            "HEALTHY",
        ],
    )

    assert (
        result["risk_level"]
        == "CRITICAL"
    )

    assert (
        result["prediction"]
        == "HIGH_RISK_MINING_ACTIVITY"
    )

    assert result["persistence_met"] is True
