import {
  CircleMarker,
  MapContainer,
  Popup,
  Polyline,
  TileLayer,
  useMap,
} from "react-leaflet";

import type {
  LatLngExpression,
} from "leaflet";

import L from "leaflet";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import "leaflet/dist/leaflet.css";

import type {
  Prediction,
  SensorNode,
} from "../../types";

import type {
  MapEventPoint,
  MapLineLayer,
} from "../../api/mapLayers";

import {
  GoldTraceGisLayers,
} from "./GoldTraceGisLayers";

import {
  integerWithUnit,
  percent,
  relativeTime,
  valueWithUnit,
} from "../../utils/formatters";

interface Props {
  nodes: SensorNode[];
  prediction: Prediction | null;

  rivers?: MapLineLayer[];
  segments?: MapLineLayer[];
  riskZones?: MapLineLayer[];
  mapEvents?: MapEventPoint[];

  height?: number;
}

function riskColor(
  risk?: string
): string {
  switch (risk) {
    case "CRITICAL":
      return "#ef4444";

    case "HIGH":
      return "#f97316";

    case "MEDIUM":
      return "#eab308";

    case "LOW":
      return "#22c55e";

    default:
      return "#64748b";
  }
}

function nodeColor(
  node: SensorNode
): string {
  if (
    node.status === "OFFLINE" ||
    node.status === "STALE"
  ) {
    return "#64748b";
  }

  return riskColor(
    node.risk
  );
}

function FitNodes({
  positions,
}: {
  positions: [
    number,
    number
  ][];
}) {
  const map = useMap();

  useEffect(() => {
    if (
      positions.length === 0
    ) {
      return;
    }

    if (
      positions.length === 1
    ) {
      map.setView(
        positions[0],
        16
      );

      return;
    }

    const bounds =
      L.latLngBounds(
        positions.map(
          ([lat, lng]) =>
            L.latLng(
              lat,
              lng
            )
        )
      );

    map.fitBounds(
      bounds,
      {
        padding: [45, 45],
        maxZoom: 16,
      }
    );
  }, [
    map,
    positions,
  ]);

  return null;
}

export function GoldTraceMap({
  nodes,
  prediction,
  rivers = [],
  segments = [],
  riskZones = [],
  mapEvents = [],
  height = 470,
}: Props) {
  const [tileFailure, setTileFailure] =
    useState(false);

  const orderedNodes =
    useMemo(
      () =>
        [...nodes]
          .filter(
            (node) =>
              Number.isFinite(
                node.latitude
              ) &&
              Number.isFinite(
                node.longitude
              )
          )
          .sort(
            (a, b) =>
              a.position_order -
              b.position_order
          ),
      [nodes]
    );

  const positions:
    [number, number][] =
      useMemo(
        () =>
          orderedNodes.map(
            (node) => [
              node.latitude,
              node.longitude,
            ]
          ),
        [orderedNodes]
      );

  const center:
    LatLngExpression =
      positions.length > 0
        ? positions[0]
        : [
            7.9465,
            -1.0232,
          ];

  const risk =
    prediction?.risk ||
    "UNKNOWN";

  return (
    <div
      className="goldtrace-map-shell"
      style={{ height }}
    >
      <MapContainer
        center={center}
        zoom={7}
        scrollWheelZoom
        className="goldtrace-map"
      >
        {!tileFailure && (
          <TileLayer
            attribution="© OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            eventHandlers={{
              tileerror: () =>
                setTileFailure(
                  true
                ),
            }}
          />
        )}

        <FitNodes
          positions={positions}
        />

        <GoldTraceGisLayers
          rivers={rivers}
          segments={segments}
          riskZones={riskZones}
          events={mapEvents}
        />

        {rivers.length === 0 &&
          segments.length === 0 &&
          positions.length >=
            2 && (
          <>
            <Polyline
              positions={
                positions
              }
              pathOptions={{
                color:
                  "#173f2a",
                weight: 12,
                opacity: 0.32,
              }}
            />

            <Polyline
              positions={
                positions
              }
              pathOptions={{
                color:
                  riskColor(
                    risk
                  ),

                weight:
                  risk ===
                  "CRITICAL"
                    ? 7
                    : 5,

                opacity: 0.92,

                dashArray:
                  risk === "LOW"
                    ? undefined
                    : "10 7",
              }}
            />
          </>
        )}

        {orderedNodes.map(
          (node) => (
            <CircleMarker
              key={
                node.node_id
              }
              center={[
                node.latitude,
                node.longitude,
              ]}
              radius={
                node.risk ===
                "CRITICAL"
                  ? 12
                  : 10
              }
              pathOptions={{
                color:
                  nodeColor(
                    node
                  ),

                fillColor:
                  "#07100a",

                fillOpacity:
                  0.95,

                weight: 4,
              }}
            >
              <Popup>
                <div className="map-popup">
                  <strong>
                    {
                      node.node_id
                    }
                  </strong>

                  <span>
                    {
                      node.position_type
                    }
                  </span>

                  <hr />

                  <p>
                    Status:{" "}
                    <b>
                      {
                        node.status
                      }
                    </b>
                  </p>

                  <p>
                    Risk:{" "}
                    <b>
                      {
                        node.risk
                      }
                    </b>
                  </p>

                  <p>
                    Turbidity:{" "}
                    <b>
                      {valueWithUnit(
                        node.turbidity,
                        " NTU",
                        1
                      )}
                    </b>
                  </p>

                  <p>
                    Audio:{" "}
                    <b>
                      {
                        node.audio_class
                      }
                    </b>
                  </p>

                  <p>
                    Machine:{" "}
                    <b>
                      {percent(
                        node.audio_machine_probability
                      )}
                    </b>
                  </p>

                  <p>
                    Vibration:{" "}
                    <b>
                      {
                        node.vibration_class
                      }
                    </b>
                  </p>

                  <p>
                    Battery:{" "}
                    <b>
                      {integerWithUnit(
                        node.battery,
                        "%"
                      )}
                    </b>
                  </p>

                  <p>
                    LoRa:{" "}
                    <b>
                      {integerWithUnit(
                        node.rssi,
                        " dBm"
                      )}
                    </b>
                  </p>

                  <p>
                    Last seen:{" "}
                    <b>
                      {relativeTime(
                        node.last_seen
                      )}
                    </b>
                  </p>
                </div>
              </Popup>
            </CircleMarker>
          )
        )}

        {prediction &&
          positions.length >=
            2 &&
          prediction.suspected_zone && (
            <CircleMarker
              center={[
                positions.reduce(
                  (
                    total,
                    item
                  ) =>
                    total +
                    item[0],
                  0
                ) /
                  positions.length,

                positions.reduce(
                  (
                    total,
                    item
                  ) =>
                    total +
                    item[1],
                  0
                ) /
                  positions.length,
              ]}
              radius={16}
              pathOptions={{
                color:
                  riskColor(
                    prediction.risk
                  ),

                fillColor:
                  riskColor(
                    prediction.risk
                  ),

                fillOpacity:
                  0.12,

                weight: 2,
              }}
            >
              <Popup>
                <div className="map-popup">
                  <strong>
                    SUSPECTED ZONE
                  </strong>

                  <hr />

                  <p>
                    {
                      prediction.suspected_zone
                    }
                  </p>

                  <p>
                    Segment:{" "}
                    <b>
                      {
                        prediction.river_segment
                      }
                    </b>
                  </p>

                  <p>
                    Risk:{" "}
                    <b>
                      {
                        prediction.risk
                      }
                    </b>
                  </p>

                  <p>
                    Confidence:{" "}
                    <b>
                      {percent(
                        prediction.confidence
                      )}
                    </b>
                  </p>

                  <p>
                    Event:{" "}
                    <b>
                      {
                        prediction.event_id
                      }
                    </b>
                  </p>

                  <p>
                    Duration:{" "}
                    <b>
                      {valueWithUnit(
                        prediction.duration_seconds,
                        " s",
                        0
                      )}
                    </b>
                  </p>
                </div>
              </Popup>
            </CircleMarker>
          )}
      </MapContainer>

      {tileFailure && (
        <div className="offline-map-indicator">
          OFFLINE TOPOLOGY MODE — map tiles unavailable
        </div>
      )}

      <div className="map-legend">
        <span>
          <i className="legend-dot safe" />
          Safe
        </span>

        <span>
          <i className="legend-dot suspicious" />
          Suspicious
        </span>

        <span>
          <i className="legend-dot high" />
          High
        </span>

        <span>
          <i className="legend-dot critical" />
          Critical
        </span>

        <span>
          <i className="legend-dot offline" />
          Offline
        </span>
      </div>
    </div>
  );
}



