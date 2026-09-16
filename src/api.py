from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import asyncio
import os

from .database import Database
from .model_manager import ModelManager
from .realtime_engine import RealtimeEngine
from .baseline_manager import BaselineManager
from .river_topology import RiverTopology
from .geospatial import GeospatialEngine
from .agency_registry import AgencyRegistry
from .config import load_settings
from .mock_sensor_stream import (
    SCENARIOS,
    scenario_packets,
)


app = FastAPI(
    title="GoldTrace ML + Geospatial + Agency Alert API",
    version="0.2.0",
)


# ============================================================
# CORS
# ============================================================

_default_origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

_extra_origins = [
    item.strip()
    for item in os.getenv(
        "GOLDTRACE_CORS_ORIGINS",
        "",
    ).split(",")
    if item.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        *_default_origins,
        *_extra_origins,
    ],
    allow_origin_regex=(
        r"^http://("
        r"192\.168\.\d{1,3}\.\d{1,3}|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
        r"):5173$"
    ),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# EXISTING GOLDTRACE SERVICES
# ============================================================

db = Database()

models = ModelManager()

engine = RealtimeEngine(
    models=models,
    database=db,
)

topology = RiverTopology()

geo = GeospatialEngine(
    topology,
)

registry = AgencyRegistry()

latest_packets: dict[
    str,
    dict
] = {}

pending_pair_nodes: set[str] = set()

alerts: deque[dict] = deque(
    maxlen=500
)


# ============================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[
            WebSocket
        ] = []

    async def connect(
        self,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

        self.active_connections.append(
            websocket
        )

    def disconnect(
        self,
        websocket: WebSocket,
    ) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(
                websocket
            )

    async def broadcast(
        self,
        payload: dict[str, Any],
    ) -> None:
        dead: list[
            WebSocket
        ] = []

        for websocket in list(
            self.active_connections
        ):
            try:
                await websocket.send_json(
                    payload
                )

            except Exception:
                dead.append(
                    websocket
                )

        for websocket in dead:
            self.disconnect(
                websocket
            )


manager = ConnectionManager()


# ============================================================
# HELPERS
# ============================================================

def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _require_admin(
    x_goldtrace_admin_key: str | None = Header(
            default=None
        ),
) -> None:
    expected = os.getenv(
        "GOLDTRACE_ADMIN_API_KEY"
    )

    if (
        expected
        and
        x_goldtrace_admin_key
        != expected
    ):
        raise HTTPException(
            403,
            "admin authorization required",
        )


def _redact_destination(
    value: str | None,
) -> str | None:
    if not value:
        return value

    text = str(value)

    if "@" in text:
        a, b = text.split(
            "@",
            1,
        )

        return (
            a[:2]
            + "***@"
            + b
        ) if len(a) > 2 else (
            "***@" + b
        )

    if len(text) > 6:
        return (
            text[:4]
            + "***"
            + text[-3:]
        )

    return "***"


def _latest_alert_for_event(
    event_id: str | None,
) -> dict[str, Any] | None:
    if not event_id:
        return None

    try:
        items = db.list_alerts()

    except Exception:
        return None

    for item in items:
        if (
            str(
                item.get(
                    "event_id",
                    ""
                )
            )
            ==
            str(event_id)
        ):
            return item

    return None


async def _broadcast_result(
    result: dict[str, Any],
) -> None:
    """
    Broadcast the result already produced by
    GoldTrace's existing RealtimeEngine.

    No additional prediction is performed here.
    """

    await manager.broadcast({
        "type":
            "prediction_update",

        "data":
            result,
    })

    await manager.broadcast({
        "type":
            "risk_update",

        "data": {
            "event_id":
                result.get(
                    "event_id"
                ),

            "prediction":
                result.get(
                    "prediction",
                    "SYSTEM_UNCERTAIN",
                ),

            "risk_level":
                result.get(
                    "risk_level",
                    "UNKNOWN",
                ),

            "confidence":
                result.get(
                    "confidence",
                    0.0,
                ),
        },
    })

    await manager.broadcast({
        "type":
            "event",

        "data":
            result,
    })

    if result.get(
        "alert_generated"
    ):
        alert = (
            _latest_alert_for_event(
                result.get(
                    "event_id"
                )
            )
        )

        if alert:
            await manager.broadcast({
                "type":
                    "alert",

                "data":
                    alert,
            })

    await manager.broadcast({
        "type":
            "system_status",

        "data":
            system_status(),
    })


# ============================================================
# REQUEST MODELS
# ============================================================

class PairRequest(BaseModel):
    node_a: dict[
        str,
        Any
    ]

    node_b: dict[
        str,
        Any
    ]

    persistence_seconds: float = 0.0


class AckRequest(BaseModel):
    acknowledged_by: str

    notes: str = ""


class SimulatorRequest(BaseModel):
    scenario: str

    seed: int = 42


SIMULATOR_ALIASES = {
    "normal":
        "normal",

    "rain":
        "heavy_rain",

    "vehicle":
        "vehicle",

    "machinery":
        "vehicle",

    "rain-vehicle":
        "mixed_rain_and_vehicle",

    "rain-machinery":
        "mixed_rain_and_machinery",

    "mining":
        "possible_mining",

    "critical":
        "high_risk_mining",

    "excavator":
        "excavator",

    "sensor-failure":
        "sensor_failure",

    "communication-failure":
        "communication_failure",
}


def _require_simulator_mode() -> None:
    mode = str(
        engine.agency_dispatcher.mode
    ).upper()

    if mode != "DEMO":
        raise HTTPException(
            403,
            (
                "GoldTrace simulator is available "
                "only while agency dispatch mode "
                "is DEMO."
            ),
        )


def _simulator_packet(
    packet: dict[str, Any],
    scenario: str,
) -> dict[str, Any]:
    return {
        **packet,

        "source":
            "SIMULATOR",

        "simulated":
            True,

        "simulation_scenario":
            scenario,
    }


# ============================================================
# HEALTH / SYSTEM
# ============================================================

def _running_on_raspberry_pi() -> bool:
    """
    Detect whether the GoldTrace backend itself is running
    on Raspberry Pi hardware.

    A successful GoldTrace API process on Windows/Linux does
    not imply that a Raspberry Pi is connected.
    """
    model_path = "/proc/device-tree/model"

    try:
        with open(
            model_path,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as handle:
            model = handle.read().lower()

        return "raspberry pi" in model
    except OSError:
        return False


def _hardware_env_status(
    variable: str,
) -> str:
    """
    Hardware peripherals must explicitly report/configure
    connectivity. Simulator packets never count as proof of
    physical hardware.
    """
    value = os.getenv(
        variable,
        "",
    ).strip().lower()

    if value in {
        "1",
        "true",
        "yes",
        "on",
        "connected",
    }:
        return "CONNECTED"

    return "NOT CONNECTED"


def _hardware_status() -> dict[str, str]:
    running_on_pi = (
        _running_on_raspberry_pi()
    )

    return {
        "runtime_host":
            (
                "RASPBERRY_PI"
                if running_on_pi
                else "DEVELOPMENT_HOST"
            ),

        "raspberry_pi":
            (
                "CONNECTED"
                if running_on_pi
                else "NOT CONNECTED"
            ),

        "lora":
            _hardware_env_status(
                "GOLDTRACE_LORA_CONNECTED"
            ),

        "cellular":
            _hardware_env_status(
                "GOLDTRACE_CELLULAR_CONNECTED"
            ),
    }


@app.get("/health")
def health():
    return {
        "system":
            "GoldTrace",

        "status":
            "healthy",

        "models_loaded":
            models.status(),

        "database":
            True,

        "agency_mode":
            engine.agency_dispatcher.mode,
    }


@app.get("/system/status")
def system_status():
    return {
        "system":
            "GoldTrace",

        "nodes_seen":
            sorted(
                latest_packets
            ),

        "hardware":
            _hardware_status(),

        "models":
            models.status(),

        "agency_mode":
            engine.agency_dispatcher.mode,

        "websocket_clients":
            len(
                manager.active_connections
            ),

        "timestamp":
            _utc_now(),
    }


# ============================================================
# MODELS / PREDICTIONS / EVENTS
# ============================================================

@app.get("/models")
def model_status():
    return models.registry


@app.get("/model-metrics")
def model_metrics():
    return {
        "note":
            "Run python -m src.evaluate to generate reports/model_evaluation.json"
    }


@app.get("/latest-prediction")
def latest_prediction():
    return (
        db.latest_prediction()
        or {}
    )


@app.get("/events")
def events(
    limit: int = 100,
):
    return db.list_predictions(
        limit
    )


@app.get("/events/{event_id}")
def event(
    event_id: str,
):
    item = db.get_prediction(
        event_id
    )

    if item:
        return item

    raise HTTPException(
        404,
        "event not found",
    )


# ============================================================
# ALERTS
# ============================================================

@app.get("/alerts")
def list_alerts():
    return db.list_alerts()


@app.get("/alerts/{alert_id}")
def get_alert(
    alert_id: int,
):
    item = db.get_alert(
        alert_id
    )

    if not item:
        raise HTTPException(
            404,
            "alert not found",
        )

    return item


@app.get(
    "/alerts/{alert_id}/deliveries"
)
def deliveries(
    alert_id: int,
):
    item = db.get_alert(
        alert_id
    )

    if not item:
        raise HTTPException(
            404,
            "alert not found",
        )

    return db.list_alert_deliveries(
        item.get(
            "event_id"
        )
    )


@app.post(
    "/alerts/{alert_id}/acknowledge"
)
def acknowledge(
    alert_id: int,
    req: AckRequest,
    x_goldtrace_admin_key: str | None = Header(
            default=None,
            alias="X-GoldTrace-Admin-Key",
        ),
):
    _require_admin(
        x_goldtrace_admin_key
    )

    item = db.acknowledge_alert(
        alert_id,
        req.acknowledged_by,
        req.notes,
    )

    if not item:
        raise HTTPException(
            404,
            "alert not found",
        )

    return item


@app.post(
    "/alerts/{alert_id}/retry"
)
def retry_alert(
    alert_id: int,
    x_goldtrace_admin_key: str | None = Header(
            default=None,
            alias="X-GoldTrace-Admin-Key",
        ),
):
    _require_admin(
        x_goldtrace_admin_key
    )

    if not db.get_alert(
        alert_id
    ):
        raise HTTPException(
            404,
            "alert not found",
        )

    return (
        engine
        .agency_dispatcher
        .retry_queue()
    )


@app.post(
    "/alerts/{alert_id}/dispatch"
)
def dispatch_alert(
    alert_id: int,
    x_goldtrace_admin_key: str | None = Header(
            default=None,
            alias="X-GoldTrace-Admin-Key",
        ),
):
    _require_admin(
        x_goldtrace_admin_key
    )

    item = db.get_alert(
        alert_id
    )

    if not item:
        raise HTTPException(
            404,
            "alert not found",
        )

    result = (
        item.get(
            "result"
        )
        or db.get_prediction(
            item.get(
                "event_id"
            )
        )
    )

    if not result:
        raise HTTPException(
            404,
            "event result not found",
        )

    return (
        engine
        .agency_dispatcher
        .dispatch(
            result,
            force=True,
        )
    )


# ============================================================
# AGENCY
# ============================================================

@app.get("/agency-recipients")
def agency_recipients(
    x_goldtrace_admin_key: str | None = Header(
            default=None,
            alias="X-GoldTrace-Admin-Key",
        ),
):
    _require_admin(
        x_goldtrace_admin_key
    )

    out = []

    for item in registry.list(
        True
    ):
        x = dict(
            item
        )

        if "phone" in x:
            x["phone"] = (
                _redact_destination(
                    x.get(
                        "phone"
                    )
                )
            )

        if "email" in x:
            x["email"] = (
                _redact_destination(
                    x.get(
                        "email"
                    )
                )
            )

        if "webhook_url" in x:
            x["webhook_url"] = (
                "configured"
                if x.get(
                    "webhook_url"
                )
                else None
            )

        out.append(
            x
        )

    return out


@app.get("/agency-alert/status")
def agency_alert_status():
    return {
        "mode":
            engine.agency_dispatcher.mode,

        "dispatches":
            db.list_agency_dispatches(
                20
            ),

        "queue":
            db.pending_alert_queue(),
    }


# ============================================================
# SENSOR HEALTH / NODES / RISK
# ============================================================

@app.get("/sensor-health")
def sensor_health():
    latest = (
        db.latest_prediction()
        or {}
    )

    return {
        k:
            v.get(
                "health"
            )

        for k, v
        in latest.get(
            "node_results",
            {},
        ).items()
    }


@app.get("/nodes")
def nodes():
    return topology.list_nodes()


@app.get("/risk")
def risk():
    latest = (
        db.latest_prediction()
        or {}
    )

    return {
        "risk_level":
            latest.get(
                "risk_level",
                "UNKNOWN",
            ),

        "prediction":
            latest.get(
                "prediction",
                "SYSTEM_UNCERTAIN",
            ),

        "confidence":
            latest.get(
                "confidence",
                0.0,
            ),
    }


# ============================================================
# MAP / GIS
# ============================================================

@app.get("/map/nodes")
def map_nodes():
    return topology.list_nodes()


@app.get("/map/rivers")
def map_rivers():
    return {
        "type":
            "FeatureCollection",

        "features":
            topology.list_segments(),
    }


@app.get("/map/segments")
def map_segments():
    return topology.list_segments()


@app.get("/map/events")
def map_events():
    return db.list_event_locations()


@app.get("/map/risk-zones")
def risk_zones():
    return db.list_risk_zones()


@app.get("/map/events/{event_id}")
def map_event(
    event_id: str,
):
    item = db.get_prediction(
        event_id
    )

    if not item:
        raise HTTPException(
            404,
            "event not found",
        )

    return geo.map_payload(
        item
    )


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
async def predict(
    req: PairRequest,
):
    result = engine.process_pair(
        req.node_a,
        req.node_b,
        req.persistence_seconds,
    )

    await _broadcast_result(
        result
    )

    return result


# ============================================================
# SENSOR INGESTION
# ============================================================

@app.post("/sensor-data")
async def sensor_data(
    packet: dict[
        str,
        Any
    ],
):
    node = str(
        packet.get(
            "node_id",
            "",
        )
    )

    if node not in {
        "NODE_A",
        "NODE_B",
    }:
        raise HTTPException(
            400,
            "node_id must be NODE_A or NODE_B",
        )

    # Preserve existing GoldTrace behaviour.
    latest_packets[
        node
    ] = packet

    pending_pair_nodes.add(
        node
    )

    # Push the new raw node packet immediately.
    await manager.broadcast({
        "type":
            "sensor_update",

        "data":
            packet,
    })

    await manager.broadcast({
        "type":
            "node_status",

        "data": {
            "node_id":
                node,

            "status":
                "ONLINE",

            "last_seen":
                packet.get(
                    "timestamp"
                )
                or packet.get(
                    "ts"
                )
                or _utc_now(),
        },
    })

    # Only process when both river nodes
    # have supplied a packet, exactly as before.
    if {
        "NODE_A",
        "NODE_B",
    }.issubset(
        pending_pair_nodes
    ):
        pending_pair_nodes.difference_update({
            "NODE_A",
            "NODE_B",
        })

        result = engine.process_pair(
            latest_packets[
                "NODE_A"
            ],
            latest_packets[
                "NODE_B"
            ],
        )

        await _broadcast_result(
            result
        )

        return result

    return {
        "accepted":
            True,

        "waiting_for_other_node":
            True,
    }


# ============================================================
# DEMO / PRESENTATION SIMULATOR
# ============================================================

@app.get("/simulator/scenarios")
def simulator_scenarios():
    _require_simulator_mode()

    settings = load_settings()

    risk_cfg = settings.get(
        "risk",
        {},
    )

    agency_cfg = settings.get(
        "agency_alerts",
        {},
    )

    risk_wait = float(
        risk_cfg.get(
            "critical_persistence_seconds",
            30,
        )
    )

    agency_wait = float(
        agency_cfg.get(
            "minimum_persistence_seconds",
            30,
        )
    )

    return {
        "mode":
            "DEMO",

        "source":
            "SIMULATOR",

        "aliases":
            SIMULATOR_ALIASES,

        "underlying_scenarios":
            SCENARIOS,

        "critical_wait_seconds":
            max(
                risk_wait,
                agency_wait,
            ) + 2.0,
    }


@app.post("/simulator/reset")
def simulator_reset(
    x_goldtrace_admin_key: str | None = Header(
        default=None,
        alias="X-GoldTrace-Admin-Key",
    ),
):
    _require_admin(
        x_goldtrace_admin_key
    )

    _require_simulator_mode()

    engine.persistence.reset()

    pending_pair_nodes.clear()

    return {
        "status":
            "RESET",

        "source":
            "SIMULATOR",

        "message":
            (
                "Simulator persistence state "
                "has been reset."
            ),
    }


@app.post("/simulator/run")
async def simulator_run(
    req: SimulatorRequest,

    x_goldtrace_admin_key: str | None = Header(
        default=None,
        alias="X-GoldTrace-Admin-Key",
    ),
):
    _require_admin(
        x_goldtrace_admin_key
    )

    _require_simulator_mode()

    alias = (
        req.scenario
        .strip()
        .lower()
    )

    scenario = (
        SIMULATOR_ALIASES.get(
            alias
        )
    )

    if not scenario:
        raise HTTPException(
            400,
            (
                "Unknown simulator scenario. "
                f"Available: "
                f"{', '.join(sorted(SIMULATOR_ALIASES))}"
            ),
        )

    timestamp = datetime.now(
        timezone.utc
    )

    node_a, node_b = (
        scenario_packets(
            scenario,
            seed=req.seed,
            timestamp=timestamp,
        )
    )

    node_a = _simulator_packet(
        node_a,
        scenario,
    )

    node_b = _simulator_packet(
        node_b,
        scenario,
    )

    # The simulator must always submit a fresh
    # A/B pair. It must never reuse a pending
    # packet from an earlier simulation.
    pending_pair_nodes.clear()

    first_response = await sensor_data(
        node_a
    )

    result = await sensor_data(
        node_b
    )

    return {
        "source":
            "SIMULATOR",

        "simulated":
            True,

        "alias":
            alias,

        "scenario":
            scenario,

        "node_a_response":
            first_response,

        "result":
            result,
    }


# ============================================================
# CALIBRATION
# ============================================================

@app.post("/calibrate")
def calibrate(
    payload: dict[
        str,
        Any
    ],
):
    node = str(
        payload.get(
            "node_id",
            "",
        )
    )

    records = payload.get(
        "records",
        [],
    )

    if (
        not node
        or not isinstance(
            records,
            list,
        )
    ):
        raise HTTPException(
            400,
            "node_id and records list required",
        )

    return BaselineManager(
        node
    ).calibrate(
        records
    )


# ============================================================
# LIVE WEBSOCKET
# ============================================================

@app.websocket("/ws/live")
async def websocket_live(
    websocket: WebSocket,
):
    await manager.connect(
        websocket
    )

    try:
        # ----------------------------------------------------
        # Send initial system snapshot
        # ----------------------------------------------------

        await websocket.send_json({
            "type":
                "system_status",

            "data":
                system_status(),
        })

        # ----------------------------------------------------
        # Send known node topology + latest raw packet
        # ----------------------------------------------------

        for node_meta in topology.list_nodes():
            node_id = str(
                node_meta.get(
                    "node_id",
                    "",
                )
            )

            snapshot = dict(
                node_meta
            )

            packet = latest_packets.get(
                node_id
            )

            if packet:
                snapshot.update(
                    packet
                )

                snapshot[
                    "status"
                ] = "ONLINE"

                snapshot[
                    "last_seen"
                ] = (
                    packet.get(
                        "timestamp"
                    )
                    or packet.get(
                        "ts"
                    )
                    or _utc_now()
                )

            else:
                snapshot[
                    "status"
                ] = "OFFLINE"

            await websocket.send_json({
                "type":
                    "sensor_update",

                "data":
                    snapshot,
            })

        # ----------------------------------------------------
        # Send latest prediction if available
        # ----------------------------------------------------

        latest = (
            db.latest_prediction()
            or {}
        )

        if latest:
            await websocket.send_json({
                "type":
                    "prediction_update",

                "data":
                    latest,
            })

            await websocket.send_json({
                "type":
                    "risk_update",

                "data": {
                    "event_id":
                        latest.get(
                            "event_id"
                        ),

                    "prediction":
                        latest.get(
                            "prediction",
                            "SYSTEM_UNCERTAIN",
                        ),

                    "risk_level":
                        latest.get(
                            "risk_level",
                            "UNKNOWN",
                        ),

                    "confidence":
                        latest.get(
                            "confidence",
                            0.0,
                        ),
                },
            })

        # ----------------------------------------------------
        # Send recent alert snapshot
        # ----------------------------------------------------

        try:
            recent_alerts = (
                db.list_alerts()
            )

        except Exception:
            recent_alerts = []

        for alert in recent_alerts[
            :20
        ]:
            await websocket.send_json({
                "type":
                    "alert",

                "data":
                    alert,
            })

        # ----------------------------------------------------
        # Keep connection alive
        # ----------------------------------------------------

        while True:
            await asyncio.sleep(
                15
            )

            await websocket.send_json({
                "type":
                    "heartbeat",

                "data": {
                    "timestamp":
                        _utc_now(),
                },
            })

    except WebSocketDisconnect:
        pass

    except Exception:
        pass

    finally:
        manager.disconnect(
            websocket
        )

