from __future__ import annotations

import hashlib
import hmac
import json

from dataclasses import (
    dataclass,
    field,
)


SIGNATURE_HEX_LENGTH = 32


class PacketSecurityError(
    ValueError
):
    """Raised when a GoldTrace LoRa packet fails validation."""


def sign_payload(
    payload_text: str,
    secret: str,
) -> str:
    if not secret:
        raise PacketSecurityError(
            "GoldTrace shared secret is empty."
        )


    signature = hmac.new(
        secret.encode(
            "utf-8"
        ),
        payload_text.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


    return signature[
        :SIGNATURE_HEX_LENGTH
    ]


def decode_wire_packet(
    wire_packet: str,
    secret: str,
) -> dict:
    if not isinstance(
        wire_packet,
        str,
    ):
        raise PacketSecurityError(
            "LoRa packet must be text."
        )


    try:
        payload_text, received_signature = (
            wire_packet.rsplit(
                "|",
                1,
            )
        )

    except ValueError as exc:
        raise PacketSecurityError(
            "Packet does not contain an authentication signature."
        ) from exc


    received_signature = (
        received_signature
        .strip()
        .lower()
    )


    if (
        len(
            received_signature
        )
        != SIGNATURE_HEX_LENGTH
    ):
        raise PacketSecurityError(
            "Packet signature length is invalid."
        )


    expected_signature = sign_payload(
        payload_text,
        secret,
    )


    if not hmac.compare_digest(
        expected_signature,
        received_signature,
    ):
        raise PacketSecurityError(
            "Packet authentication failed."
        )


    try:
        packet = json.loads(
            payload_text
        )

    except json.JSONDecodeError as exc:
        raise PacketSecurityError(
            "Authenticated payload is not valid JSON."
        ) from exc


    if not isinstance(
        packet,
        dict,
    ):
        raise PacketSecurityError(
            "Authenticated payload must be a JSON object."
        )


    required_fields = {
        "v",
        "id",
        "b",
        "seq",
        "up",
    }


    missing_fields = (
        required_fields -
        packet.keys()
    )


    if missing_fields:
        raise PacketSecurityError(
            "Missing required packet fields: "
            +
            ", ".join(
                sorted(
                    missing_fields
                )
            )
        )


    try:
        protocol_version = int(
            packet["v"]
        )


        boot_id = int(
            packet["b"]
        )


        sequence = int(
            packet["seq"]
        )


        uptime = int(
            packet["up"]
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise PacketSecurityError(
            "Packet identifiers contain invalid values."
        ) from exc


    if (
        protocol_version != 1
    ):
        raise PacketSecurityError(
            f"Unsupported protocol version: {protocol_version}"
        )


    if (
        boot_id < 0
        or sequence < 0
        or uptime < 0
    ):
        raise PacketSecurityError(
            "Packet counters cannot be negative."
        )


    node_id = str(
        packet["id"]
    ).strip()


    if not node_id:
        raise PacketSecurityError(
            "Packet node ID is empty."
        )


    packet["id"] = (
        node_id
    )


    packet["v"] = (
        protocol_version
    )


    packet["b"] = (
        boot_id
    )


    packet["seq"] = (
        sequence
    )


    packet["up"] = (
        uptime
    )


    return packet


@dataclass
class ReplayGuard:
    """
    In-memory replay protection.

    Keyed by:
        node ID + ESP32 boot ID

    Each new ESP32 boot receives a new boot ID,
    allowing sequence numbers to restart safely.
    """

    last_sequences: dict[
        tuple[
            str,
            int,
        ],
        int,
    ] = field(
        default_factory=dict
    )


    def accept(
        self,
        packet: dict,
    ) -> bool:
        node_id = str(
            packet["id"]
        )


        boot_id = int(
            packet["b"]
        )


        sequence = int(
            packet["seq"]
        )


        key = (
            node_id,
            boot_id,
        )


        previous = (
            self.last_sequences.get(
                key
            )
        )


        if (
            previous is not None
            and sequence <= previous
        ):
            return False


        self.last_sequences[
            key
        ] = sequence


        return True


    def reset_node(
        self,
        node_id: str,
    ) -> None:
        keys = [
            key
            for key in self.last_sequences
            if key[0] == node_id
        ]


        for key in keys:
            self.last_sequences.pop(
                key,
                None,
            )
