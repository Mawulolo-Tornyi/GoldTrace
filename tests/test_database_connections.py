import sqlite3

import pytest

from src.database import Database


def test_managed_database_connection_closes(
    tmp_path,
):
    db = Database(
        tmp_path / "managed.sqlite"
    )

    with db.connection() as con:
        row = con.execute(
            "SELECT 1 AS value"
        ).fetchone()

        assert row["value"] == 1

    with pytest.raises(
        sqlite3.ProgrammingError
    ):
        con.execute(
            "SELECT 1"
        )


def test_database_methods_still_work(
    tmp_path,
):
    db = Database(
        tmp_path / "methods.sqlite"
    )

    db.save_sensor_reading({
        "node_id": "NODE_A",
        "timestamp":
            "2026-09-16T05:00:00Z",
        "turbidity_ntu": 18.0,
    })

    assert (
        db.latest_prediction()
        is None
    )
