import {
  Layers3,
  MapPinned,
} from "lucide-react";

import {
  useQuery,
} from "@tanstack/react-query";

import { GoldTraceMap } from "../components/map/GoldTraceMap";

import {
  mapApi,
} from "../api/goldtraceApi";

import {
  normalizeMapEvents,
  normalizeRiskLines,
  normalizeRiverLines,
  normalizeSegmentLines,
} from "../api/mapLayers";

import { useLiveStore } from "../store/liveStore";


export default function MapView() {
  const nodes =
    useLiveStore(
      (state) =>
        state.nodes
    );

  const prediction =
    useLiveStore(
      (state) =>
        state.prediction
    );


  const riversQuery =
    useQuery({
      queryKey: [
        "goldtrace",
        "map",
        "rivers",
      ],

      queryFn:
        async () => {
          const response =
            await mapApi.rivers();

          return normalizeRiverLines(
            response.data
          );
        },

      staleTime:
        5 * 60 * 1000,

      retry: 1,
    });


  const segmentsQuery =
    useQuery({
      queryKey: [
        "goldtrace",
        "map",
        "segments",
      ],

      queryFn:
        async () => {
          const response =
            await mapApi.segments();

          return normalizeSegmentLines(
            response.data
          );
        },

      staleTime:
        5 * 60 * 1000,

      retry: 1,
    });


  const eventsQuery =
    useQuery({
      queryKey: [
        "goldtrace",
        "map",
        "events",
      ],

      queryFn:
        async () => {
          const response =
            await mapApi.events();

          return normalizeMapEvents(
            response.data
          );
        },

      refetchInterval:
        15000,

      retry: 1,
    });


  const riskZonesQuery =
    useQuery({
      queryKey: [
        "goldtrace",
        "map",
        "risk-zones",
      ],

      queryFn:
        async () => {
          const response =
            await mapApi.riskZones();

          return normalizeRiskLines(
            response.data
          );
        },

      refetchInterval:
        15000,

      retry: 1,
    });


  const rivers =
    riversQuery.data ?? [];

  const segments =
    segmentsQuery.data ?? [];

  const mapEvents =
    eventsQuery.data ?? [];

  const riskZones =
    riskZonesQuery.data ?? [];


  const upstream =
    [...nodes]
      .sort(
        (a, b) =>
          a.position_order -
          b.position_order
      )[0];


  const downstream =
    [...nodes]
      .sort(
        (a, b) =>
          b.position_order -
          a.position_order
      )[0];


  const gisUnavailable =
    riversQuery.isError &&
    segmentsQuery.isError &&
    eventsQuery.isError &&
    riskZonesQuery.isError;


  return (
    <div>
      <div className="page-heading map-page-heading">
        <div>
          <span className="eyebrow">
            OPERATIONAL GIS
          </span>

          <h2>
            River Intelligence Map
          </h2>

          <p>
            Live sensor nodes, real river
            geometry, monitored segments,
            historical events and investigation
            zones.
          </p>
        </div>

        <div className="map-page-actions">
          <span>
            <MapPinned
              size={14}
            />

            {nodes.length}
            {" "}
            nodes
          </span>

          <span>
            <Layers3
              size={14}
            />

            {
              gisUnavailable
                ? "Topology fallback"
                : `${rivers.length + segments.length + riskZones.length} GIS layers`
            }
          </span>
        </div>
      </div>


      <div className="map-page-card">
        <GoldTraceMap
          nodes={nodes}

          prediction={
            prediction
          }

          rivers={
            rivers
          }

          segments={
            segments
          }

          riskZones={
            riskZones
          }

          mapEvents={
            mapEvents
          }

          height={680}
        />
      </div>


      {gisUnavailable && (
        <div className="offline-map-indicator">
          GIS API layers unavailable — using
          live node topology fallback.
        </div>
      )}


      <div className="map-information-grid">
        <article>
          <span>
            UPSTREAM
          </span>

          <strong>
            {
              upstream?.node_id ||
              "Unknown"
            }
          </strong>
        </article>


        <article>
          <span>
            DOWNSTREAM
          </span>

          <strong>
            {
              downstream?.node_id ||
              "Unknown"
            }
          </strong>
        </article>


        <article>
          <span>
            SUSPECTED SEGMENT
          </span>

          <strong>
            {
              prediction?.river_segment ||
              "None"
            }
          </strong>
        </article>


        <article>
          <span>
            CURRENT RISK
          </span>

          <strong>
            {
              prediction?.risk ||
              "UNKNOWN"
            }
          </strong>
        </article>
      </div>


      <div className="map-information-grid">
        <article>
          <span>
            RIVER LAYERS
          </span>

          <strong>
            {rivers.length}
          </strong>
        </article>


        <article>
          <span>
            MONITORED SEGMENTS
          </span>

          <strong>
            {segments.length}
          </strong>
        </article>


        <article>
          <span>
            EVENT LOCATIONS
          </span>

          <strong>
            {mapEvents.length}
          </strong>
        </article>


        <article>
          <span>
            RISK ZONES
          </span>

          <strong>
            {riskZones.length}
          </strong>
        </article>
      </div>
    </div>
  );
}
