import type { RiskLevel } from "../types";

import {
  normalizeRisk,
} from "./normalizers";


type UnknownObject =
  Record<string, unknown>;


export interface MapLineLayer {
  id: string;

  kind:
    | "river"
    | "segment"
    | "risk";

  segment_id: string;

  river_id: string;

  river_name: string;

  event_id: string;

  risk: RiskLevel;

  positions:
    [number, number][];

  properties:
    Record<string, unknown>;
}


export interface MapEventPoint {
  event_id: string;

  segment_id: string;

  zone_code: string;

  river_id: string;

  river_name: string;

  latitude: number;

  longitude: number;
}


function objectOf(
  value: unknown
): UnknownObject {
  if (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  ) {
    return value as UnknownObject;
  }

  return {};
}


function textFrom(
  ...values: unknown[]
): string {
  for (const value of values) {
    if (
      typeof value === "string" &&
      value.trim()
    ) {
      return value.trim();
    }

    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {
      return String(value);
    }
  }

  return "";
}


function numberFrom(
  ...values: unknown[]
): number {
  for (const value of values) {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      continue;
    }

    const result =
      Number(value);

    if (Number.isFinite(result)) {
      return result;
    }
  }

  return Number.NaN;
}


function featureList(
  value: unknown
): UnknownObject[] {
  if (Array.isArray(value)) {
    return value.map(
      (item) =>
        objectOf(item)
    );
  }

  const raw =
    objectOf(value);

  if (
    raw.type === "FeatureCollection" &&
    Array.isArray(raw.features)
  ) {
    return raw.features.map(
      (item) =>
        objectOf(item)
    );
  }

  if (
    raw.type === "Feature"
  ) {
    return [raw];
  }

  return [];
}


function linePositions(
  featureValue: unknown
): [number, number][] {
  const feature =
    objectOf(featureValue);

  const geometry =
    objectOf(
      feature.geometry
    );

  if (
    geometry.type !== "LineString" ||
    !Array.isArray(
      geometry.coordinates
    )
  ) {
    return [];
  }

  const positions:
    [number, number][] = [];

  for (
    const coordinate
    of geometry.coordinates
  ) {
    if (
      !Array.isArray(coordinate) ||
      coordinate.length < 2
    ) {
      continue;
    }

    /*
     * GeoJSON uses:
     * [longitude, latitude]
     *
     * Leaflet uses:
     * [latitude, longitude]
     */
    const longitude =
      numberFrom(
        coordinate[0]
      );

    const latitude =
      numberFrom(
        coordinate[1]
      );

    if (
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude)
    ) {
      continue;
    }

    positions.push([
      latitude,
      longitude,
    ]);
  }

  return positions;
}


function normalizeFeatureLine(
  featureValue: unknown,
  kind:
    | "river"
    | "segment"
    | "risk",
  index: number,
  externalRisk?: unknown,
  externalEventId?: unknown
): MapLineLayer | null {
  const feature =
    objectOf(featureValue);

  const properties =
    objectOf(
      feature.properties
    );

  const positions =
    linePositions(feature);

  if (
    positions.length < 2
  ) {
    return null;
  }

  const segmentId =
    textFrom(
      properties.segment_id
    );

  const riverId =
    textFrom(
      properties.river_id
    );

  const eventId =
    textFrom(
      externalEventId,
      properties.event_id
    );

  return {
    id:
      eventId
        ? `${kind}-${eventId}-${segmentId || index}`
        : `${kind}-${segmentId || riverId || index}`,

    kind,

    segment_id:
      segmentId,

    river_id:
      riverId,

    river_name:
      textFrom(
        properties.river_name
      ),

    event_id:
      eventId,

    risk:
      normalizeRisk(
        externalRisk ??
          properties.risk
      ),

    positions,

    properties,
  };
}


export function normalizeRiverLines(
  value: unknown
): MapLineLayer[] {
  return featureList(value)
    .map(
      (feature, index) =>
        normalizeFeatureLine(
          feature,
          "river",
          index
        )
    )
    .filter(
      (
        item
      ): item is MapLineLayer =>
        item !== null
    );
}


export function normalizeSegmentLines(
  value: unknown
): MapLineLayer[] {
  return featureList(value)
    .map(
      (feature, index) =>
        normalizeFeatureLine(
          feature,
          "segment",
          index
        )
    )
    .filter(
      (
        item
      ): item is MapLineLayer =>
        item !== null
    );
}


const riskRank:
  Record<RiskLevel, number> = {
    UNKNOWN: 0,
    LOW: 1,
    MEDIUM: 2,
    HIGH: 3,
    CRITICAL: 4,
  };


export function normalizeRiskLines(
  value: unknown
): MapLineLayer[] {
  const input =
    Array.isArray(value)
      ? value
      : value
      ? [value]
      : [];

  /*
   * The current backend can return repeated
   * prediction rows for one event/segment.
   *
   * Since these rows do not contain a timestamp,
   * collapse duplicate overlays and retain the
   * strongest recorded risk for that event/segment.
   *
   * The live Prediction still remains authoritative
   * for the current operational risk.
   */
  const unique =
    new Map<
      string,
      MapLineLayer
    >();

  input.forEach(
    (item, index) => {
      const raw =
        objectOf(item);

      const feature =
        objectOf(
          raw.geojson
        );

      const layer =
        normalizeFeatureLine(
          feature,
          "risk",
          index,
          raw.risk,
          raw.event_id
        );

      if (!layer) {
        return;
      }

      const key =
        `${layer.event_id}|${layer.segment_id}`;

      const current =
        unique.get(key);

      if (
        !current ||
        riskRank[layer.risk] >
          riskRank[current.risk]
      ) {
        unique.set(
          key,
          layer
        );
      }
    }
  );

  return Array.from(
    unique.values()
  );
}


export function normalizeMapEvents(
  value: unknown
): MapEventPoint[] {
  const input =
    Array.isArray(value)
      ? value
      : value
      ? [value]
      : [];

  const unique =
    new Map<
      string,
      MapEventPoint
    >();

  for (const item of input) {
    const raw =
      objectOf(item);

    const eventId =
      textFrom(
        raw.event_id
      );

    if (!eventId) {
      continue;
    }

    const location =
      objectOf(
        raw.location
      );

    const centroid =
      objectOf(
        location.centroid
      );

    const latitude =
      numberFrom(
        centroid.latitude
      );

    const longitude =
      numberFrom(
        centroid.longitude
      );

    if (
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude)
    ) {
      continue;
    }

    unique.set(
      eventId,
      {
        event_id:
          eventId,

        segment_id:
          textFrom(
            location.segment_id
          ),

        zone_code:
          textFrom(
            location.zone_code
          ),

        river_id:
          textFrom(
            location.river_id
          ),

        river_name:
          textFrom(
            location.river_name
          ),

        latitude,

        longitude,
      }
    );
  }

  return Array.from(
    unique.values()
  );
}


export interface HistoricalEventMapData {
  riskZones: MapLineLayer[];
  eventPoints: MapEventPoint[];
}


export function normalizeHistoricalEventMap(
  value: unknown
): HistoricalEventMapData {
  const raw =
    objectOf(value);

  const map =
    objectOf(
      raw.map
    );

  const suspectedSegment =
    objectOf(
      map.suspected_segment
    );

  const geojson =
    objectOf(
      suspectedSegment.geojson
    );

  const properties =
    objectOf(
      geojson.properties
    );

  const eventId =
    textFrom(
      raw.event_id,
      properties.event_id
    );


  const riskZones =
    suspectedSegment.geojson
      ? normalizeRiskLines([
          {
            event_id:
              eventId,

            risk:
              suspectedSegment.risk ??
              properties.risk,

            geojson:
              suspectedSegment.geojson,
          },
        ])
      : [];


  const center =
    Array.isArray(map.center)
      ? map.center
      : [];

  const latitude =
    numberFrom(
      center[0]
    );

  const longitude =
    numberFrom(
      center[1]
    );


  const eventPoints:
    MapEventPoint[] = [];


  if (
    eventId &&
    Number.isFinite(latitude) &&
    Number.isFinite(longitude)
  ) {
    eventPoints.push({
      event_id:
        eventId,

      segment_id:
        textFrom(
          suspectedSegment.segment_id,
          properties.segment_id
        ),

      zone_code:
        textFrom(
          properties.zone_code
        ),

      river_id:
        textFrom(
          properties.river_id
        ),

      river_name:
        textFrom(
          properties.river_name
        ),

      latitude,
      longitude,
    });
  }


  return {
    riskZones,
    eventPoints,
  };
}
