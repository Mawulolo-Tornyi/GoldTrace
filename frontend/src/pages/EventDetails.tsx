import {
  ArrowLeft,
  Clock3,
  MapPin,
  ShieldAlert,
} from "lucide-react";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  useQuery,
} from "@tanstack/react-query";

import { GoldTraceMap } from "../components/map/GoldTraceMap";

import {
  alertsApi,
  eventsApi,
  mapApi,
} from "../api/goldtraceApi";

import {
  normalizeAlerts,
  normalizeEvent,
  normalizePrediction,
} from "../api/normalizers";

import {
  normalizeHistoricalEventMap,
} from "../api/mapLayers";

import { useLiveStore } from "../store/liveStore";

import {
  percent,
  riskClass,
  valueWithUnit,
} from "../utils/formatters";


export default function EventDetails() {
  const { id } =
    useParams();

  const eventId =
    id ?? "";


  const storedEvents =
    useLiveStore(
      (state) =>
        state.events
    );

  const nodes =
    useLiveStore(
      (state) =>
        state.nodes
    );

  const livePrediction =
    useLiveStore(
      (state) =>
        state.prediction
    );

  const storedAlerts =
    useLiveStore(
      (state) =>
        state.alerts
    );


  const eventQuery =
    useQuery({
      queryKey: [
        "goldtrace",
        "event",
        eventId,
      ],

      enabled:
        Boolean(eventId),

      queryFn:
        async () => {
          const response =
            await eventsApi.one(
              eventId
            );

          return response.data;
        },

      staleTime:
        30_000,

      retry: 1,
    });


  const mapQuery =
    useQuery({
      queryKey: [
        "goldtrace",
        "event-map",
        eventId,
      ],

      enabled:
        Boolean(eventId),

      queryFn:
        async () => {
          const response =
            await mapApi.event(
              eventId
            );

          return response.data;
        },

      staleTime:
        30_000,

      retry: 1,
    });


  const alertsQuery =
    useQuery({
      queryKey: [
        "goldtrace",
        "alerts",
      ],

      queryFn:
        async () => {
          const response =
            await alertsApi.all();

          return response.data;
        },

      staleTime:
        15_000,

      retry: 1,
    });


  const storedEvent =
    storedEvents.find(
      (item) =>
        item.event_id ===
        eventId
    );


  const historicalEvent =
    eventQuery.data
      ? normalizeEvent(
          eventQuery.data
        )
      : null;


  const event =
    historicalEvent ??
    storedEvent;


  const historicalPrediction =
    eventQuery.data
      ? normalizePrediction(
          eventQuery.data
        )
      : null;


  /*
   * Never borrow another event's live
   * prediction.
   *
   * Live state is only a fallback when
   * its event_id matches this page.
   */
  const eventPrediction =
    historicalPrediction ??
    (
      livePrediction?.event_id ===
        eventId
        ? livePrediction
        : null
    );


  /*
   * Prefer the dedicated event map API.
   *
   * The full historical event response
   * also contains a map object, so it
   * provides a safe fallback.
   */
  const historicalMap =
    normalizeHistoricalEventMap(
      mapQuery.data ??
      eventQuery.data
    );


  const allAlerts =
    alertsQuery.data
      ? normalizeAlerts(
          alertsQuery.data
        )
      : storedAlerts;


  const relatedAlerts =
    allAlerts.filter(
      (alert) =>
        alert.event_id ===
        eventId
    );


  if (
    eventQuery.isPending &&
    !storedEvent
  ) {
    return (
      <div>
        <Link
          to="/events"
          className="back-link"
        >
          <ArrowLeft size={15} />
          Back to events
        </Link>

        <div className="empty-state">
          <strong>
            Loading event...
          </strong>

          <p>
            Retrieving historical
            GoldTrace data.
          </p>
        </div>
      </div>
    );
  }


  if (!event) {
    return (
      <div>
        <Link
          to="/events"
          className="back-link"
        >
          <ArrowLeft size={15} />
          Back to events
        </Link>

        <div className="empty-state">
          <strong>
            Event not found
          </strong>

          <p>
            The historical record
            could not be retrieved.
          </p>
        </div>
      </div>
    );
  }


  return (
    <div>
      <Link
        to="/events"
        className="back-link"
      >
        <ArrowLeft size={15} />
        Back to events
      </Link>


      <div className="details-heading">
        <div>
          <span className="eyebrow">
            GOLDTRACE HISTORICAL EVENT
          </span>

          <h2>
            {event.event_id}
          </h2>

          <p>
            {new Date(
              event.timestamp
            ).toLocaleString()}
          </p>

          {eventPrediction
            ?.human_description && (
            <p>
              {
                eventPrediction
                  .human_description
              }
            </p>
          )}
        </div>

        <span
          className={`risk-badge ${riskClass(
            event.risk
          )}`}
        >
          {event.risk}
        </span>
      </div>


      <div className="event-summary-grid">
        <article>
          <ShieldAlert
            size={18}
          />

          <span>
            Prediction
          </span>

          <strong>
            {event.prediction}
          </strong>
        </article>


        <article>
          <span>
            Confidence
          </span>

          <strong className="purple-text">
            {percent(
              event.confidence
            )}
          </strong>
        </article>


        <article>
          <MapPin
            size={18}
          />

          <span>
            Zone
          </span>

          <strong>
            {event.zone}
          </strong>
        </article>


        <article>
          <Clock3
            size={18}
          />

          <span>
            Persistence
          </span>

          <strong>
            {valueWithUnit(
              eventPrediction
                ?.duration_seconds ??
                event.duration_seconds,
              " s",
              0
            )}
          </strong>
        </article>
      </div>


      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              EVENT GIS
            </span>

            <h2>
              Historical Suspected Location
            </h2>
          </div>

          <span className="section-meta">
            {
              eventPrediction
                ?.river_segment ||
              "Unknown segment"
            }
          </span>
        </div>


        <div className="dashboard-map-card">
          <GoldTraceMap
            nodes={nodes}

            prediction={
              eventPrediction
            }

            riskZones={
              historicalMap.riskZones
            }

            mapEvents={
              historicalMap.eventPoints
            }

            height={500}
          />
        </div>
      </div>


      <div className="node-detail-grid dashboard-section">
        <article className="detail-panel">
          <span className="detail-label">
            EVENT EVIDENCE
          </span>

          <div className="evidence-stack">
            {eventPrediction &&
            eventPrediction.reasons.length >
              0 ? (
              eventPrediction.reasons.map(
                (
                  reason,
                  index
                ) => (
                  <div
                    key={`${index}-${reason}`}
                  >
                    <span>
                      ✓
                    </span>

                    {reason}
                  </div>
                )
              )
            ) : (
              <p className="muted-text">
                No historical evidence
                reasons were recorded.
              </p>
            )}
          </div>
        </article>


        <article className="detail-panel">
          <span className="detail-label">
            EVENT CONTEXT
          </span>

          <div className="detail-list">
            <div>
              <span>
                Segment
              </span>

              <strong>
                {
                  eventPrediction
                    ?.river_segment ||
                  "Unknown"
                }
              </strong>
            </div>

            <div>
              <span>
                Zone
              </span>

              <strong>
                {
                  event.zone ||
                  "Unknown"
                }
              </strong>
            </div>

            <div>
              <span>
                Risk
              </span>

              <strong>
                {event.risk}
              </strong>
            </div>

            <div>
              <span>
                Recommendation
              </span>

              <strong>
                {
                  eventPrediction
                    ?.recommendation ||
                  "No recommendation recorded"
                }
              </strong>
            </div>
          </div>
        </article>
      </div>


      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              ALERT HISTORY
            </span>

            <h2>
              Related Alerts
            </h2>
          </div>
        </div>


        <div className="detail-panel">
          <div className="detail-list">
            {relatedAlerts.length >
            0 ? (
              relatedAlerts.map(
                (alert) => (
                  <div
                    key={
                      alert.alert_id
                    }
                  >
                    <span>
                      {
                        alert.alert_id
                      }
                    </span>

                    <strong>
                      {
                        alert.status
                      }
                    </strong>
                  </div>
                )
              )
            ) : (
              <div>
                <span>
                  Alerts
                </span>

                <strong>
                  None recorded
                </strong>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
