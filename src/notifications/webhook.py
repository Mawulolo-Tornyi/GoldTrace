from __future__ import annotations
import httpx
from .base import DeliveryResult


class WebhookChannel:
    name = 'webhook'
    def __init__(self, timeout: float = 10.0): self.timeout = timeout
    def send(self, destination: str, message: str) -> DeliveryResult:
        try:
            r = httpx.post(destination, json={'message': message}, timeout=self.timeout)
            ok = 200 <= r.status_code < 300
            return DeliveryResult(ok, 'SENT' if ok else 'FAILED', f'HTTP {r.status_code}', None if ok else r.text[:200])
        except Exception as exc:
            return DeliveryResult(False, 'FAILED', error=str(exc))
