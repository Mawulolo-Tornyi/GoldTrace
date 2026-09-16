import {
  CircleMarker,
  Popup,
  Polyline,
} from "react-leaflet";

import type {
  MapEventPoint,
  MapLineLayer,
} from "../../api/mapLayers";


interface Props {
  rivers: MapLineLayer[];
  segments: MapLineLayer[];
  riskZones: MapLineLayer[];
  events: MapEventPoint[];
}


function riskColor(
  risk: string
): string {
  switch (risk) {
    case "CRITICAL":
      return "#dc2626";

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


export function GoldTraceGisLayers({
  rivers,
  segments,
  riskZones,
  events,
}: Props) {
  return (
    <>
      {/* Real river geometry from backend GeoJSON */}
      {rivers.map(
        (river) => (
          <Polyline
            key={river.id}
            positions={
              river.positions
            }
            pathOptions={{
              color:
                "#173f2a",

              weight:
                11,

              opacity:
                0.28,

              lineCap:
                "round",
            }}
          >
            <Popup>
              <div className="map-popup">
                <strong>
                  {
                    river.river_name ||
                    "Monitored River"
                  }
                </strong>

                <hr />

                <p>
                  River ID:{" "}
                  <b>
                    {
                      river.river_id ||
                      "Unknown"
                    }
                  </b>
                </p>

                <p>
                  Segment:{" "}
                  <b>
                    {
                      river.segment_id ||
                      "Unknown"
                    }
                  </b>
                </p>
              </div>
            </Popup>
          </Polyline>
        )
      )}


      {/* Monitored sensor segment topology */}
      {segments.map(
        (segment) => (
          <Polyline
            key={segment.id}
            positions={
              segment.positions
            }
            pathOptions={{
              color:
                "#22c55e",

              weight:
                3,

              opacity:
                0.82,

              dashArray:
                "8 8",
            }}
          >
            <Popup>
              <div className="map-popup">
                <strong>
                  MONITORED SEGMENT
                </strong>

                <hr />

                <p>
                  {
                    segment.segment_id ||
                    "Unknown segment"
                  }
                </p>

                <p>
                  River:{" "}
                  <b>
                    {
                      segment.river_name ||
                      segment.river_id ||
                      "Unknown"
                    }
                  </b>
                </p>
              </div>
            </Popup>
          </Polyline>
        )
      )}


      {/* Historical/current backend risk-zone overlays */}
      {riskZones.map(
        (zone) => (
          <Polyline
            key={zone.id}
            positions={
              zone.positions
            }
            pathOptions={{
              color:
                riskColor(
                  zone.risk
                ),

              weight:
                zone.risk ===
                "CRITICAL"
                  ? 8
                  : 6,

              opacity:
                0.88,

              dashArray:
                zone.risk ===
                "LOW"
                  ? undefined
                  : "12 7",
            }}
          >
            <Popup>
              <div className="map-popup">
                <strong>
                  RISK ZONE
                </strong>

                <hr />

                <p>
                  Event:{" "}
                  <b>
                    {
                      zone.event_id ||
                      "Unknown"
                    }
                  </b>
                </p>

                <p>
                  Segment:{" "}
                  <b>
                    {
                      zone.segment_id ||
                      "Unknown"
                    }
                  </b>
                </p>

                <p>
                  Risk:{" "}
                  <b>
                    {zone.risk}
                  </b>
                </p>
              </div>
            </Popup>
          </Polyline>
        )
      )}


      {/* Historical event centroids */}
      {events.map(
        (event) => (
          <CircleMarker
            key={
              event.event_id
            }
            center={[
              event.latitude,
              event.longitude,
            ]}
            radius={7}
            pathOptions={{
              color:
                "#a855f7",

              fillColor:
                "#7e22ce",

              fillOpacity:
                0.75,

              weight:
                2,
            }}
          >
            <Popup>
              <div className="map-popup">
                <strong>
                  EVENT LOCATION
                </strong>

                <hr />

                <p>
                  {
                    event.event_id
                  }
                </p>

                <p>
                  Segment:{" "}
                  <b>
                    {
                      event.segment_id ||
                      "Unknown"
                    }
                  </b>
                </p>

                <p>
                  Zone:{" "}
                  <b>
                    {
                      event.zone_code ||
                      "Unknown"
                    }
                  </b>
                </p>

                <p>
                  River:{" "}
                  <b>
                    {
                      event.river_name ||
                      event.river_id ||
                      "Unknown"
                    }
                  </b>
                </p>
              </div>
            </Popup>
          </CircleMarker>
        )
      )}
    </>
  );
}
