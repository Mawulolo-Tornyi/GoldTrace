from src.database import Database
from src.mock_sensor_stream import scenario_packets
from src.realtime_engine import RealtimeEngine


def test_auto_persistence_promotes_high_to_critical(
    tmp_path,
    monkeypatch,
):
    clock = [100.0]

    monkeypatch.setattr(
        "src.persistence_tracker.monotonic",
        lambda: clock[0],
    )

    engine = RealtimeEngine(
        database=Database(
            tmp_path / "db.sqlite"
        )
    )

    a1, b1 = scenario_packets(
        "high_risk_mining",
        seed=42,
    )

    first = engine.process_pair(
        a1,
        b1,
    )

    assert (
        first["risk_level"]
        == "HIGH"
    )

    assert (
        first["evidence"][
            "persistent_activity"
        ]
        is False
    )

    required = float(
        first["evidence"][
            "required_persistence_seconds"
        ]
    )

    clock[0] += (
        required + 1.0
    )

    a2, b2 = scenario_packets(
        "high_risk_mining",
        seed=43,
    )

    second = engine.process_pair(
        a2,
        b2,
    )

    assert (
        second["risk_level"]
        == "CRITICAL"
    )

    assert (
        second["prediction"]
        == "HIGH_RISK_MINING_ACTIVITY"
    )

    assert (
        second["evidence"][
            "persistent_activity"
        ]
        is True
    )

    assert (
        second["evidence"][
            "persistence_seconds"
        ]
        >= required
    )
