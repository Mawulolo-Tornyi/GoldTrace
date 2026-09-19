from __future__ import annotations

import os

from dataclasses import (
    dataclass,
)

from pathlib import (
    Path,
)


try:
    from dotenv import (
        load_dotenv,
    )
except ImportError:
    load_dotenv = None


BASE_DIR = Path(
    __file__
).resolve().parent


if load_dotenv is not None:
    load_dotenv(
        BASE_DIR /
        ".env"
    )


def env_bool(
    name: str,
    default: bool = False,
) -> bool:
    value = os.getenv(
        name
    )


    if value is None:
        return default


    return (
        value.strip().lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )


@dataclass(
    frozen=True,
)
class GatewaySettings:
    backend_url: str

    allowed_nodes: tuple[
        str,
        ...
    ]

    lora_frequency_mhz: float

    lora_cs_pin: str

    lora_reset_pin: str

    lora_shared_key: str

    lcd_enabled: bool

    lcd_i2c_address: int

    sim7600_enabled: bool

    sim7600_port: str

    sim7600_baud: int

    backend_timeout_seconds: float


def load_settings() -> GatewaySettings:
    secret = os.getenv(
        "LORA_SHARED_KEY",
        "",
    ).strip()


    if not secret:
        raise RuntimeError(
            "LORA_SHARED_KEY is not configured."
        )


    allowed_nodes_raw = os.getenv(
        "GOLDTRACE_ALLOWED_NODES",
        "NODE_A,NODE_B",
    )


    allowed_nodes = tuple(
        item.strip()
        for item in allowed_nodes_raw.split(
            ","
        )
        if item.strip()
    )


    if not allowed_nodes:
        raise RuntimeError(
            "No GoldTrace node IDs are configured."
        )


    return GatewaySettings(
        backend_url=os.getenv(
            "GOLDTRACE_BACKEND_URL",
            "http://127.0.0.1:8000/sensor-data",
        ),

        allowed_nodes=allowed_nodes,

        lora_frequency_mhz=float(
            os.getenv(
                "LORA_FREQUENCY_MHZ",
                "868.0",
            )
        ),

        lora_cs_pin=os.getenv(
            "LORA_CS_PIN",
            "CE1",
        ),

        lora_reset_pin=os.getenv(
            "LORA_RESET_PIN",
            "D25",
        ),

        lora_shared_key=secret,

        lcd_enabled=env_bool(
            "LCD_ENABLED",
            True,
        ),

        lcd_i2c_address=int(
            os.getenv(
                "LCD_I2C_ADDRESS",
                "0x27",
            ),
            0,
        ),

        sim7600_enabled=env_bool(
            "SIM7600_ENABLED",
            False,
        ),

        sim7600_port=os.getenv(
            "SIM7600_PORT",
            "/dev/ttyUSB2",
        ),

        sim7600_baud=int(
            os.getenv(
                "SIM7600_BAUD",
                "115200",
            )
        ),

        backend_timeout_seconds=float(
            os.getenv(
                "BACKEND_TIMEOUT_SECONDS",
                "5",
            )
        ),
    )
