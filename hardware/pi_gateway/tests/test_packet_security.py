import json
import pathlib
import sys

import pytest


TEST_DIR = pathlib.Path(
    __file__
).resolve().parent


GATEWAY_DIR = (
    TEST_DIR.parent
)


sys.path.insert(
    0,
    str(
        GATEWAY_DIR
    ),
)


from packet_security import (
    PacketSecurityError,
    ReplayGuard,
    decode_wire_packet,
    sign_payload,
)


SECRET = (
    "goldtrace-test-secret"
)


def make_payload(
    *,
    node_id: str = "NODE_A",
    boot_id: int = 12345,
    sequence: int = 1,
) -> str:
    return json.dumps(
        {
            "v": 1,
            "id": node_id,
            "b": boot_id,
            "seq": sequence,
            "up": 5000,
            "tu": 31.4,
            "ar": 0.014,
            "vr": 0.027,
        },
        separators=(
            ",",
            ":",
        ),
    )


def build_wire_packet(
    payload: str,
) -> str:
    signature = sign_payload(
        payload,
        SECRET,
    )


    return (
        payload +
        "|" +
        signature
    )


def test_valid_authenticated_packet():
    payload = make_payload()


    packet = decode_wire_packet(
        build_wire_packet(
            payload
        ),
        SECRET,
    )


    assert (
        packet["id"]
        ==
        "NODE_A"
    )


    assert (
        packet["seq"]
        ==
        1
    )


def test_modified_payload_is_rejected():
    payload = make_payload()


    wire_packet = (
        build_wire_packet(
            payload
        )
    )


    tampered = wire_packet.replace(
        "31.4",
        "99.9",
    )


    with pytest.raises(
        PacketSecurityError
    ):
        decode_wire_packet(
            tampered,
            SECRET,
        )


def test_wrong_secret_is_rejected():
    payload = make_payload()


    wire_packet = (
        build_wire_packet(
            payload
        )
    )


    with pytest.raises(
        PacketSecurityError
    ):
        decode_wire_packet(
            wire_packet,
            "wrong-key",
        )


def test_missing_signature_is_rejected():
    with pytest.raises(
        PacketSecurityError
    ):
        decode_wire_packet(
            make_payload(),
            SECRET,
        )


def test_replay_guard_rejects_duplicate_sequence():
    guard = ReplayGuard()


    packet = {
        "id": "NODE_A",
        "b": 999,
        "seq": 7,
    }


    assert (
        guard.accept(
            packet
        )
        is True
    )


    assert (
        guard.accept(
            packet
        )
        is False
    )


def test_replay_guard_rejects_older_sequence():
    guard = ReplayGuard()


    assert guard.accept(
        {
            "id": "NODE_A",
            "b": 999,
            "seq": 10,
        }
    )


    assert (
        guard.accept(
            {
                "id": "NODE_A",
                "b": 999,
                "seq": 9,
            }
        )
        is False
    )


def test_new_boot_id_allows_sequence_restart():
    guard = ReplayGuard()


    assert guard.accept(
        {
            "id": "NODE_A",
            "b": 100,
            "seq": 25,
        }
    )


    assert guard.accept(
        {
            "id": "NODE_A",
            "b": 101,
            "seq": 0,
        }
    )


def test_different_nodes_have_independent_sequences():
    guard = ReplayGuard()


    assert guard.accept(
        {
            "id": "NODE_A",
            "b": 1,
            "seq": 4,
        }
    )


    assert guard.accept(
        {
            "id": "NODE_B",
            "b": 1,
            "seq": 4,
        }
    )
