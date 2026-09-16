import pytest

from src.database import Database
from src.mock_sensor_stream import scenario_packets
from src.realtime_engine import RealtimeEngine


@pytest.mark.parametrize(
    (
        "scenario",
        "expected_prediction",
        "expected_risk",
    ),
    [
        (
            "normal",
            "SAFE",
            "LOW",
        ),
        (
            "heavy_rain",
            "SUSPICIOUS_ENVIRONMENTAL_CHANGE",
            "MEDIUM",
        ),
        (
            "vehicle",
            "MACHINERY_ACTIVITY",
            "MEDIUM",
        ),
        (
            "mixed_rain_and_vehicle",
            "MACHINERY_ACTIVITY",
            "MEDIUM",
        ),
        (
            "mixed_rain_and_machinery",
            "MACHINERY_ACTIVITY",
            "MEDIUM",
        ),
        (
            "possible_mining",
            "POSSIBLE_MINING_ACTIVITY",
            "HIGH",
        ),
        (
            "excavator",
            "MACHINERY_ACTIVITY",
            "MEDIUM",
        ),
        (
            "sensor_failure",
            "SYSTEM_UNCERTAIN",
            "UNKNOWN",
        ),
        (
            "communication_failure",
            "SYSTEM_UNCERTAIN",
            "UNKNOWN",
        ),
    ],
)
def test_noncritical_scenario_matrix(
    tmp_path,
    scenario,
    expected_prediction,
    expected_risk,
):
    engine = RealtimeEngine(
        database=Database(
            tmp_path /
            f"{scenario}.sqlite"
        )
    )

    node_a, node_b = scenario_packets(
        scenario,
        seed=42,
    )

    result = engine.process_pair(
        node_a,
        node_b,
        persistence_seconds=0,
    )

    assert (
        result["prediction"]
        == expected_prediction
    )

    assert (
        result["risk_level"]
        == expected_risk
    )

    assert (
        result["risk_level"]
        != "CRITICAL"
    )

    assert (
        result["agency_alert"][
            "eligible"
        ]
        is False
    )


def test_high_risk_requires_persistence(
    tmp_path,
):
    engine = RealtimeEngine(
        database=Database(
            tmp_path /
            "critical.sqlite"
        )
    )

    node_a, node_b = scenario_packets(
        "high_risk_mining",
        seed=42,
    )

    initial = engine.process_pair(
        node_a,
        node_b,
        persistence_seconds=0,
    )

    assert (
        initial["prediction"]
        == "POSSIBLE_MINING_ACTIVITY"
    )

    assert (
        initial["risk_level"]
        == "HIGH"
    )

    assert (
        initial["agency_alert"][
            "eligible"
        ]
        is False
    )

    persistent = engine.process_pair(
        node_a,
        node_b,
        persistence_seconds=42,
    )

    assert (
        persistent["prediction"]
        == "HIGH_RISK_MINING_ACTIVITY"
    )

    assert (
        persistent["risk_level"]
        == "CRITICAL"
    )

    assert (
        persistent["suspected_zone"]
        == "BETWEEN_NODE_A_AND_NODE_B"
    )

    assert (
        persistent["location"][
            "segment_id"
        ]
        == "SEGMENT_A_B"
    )

    assert (
        persistent["agency_alert"][
            "eligible"
        ]
        is True
    )
