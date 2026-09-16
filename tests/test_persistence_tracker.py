from src.persistence_tracker import (
    PersistenceTracker,
)


def test_persistence_tracker_starts_and_resets():
    tracker = PersistenceTracker()

    assert tracker.update(
        True,
        now=100.0,
    ) == 0.0

    assert tracker.update(
        True,
        now=112.5,
    ) == 12.5

    assert tracker.update(
        False,
        now=113.0,
    ) == 0.0

    assert tracker.update(
        True,
        now=200.0,
    ) == 0.0
