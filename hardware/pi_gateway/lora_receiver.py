from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


# ============================================================
# OPTIONAL HARDWARE IMPORTS
# ============================================================

try:
    import board
    import digitalio
    import adafruit_rfm9x

    HARDWARE_LIBRARIES_AVAILABLE = True

except ImportError:
    board = None
    digitalio = None
    adafruit_rfm9x = None

    HARDWARE_LIBRARIES_AVAILABLE = False


# ============================================================
# CONSTANTS
# ============================================================

SX127X_SYNC_WORD_REGISTER = 0x39

DEFAULT_SYNC_WORD = 0x12

DEFAULT_PREAMBLE_LENGTH = 8

MAX_GOLDTRACE_PACKET_BYTES = 240


# ============================================================
# RECEIVED PACKET
# ============================================================

@dataclass(frozen=True)
class ReceivedLoRaPacket:
    payload: str

    rssi: float | None

    snr: float | None

    received_at: datetime

    raw_length: int


# ============================================================
# ERRORS
# ============================================================

class LoRaReceiverError(
    RuntimeError
):
    pass


# ============================================================
# PIN RESOLUTION
# ============================================================

def _resolve_board_pin(
    pin_name: str,
):
    if board is None:
        raise LoRaReceiverError(
            "Raspberry Pi board library is unavailable."
        )


    normalized = (
        str(
            pin_name
        )
        .strip()
        .upper()
    )


    aliases = {
        "GPIO7": "D7",
        "GPIO8": "D8",
        "GPIO25": "D25",
        "GPIO22": "D22",

        "SPI0_CE0": "CE0",
        "SPI0_CE1": "CE1",
    }


    normalized = aliases.get(
        normalized,
        normalized,
    )


    if not hasattr(
        board,
        normalized,
    ):
        raise LoRaReceiverError(
            f"Unknown Raspberry Pi pin: {pin_name}"
        )


    return getattr(
        board,
        normalized,
    )


# ============================================================
# LORA RECEIVER
# ============================================================

class LoRaReceiver:
    def __init__(
        self,
        *,
        frequency_mhz: float,
        cs_pin: str = "CE1",
        reset_pin: str = "D25",
        bandwidth_hz: int = 125000,
        spreading_factor: int = 9,
        coding_rate: int = 7,
        sync_word: int = DEFAULT_SYNC_WORD,
        preamble_length: int = DEFAULT_PREAMBLE_LENGTH,
    ) -> None:
        self.frequency_mhz = float(
            frequency_mhz
        )


        self.cs_pin_name = str(
            cs_pin
        )


        self.reset_pin_name = str(
            reset_pin
        )


        self.bandwidth_hz = int(
            bandwidth_hz
        )


        self.spreading_factor = int(
            spreading_factor
        )


        self.coding_rate = int(
            coding_rate
        )


        self.sync_word = int(
            sync_word
        )


        self.preamble_length = int(
            preamble_length
        )


        self._spi: Any = None

        self._cs: Any = None

        self._reset: Any = None

        self._radio: Any = None

        self._ready = False


    # ========================================================
    # INITIALIZE
    # ========================================================

    def initialize(
        self,
    ) -> bool:
        if not HARDWARE_LIBRARIES_AVAILABLE:
            raise LoRaReceiverError(
                "Raspberry Pi LoRa libraries are not installed."
            )


        if not (
            0 <= self.sync_word <= 255
        ):
            raise LoRaReceiverError(
                "LoRa sync word must fit in one byte."
            )


        if not (
            5 <= self.coding_rate <= 8
        ):
            raise LoRaReceiverError(
                "LoRa coding rate must be between 5 and 8."
            )


        if not (
            6 <= self.spreading_factor <= 12
        ):
            raise LoRaReceiverError(
                "LoRa spreading factor must be between 6 and 12."
            )


        try:
            cs_pin_object = (
                _resolve_board_pin(
                    self.cs_pin_name
                )
            )


            reset_pin_object = (
                _resolve_board_pin(
                    self.reset_pin_name
                )
            )


            self._spi = (
                board.SPI()
            )


            self._cs = (
                digitalio.DigitalInOut(
                    cs_pin_object
                )
            )


            self._reset = (
                digitalio.DigitalInOut(
                    reset_pin_object
                )
            )


            self._radio = (
                adafruit_rfm9x.RFM9x(
                    self._spi,
                    self._cs,
                    self._reset,
                    self.frequency_mhz,
                )
            )


            # ------------------------------------------------
            # MATCH ESP32 RADIOLIB CONFIGURATION
            # ------------------------------------------------

            self._radio.signal_bandwidth = (
                self.bandwidth_hz
            )


            self._radio.spreading_factor = (
                self.spreading_factor
            )


            self._radio.coding_rate = (
                self.coding_rate
            )


            self._radio.preamble_length = (
                self.preamble_length
            )


            self._radio.enable_crc = (
                True
            )


            # ------------------------------------------------
            # LORA SYNC WORD
            # ------------------------------------------------
            #
            # SX1276 register 0x39 stores RegSyncWord.
            #
            # Adafruit's driver currently uses the internal
            # register writer for custom sync-word settings.
            #
            # GoldTrace ESP32 nodes use 0x12, so the Pi must
            # use the same value.
            #

            self._radio._write_u8(
                SX127X_SYNC_WORD_REGISTER,
                self.sync_word,
            )


            self._ready = True


            return True


        except Exception as exc:
            self._ready = False


            self.close()


            raise LoRaReceiverError(
                f"Unable to initialize LoRa receiver: {exc}"
            ) from exc


    # ========================================================
    # STATUS
    # ========================================================

    @property
    def ready(
        self,
    ) -> bool:
        return (
            self._ready
            and
            self._radio is not None
        )


    # ========================================================
    # RECEIVE ONE PACKET
    # ========================================================

    def receive(
        self,
        *,
        timeout_seconds: float = 1.0,
    ) -> ReceivedLoRaPacket | None:
        if not self.ready:
            raise LoRaReceiverError(
                "LoRa receiver is not initialized."
            )


        try:
            packet = (
                self._radio.receive(
                    timeout=max(
                        0.0,
                        float(
                            timeout_seconds
                        ),
                    )
                )
            )


        except Exception as exc:
            raise LoRaReceiverError(
                f"LoRa receive failed: {exc}"
            ) from exc



        if packet is None:
            return None


        raw = bytes(
            packet
        )


        raw_length = len(
            raw
        )


        if raw_length == 0:
            return None


        if (
            raw_length >
            MAX_GOLDTRACE_PACKET_BYTES
        ):
            raise LoRaReceiverError(
                "Received LoRa packet exceeds "
                f"{MAX_GOLDTRACE_PACKET_BYTES} bytes."
            )


        try:
            payload = raw.decode(
                "utf-8",
                errors="strict",
            )


        except UnicodeDecodeError as exc:
            raise LoRaReceiverError(
                "Received LoRa payload is not valid UTF-8."
            ) from exc


        # ----------------------------------------------------
        # RADIO QUALITY
        # ----------------------------------------------------

        rssi = getattr(
            self._radio,
            "last_rssi",
            None,
        )


        snr = getattr(
            self._radio,
            "last_snr",
            None,
        )


        if rssi is not None:
            try:
                rssi = float(
                    rssi
                )

            except (
                TypeError,
                ValueError,
            ):
                rssi = None


        if snr is not None:
            try:
                snr = float(
                    snr
                )

            except (
                TypeError,
                ValueError,
            ):
                snr = None


        return ReceivedLoRaPacket(
            payload=payload,

            rssi=rssi,

            snr=snr,

            received_at=datetime.now(
                timezone.utc
            ),

            raw_length=raw_length,
        )


    # ========================================================
    # CLEANUP
    # ========================================================

    def close(
        self,
    ) -> None:
        self._ready = False

        self._radio = None


        if self._cs is not None:
            try:
                self._cs.deinit()

            except Exception:
                pass


            self._cs = None


        if self._reset is not None:
            try:
                self._reset.deinit()

            except Exception:
                pass


            self._reset = None


        self._spi = None


    # ========================================================
    # CONTEXT MANAGER
    # ========================================================

    def __enter__(
        self,
    ) -> "LoRaReceiver":
        self.initialize()

        return self


    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.close()
