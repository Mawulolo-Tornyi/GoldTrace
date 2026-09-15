from __future__ import annotations
import os, smtplib
from email.message import EmailMessage
from .base import DeliveryResult


class EmailChannel:
    name = 'email'
    def send(self, destination: str, message: str) -> DeliveryResult:
        host = os.getenv('GOLDTRACE_SMTP_HOST')
        user = os.getenv('GOLDTRACE_SMTP_USER')
        password = os.getenv('GOLDTRACE_SMTP_PASSWORD')
        if not host or not user or not password:
            return DeliveryResult(False, 'FAILED', error='SMTP environment variables not configured')
        try:
            msg = EmailMessage(); msg['Subject'] = 'GoldTrace Alert'; msg['From'] = user; msg['To'] = destination; msg.set_content(message)
            with smtplib.SMTP_SSL(host, int(os.getenv('GOLDTRACE_SMTP_PORT','465'))) as smtp:
                smtp.login(user, password); smtp.send_message(msg)
            return DeliveryResult(True, 'SENT', 'SMTP accepted message')
        except Exception as exc:
            return DeliveryResult(False, 'FAILED', error=str(exc))
