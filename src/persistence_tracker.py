from __future__ import annotations

from time import monotonic


class PersistenceTracker:
    """
    Tracks how long a continuous pre-CRITICAL
    condition has remained active.

    Uses backend monotonic time so persistence
    does not depend on ESP32 clock accuracy.
    """

    def __init__(self) -> None:
        self._started_at: float | None = None

    def reset(self) -> None:
        self._started_at = None

    def update(
        self,
        active: bool,
        now: float | None = None,
    ) -> float:
        if not active:
            self.reset()
            return 0.0

        current = (
            monotonic()
            if now is None
            else float(now)
        )

        if self._started_at is None:
            self._started_at = current
            return 0.0

        return max(
            0.0,
            current - self._started_at,
        )
