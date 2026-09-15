from __future__ import annotations
from .base import DeliveryResult


class MockSMSChannel:
    name = 'mock_sms'
    def __init__(self, succeed: bool = True):
        self.succeed = succeed
        self.sent: list[tuple[str, str]] = []

    def send(self, destination: str, message: str) -> DeliveryResult:
        self.sent.append((destination, message))
        if self.succeed:
            return DeliveryResult(True, 'SENT', 'SIMULATED')
        return DeliveryResult(False, 'FAILED', error='Simulated network failure')
