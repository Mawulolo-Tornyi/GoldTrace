from fastapi.testclient import TestClient

import src.api as api

from src.database import Database
from src.realtime_engine import RealtimeEngine


def _install_test_engine(
    tmp_path,
    monkeypatch,
):
    database = Database(
        tmp_path / "simulator.sqlite"
    )

    engine = RealtimeEngine(
        database=database
    )

    monkeypatch.setattr(
        api,
        "db",
        database,
    )

    monkeypatch.setattr(
        api,
        "engine",
        engine,
    )

    api.latest_packets.clear()
    api.pending_pair_nodes.clear()

    return engine


def test_simulator_scenarios_available(
    tmp_path,
    monkeypatch,
):
    engine = _install_test_engine(
        tmp_path,
        monkeypatch,
    )

    assert (
        engine.agency_dispatcher.mode
        == "DEMO"
    )

    client = TestClient(
        api.app
    )

    response = client.get(
        "/simulator/scenarios"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["mode"] == "DEMO"

    assert (
        body["aliases"]["critical"]
        == "high_risk_mining"
    )

    assert (
        body["critical_wait_seconds"]
        >= 20
    )


def test_simulator_normal_uses_real_pipeline(
    tmp_path,
    monkeypatch,
):
    _install_test_engine(
        tmp_path,
        monkeypatch,
    )

    client = TestClient(
        api.app
    )

    response = client.post(
        "/simulator/run",
        json={
            "scenario": "normal",
            "seed": 42,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["source"] == "SIMULATOR"
    assert body["simulated"] is True
    assert body["scenario"] == "normal"

    result = body["result"]

    assert result["prediction"] == "SAFE"
    assert result["risk_level"] == "LOW"

    assert (
        result["agency_alert"]["eligible"]
        is False
    )


def test_simulator_rejects_unknown_scenario(
    tmp_path,
    monkeypatch,
):
    _install_test_engine(
        tmp_path,
        monkeypatch,
    )

    client = TestClient(
        api.app
    )

    response = client.post(
        "/simulator/run",
        json={
            "scenario":
                "not-a-real-scenario"
        },
    )

    assert response.status_code == 400
