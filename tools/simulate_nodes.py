from __future__ import annotations

import argparse
import json
import sys
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from src.mock_sensor_stream import (
    SCENARIOS,
    scenario_packets,
)


DEFAULT_API = "http://127.0.0.1:8000"


ALIASES = {
    "normal": "normal",

    "rain": "heavy_rain",

    "vehicle": "vehicle",

    "machinery": "vehicle",

    "rain-vehicle":
        "mixed_rain_and_vehicle",

    "rain-machinery":
        "mixed_rain_and_machinery",

    "mining": "possible_mining",

    "critical": "high_risk_mining",

    "excavator": "excavator",

    "sensor-failure": "sensor_failure",

    "communication-failure":
        "communication_failure",
}


def post_json(
    url: str,
    payload: dict,
) -> dict:
    body = json.dumps(
        payload
    ).encode("utf-8")

    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type":
                "application/json",
        },
    )

    try:
        with urlopen(
            request,
            timeout=30,
        ) as response:
            text = (
                response
                .read()
                .decode("utf-8")
            )

            if not text:
                return {}

            return json.loads(text)

    except HTTPError as exc:
        body = (
            exc.read()
            .decode(
                "utf-8",
                errors="replace",
            )
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {body}"
        ) from exc

    except URLError as exc:
        raise RuntimeError(
            "Cannot connect to the "
            "GoldTrace backend. "
            "Make sure Uvicorn is "
            "running on port 8000."
        ) from exc


def enrich_packet(
    packet: dict,
    scenario: str,
) -> dict:
    return {
        **packet,

        "source":
            "SIMULATOR",

        "simulated":
            True,

        "simulation_scenario":
            scenario,
    }


def decision_from(
    response: dict,
) -> dict:
    result = response.get(
        "result"
    )

    if isinstance(
        result,
        dict,
    ):
        return result

    return response


def print_decision(
    response: dict,
) -> None:
    result = decision_from(
        response
    )

    if result.get(
        "waiting_for_other_node"
    ):
        print(
            "Waiting for the other node."
        )

        return

    print()

    print(
        "Prediction:",
        result.get(
            "prediction",
            "UNKNOWN",
        ),
    )

    print(
        "Risk:",
        result.get(
            "risk_level",
            result.get(
                "risk",
                "UNKNOWN",
            ),
        ),
    )

    print(
        "Confidence:",
        result.get(
            "confidence",
            "—",
        ),
    )

    print(
        "Zone:",
        result.get(
            "suspected_zone",
            "—",
        ),
    )

    evidence = result.get(
        "evidence"
    ) or {}

    print(
        "Persistence:",
        evidence.get(
            "persistence_seconds",
            0,
        ),
        "seconds",
    )

    print(
        "Persistent:",
        evidence.get(
            "persistent_activity",
            False,
        ),
    )

    location = result.get(
        "location"
    ) or {}

    print(
        "Segment:",
        location.get(
            "segment_id",
            "—",
        ),
    )

    agency = result.get(
        "agency_alert"
    ) or {}

    print(
        "Agency mode:",
        agency.get(
            "dispatch_mode",
            "—",
        ),
    )

    print(
        "Agency status:",
        agency.get(
            "dispatch_status",
            "—",
        ),
    )


def send_pair(
    api: str,
    scenario: str,
    seed: int,
) -> dict:
    timestamp = datetime.now(
        timezone.utc
    )

    node_a, node_b = (
        scenario_packets(
            scenario,
            seed=seed,
            timestamp=timestamp,
        )
    )

    node_a = enrich_packet(
        node_a,
        scenario,
    )

    node_b = enrich_packet(
        node_b,
        scenario,
    )

    print()
    print(
        "Sending NODE_A..."
    )

    result_a = post_json(
        f"{api}/sensor-data",
        node_a,
    )

    if result_a:
        if result_a.get(
            "waiting_for_other_node"
        ):
            print(
                "NODE_A accepted. "
                "Waiting for NODE_B."
            )
        else:
            print(
                "NODE_A accepted."
            )

    print(
        "Sending NODE_B..."
    )

    result_b = post_json(
        f"{api}/sensor-data",
        node_b,
    )

    print_decision(
        result_b
    )

    return result_b


def countdown(
    seconds: int,
) -> None:
    print()
    print(
        "Maintaining simulated "
        "activity for persistence..."
    )

    for remaining in range(
        seconds,
        0,
        -1,
    ):
        print(
            f"\r"
            f"Persistence wait: "
            f"{remaining:02d}s",
            end="",
            flush=True,
        )

        time.sleep(1)

    print(
        "\rPersistence wait: complete"
    )


def run(
    alias: str,
    api: str,
    seed: int,
    persistence: int,
) -> None:
    scenario = ALIASES[
        alias
    ]

    print()
    print(
        "=" * 60
    )

    print(
        "GOLDTRACE NODE SIMULATOR"
    )

    print(
        "=" * 60
    )

    print(
        "Source: SIMULATOR"
    )

    print(
        "Scenario:",
        alias,
    )

    print(
        "Backend:",
        api,
    )

    print(
        "Underlying scenario:",
        scenario,
    )

    print(
        "Agency dispatch remains "
        "controlled by backend config."
    )

    print(
        "=" * 60
    )

    if alias != "critical":
        send_pair(
            api,
            scenario,
            seed,
        )

        return

    print()
    print(
        "PHASE 1"
    )

    print(
        "Strong multi-sensor evidence "
        "without sufficient persistence."
    )

    first = send_pair(
        api,
        scenario,
        seed,
    )

    first_result = decision_from(
        first
    )

    if (
        first_result.get(
            "risk_level"
        ) == "CRITICAL"
    ):
        print()
        print(
            "The backend already has "
            "persistent activity state "
            "for this event."
        )

        print(
            "For a clean HIGH -> "
            "CRITICAL demonstration, "
            "restart the backend first."
        )

        return

    countdown(
        persistence
    )

    print()
    print(
        "PHASE 2"
    )

    print(
        "Sending the persistent "
        "multi-sensor condition again."
    )

    send_pair(
        api,
        scenario,
        seed + 1,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "GoldTrace virtual river "
            "sensor-node simulator"
        )
    )

    parser.add_argument(
        "scenario",
        nargs="?",
        choices=sorted(
            ALIASES
        ),
        help=(
            "Simulation scenario"
        ),
    )

    parser.add_argument(
        "--api",
        default=DEFAULT_API,
        help=(
            "GoldTrace backend base URL"
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--persistence",
        type=int,
        default=42,
        help=(
            "Seconds to maintain the "
            "critical scenario before "
            "sending the second pair"
        ),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help=(
            "Show simulator scenarios"
        ),
    )

    args = parser.parse_args()

    if args.list:
        print(
            "Available GoldTrace "
            "simulator scenarios:"
        )

        for name in sorted(
            ALIASES
        ):
            print(
                f"  {name:<22}"
                f" -> "
                f"{ALIASES[name]}"
            )

        print()
        print(
            "Underlying project "
            "scenarios:"
        )

        for name in sorted(
            SCENARIOS
        ):
            print(
                f"  {name}"
            )

        return

    if not args.scenario:
        parser.error(
            "choose a scenario "
            "or use --list"
        )

    run(
        args.scenario,
        args.api.rstrip("/"),
        args.seed,
        max(
            1,
            args.persistence,
        ),
    )


if __name__ == "__main__":
    main()

