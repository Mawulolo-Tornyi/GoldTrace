from __future__ import annotations

from .config import load_settings


CLASS_RISK = {
    "SAFE": "LOW",
    "SUSPICIOUS_ENVIRONMENTAL_CHANGE": "MEDIUM",
    "MACHINERY_ACTIVITY": "MEDIUM",
    "POSSIBLE_MINING_ACTIVITY": "HIGH",
    "HIGH_RISK_MINING_ACTIVITY": "CRITICAL",
    "SYSTEM_UNCERTAIN": "UNKNOWN",
}


def assess_risk(
    fusion_class: str,
    confidence: float,
    features: dict,
    sensor_health: list[str],
) -> dict:

    cfg = load_settings()["risk"]

    critical_persistence = float(
        cfg["critical_persistence_seconds"]
    )

    # --------------------------------------------------------
    # SENSOR HEALTH
    # --------------------------------------------------------

    if not sensor_health:
        return {
            "prediction": "SYSTEM_UNCERTAIN",
            "risk_level": "UNKNOWN",
            "reasons": [
                "Insufficient healthy sensor coverage"
            ],
            "persistence_met": False,
            "required_persistence_seconds":
                critical_persistence,
        }

    healthy_count = sum(
        health in {"HEALTHY", "DEGRADED"}
        for health in sensor_health
    )

    healthy_fraction = (
        healthy_count / len(sensor_health)
    )

    minimum_healthy_fraction = (
        1.0
        - float(
            cfg["uncertain_sensor_fraction"]
        )
    )

    if (
        healthy_fraction
        < minimum_healthy_fraction
    ):
        return {
            "prediction": "SYSTEM_UNCERTAIN",
            "risk_level": "UNKNOWN",
            "reasons": [
                "Insufficient healthy sensor coverage"
            ],
            "persistence_met": False,
            "required_persistence_seconds":
                critical_persistence,
        }

    # --------------------------------------------------------
    # INPUT FEATURES
    # --------------------------------------------------------

    turbidity_difference = float(
        features.get(
            "turbidity_difference",
            0.0,
        )
        or 0.0
    )

    turbidity_a = float(
        features.get(
            "turbidity_a",
            0.0,
        )
        or 0.0
    )

    turbidity_b = float(
        features.get(
            "turbidity_b",
            0.0,
        )
        or 0.0
    )

    audio_probability = float(
        features.get(
            "audio_machine_probability_b",
            0.0,
        )
        or 0.0
    )

    vibration_probability = float(
        features.get(
            "vibration_machinery_probability_b",
            0.0,
        )
        or 0.0
    )

    persistence_seconds = float(
        features.get(
            "persistence_seconds",
            0.0,
        )
        or 0.0
    )

    confirmation_score = float(
        features.get(
            "multi_sensor_confirmation_score",
            0.0,
        )
        or 0.0
    )

    # --------------------------------------------------------
    # THRESHOLD CHECKS
    # --------------------------------------------------------

    strong_turbidity = (
        turbidity_difference
        >= float(
            cfg[
                "turbidity_difference_critical"
            ]
        )
    )

    elevated_turbidity = (
        turbidity_difference
        >= float(
            cfg[
                "turbidity_difference_high"
            ]
        )
    )

    strong_audio = (
        audio_probability
        >= float(
            cfg[
                "machine_probability_high"
            ]
        )
    )

    strong_vibration = (
        vibration_probability
        >= float(
            cfg[
                "vibration_probability_high"
            ]
        )
    )

    confidence_ok = (
        float(confidence)
        >= float(
            cfg["confidence_minimum"]
        )
    )

    persistence_met = (
        persistence_seconds
        >= critical_persistence
    )

    # Some older callers/tests do not provide
    # multi_sensor_confirmation_score.
    #
    # In that case, derive agreement from the
    # independent turbidity/audio/vibration signals.

    derived_agreeing_signals = sum([
        int(strong_turbidity),
        int(strong_audio),
        int(strong_vibration),
    ])

    multi_sensor_confirmed = (
        confirmation_score >= 0.66
        or derived_agreeing_signals >= 3
    )

    # --------------------------------------------------------
    # CRITICAL
    #
    # CRITICAL requires strong independent evidence,
    # confidence, sensor health and persistence.
    # --------------------------------------------------------

    critical_evidence = (
        strong_turbidity
        and strong_audio
        and strong_vibration
        and multi_sensor_confirmed
        and confidence_ok
    )

    if (
        critical_evidence
        and persistence_met
    ):
        return {
            "prediction":
                "HIGH_RISK_MINING_ACTIVITY",

            "risk_level":
                "CRITICAL",

            "reasons": [
                "Strong downstream turbidity increase",
                "Machine-like acoustic signature",
                "Heavy machinery vibration",
                "Abnormal conditions persisted",
                "Multiple sensors agree",
            ],

            "persistence_met":
                True,

            "required_persistence_seconds":
                critical_persistence,
        }

    # --------------------------------------------------------
    # HIGH / PRE-CRITICAL
    #
    # Same strong evidence, but insufficient persistence.
    # --------------------------------------------------------

    if critical_evidence:
        return {
            "prediction":
                "POSSIBLE_MINING_ACTIVITY",

            "risk_level":
                "HIGH",

            "reasons": [
                "Strong downstream turbidity increase",
                "Machine-like acoustic signature",
                "Heavy machinery vibration",
                "Multiple sensors agree",
                (
                    "Persistence threshold not yet met "
                    f"({persistence_seconds:.1f}/"
                    f"{critical_persistence:.1f} seconds)"
                ),
            ],

            "critical_candidate":
                True,

            "persistence_met":
                False,

            "required_persistence_seconds":
                critical_persistence,
        }

    # --------------------------------------------------------
    # HIGH
    #
    # Correlated river disturbance and machinery evidence.
    # --------------------------------------------------------

    if (
        elevated_turbidity
        and (
            strong_audio
            or strong_vibration
        )
        and (
            confirmation_score >= 0.66
            or (
                elevated_turbidity
                and strong_audio
                and strong_vibration
            )
        )
    ):
        return {
            "prediction":
                "POSSIBLE_MINING_ACTIVITY",

            "risk_level":
                "HIGH",

            "reasons": [
                "River disturbance detected",
                "Machinery-related evidence detected",
                "Multiple sensors provide supporting evidence",
            ],

            "persistence_met":
                persistence_met,

            "required_persistence_seconds":
                critical_persistence,
        }

    # --------------------------------------------------------
    # MEDIUM - MACHINERY ONLY
    # --------------------------------------------------------

    if (
        strong_audio
        or strong_vibration
    ):
        return {
            "prediction":
                "MACHINERY_ACTIVITY",

            "risk_level":
                "MEDIUM",

            "reasons": [
                "Machinery signature detected",
                "River disturbance evidence is insufficient for high-risk mining classification",
            ],

            "persistence_met":
                persistence_met,

            "required_persistence_seconds":
                critical_persistence,
        }

    # --------------------------------------------------------
    # MEDIUM - TURBIDITY / ENVIRONMENT ONLY
    # --------------------------------------------------------

    if (
        elevated_turbidity
        or max(
            turbidity_a,
            turbidity_b,
        ) >= 50.0
    ):
        return {
            "prediction":
                "SUSPICIOUS_ENVIRONMENTAL_CHANGE",

            "risk_level":
                "MEDIUM",

            "reasons": [
                "River turbidity is elevated without matching machinery signatures"
            ],

            "persistence_met":
                persistence_met,

            "required_persistence_seconds":
                critical_persistence,
        }

    # --------------------------------------------------------
    # SAFE
    #
    # A fusion-model label alone must not bypass the
    # GoldTrace safety/risk policy.
    # --------------------------------------------------------

    return {
        "prediction":
            "SAFE",

        "risk_level":
            "LOW",

        "reasons": [
            (
                f"Fusion model output {fusion_class} "
                "did not satisfy GoldTrace multi-sensor risk rules"
            )
        ],

        "persistence_met":
            persistence_met,

        "required_persistence_seconds":
            critical_persistence,
    }
