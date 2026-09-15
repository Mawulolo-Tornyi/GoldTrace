from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass
class DeliveryResult:
    success: bool
    status: str
    provider_response: str = ''
    error: str | None = None


class NotificationChannel(Protocol):
    name: str
    def send(self, destination: str, message: str) -> DeliveryResult: ...
