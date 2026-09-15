from __future__ import annotations
import time
from .base import DeliveryResult


class SIM7600SMSChannel:
    name = 'sim7600_sms'
    def __init__(self, port: str = '/dev/ttyUSB2', baudrate: int = 115200, timeout: float = 8.0):
        self.port = port; self.baudrate = int(baudrate); self.timeout = float(timeout)

    def _serial(self):
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError('pyserial is required for SIM7600 production SMS') from exc
        return serial.Serial(self.port, self.baudrate, timeout=self.timeout, write_timeout=self.timeout)

    @staticmethod
    def _command(ser, command: str, wait: float = 0.5) -> str:
        ser.reset_input_buffer()
        ser.write((command + '\r').encode('ascii'))
        ser.flush(); time.sleep(wait)
        return ser.read_all().decode('utf-8', errors='replace')

    def send(self, destination: str, message: str) -> DeliveryResult:
        try:
            with self._serial() as ser:
                if 'OK' not in self._command(ser, 'AT'):
                    return DeliveryResult(False, 'FAILED', error='SIM7600 did not answer AT')
                cpin = self._command(ser, 'AT+CPIN?')
                if 'READY' not in cpin:
                    return DeliveryResult(False, 'FAILED', provider_response=cpin, error='SIM not ready')
                creg = self._command(ser, 'AT+CREG?')
                if not any(x in creg for x in [',1', ',5']):
                    return DeliveryResult(False, 'FAILED', provider_response=creg, error='Not registered on mobile network')
                self._command(ser, 'AT+CMGF=1')
                ser.write((f'AT+CMGS="{destination}"\r').encode('ascii')); ser.flush(); time.sleep(0.7)
                prompt = ser.read_all().decode('utf-8', errors='replace')
                if '>' not in prompt:
                    return DeliveryResult(False, 'FAILED', provider_response=prompt, error='SMS prompt not received')
                ser.write(message.encode('utf-8') + bytes([26])); ser.flush(); time.sleep(3.0)
                response = ser.read_all().decode('utf-8', errors='replace')
                success = '+CMGS:' in response and 'OK' in response
                return DeliveryResult(success, 'SENT' if success else 'FAILED', response, None if success else 'Modem rejected SMS')
        except Exception as exc:
            return DeliveryResult(False, 'FAILED', error=str(exc))
