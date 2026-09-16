import {
  CheckCircle2,
  MessageSquareText,
  ShieldAlert,
} from "lucide-react";

import {
  useState,
} from "react";

import { toast } from "sonner";

import { alertsApi } from "../api/goldtraceApi";

import { useLiveStore } from "../store/liveStore";

import {
  riskClass,
} from "../utils/formatters";

export default function Alerts() {
  const alerts =
    useLiveStore(
      (state) =>
        state.alerts
    );

  const demoMode =
    useLiveStore(
      (state) =>
        state.demoMode
    );

  const acknowledgeLocal =
    useLiveStore(
      (state) =>
        state.acknowledgeAlertLocally
    );

  const [notes, setNotes] =
    useState<
      Record<string, string>
    >({});

  const [loading, setLoading] =
    useState<string | null>(
      null
    );

  async function acknowledge(
    alertId: string
  ) {
    const note =
      notes[alertId]?.trim() ||
      "";

    setLoading(alertId);

    try {
      if (demoMode) {
        acknowledgeLocal(
          alertId,
          note
        );

        toast.success(
          "Demo alert acknowledged"
        );

        return;
      }

      await alertsApi.acknowledge(
        alertId,
        note
      );

      acknowledgeLocal(
        alertId,
        note
      );

      toast.success(
        "Alert acknowledged successfully"
      );
    } catch (error) {
      console.error(
        error
      );

      toast.error(
        "Unable to acknowledge alert",
        {
          description:
            "The backend did not confirm the acknowledgement.",
        }
      );
    } finally {
      setLoading(null);
    }
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            RESPONSE MANAGEMENT
          </span>

          <h2>
            Alerts
          </h2>

          <p>
            Review and acknowledge GoldTrace
            operational alerts.
          </p>
        </div>
      </div>

      <div className="alert-list">
        {alerts.map(
          (alert) => (
            <article
              className="response-alert-card"
              key={
                alert.alert_id
              }
            >
              <div className="alert-main">
                <div className="alert-title-row">
                  <div>
                    <span
                      className={`risk-badge ${riskClass(
                        alert.severity
                      )}`}
                    >
                      {
                        alert.severity
                      }
                    </span>

                    <h3>
                      {
                        alert.alert_id
                      }
                    </h3>
                  </div>

                  <ShieldAlert
                    size={22}
                  />
                </div>

                <p>
                  {alert.message}
                </p>

                <div className="alert-metadata">
                  <span>
                    Event:{" "}
                    <strong>
                      {
                        alert.event_id
                      }
                    </strong>
                  </span>

                  <span>
                    Location:{" "}
                    <strong>
                      {
                        alert.location
                      }
                    </strong>
                  </span>

                  <span>
                    Time:{" "}
                    <strong>
                      {new Date(
                        alert.timestamp
                      ).toLocaleString()}
                    </strong>
                  </span>
                </div>
              </div>

              <div className="alert-response">
                <span className="detail-label">
                  RESPONSE STATUS
                </span>

                <strong
                  className={`alert-status status-${alert.status.toLowerCase()}`}
                >
                  {alert.status}
                </strong>

                {alert.status ===
                  "ACTIVE" && (
                  <>
                    <label>
                      <MessageSquareText
                        size={14}
                      />

                      Response note
                    </label>

                    <textarea
                      value={
                        notes[
                          alert.alert_id
                        ] || ""
                      }
                      onChange={(
                        event
                      ) =>
                        setNotes(
                          (
                            current
                          ) => ({
                            ...current,

                            [alert.alert_id]:
                              event
                                .target
                                .value,
                          })
                        )
                      }
                      placeholder="Example: Field team dispatched."
                    />

                    <button
                      className="acknowledge-button"
                      disabled={
                        loading ===
                        alert.alert_id
                      }
                      onClick={() =>
                        acknowledge(
                          alert.alert_id
                        )
                      }
                    >
                      <CheckCircle2
                        size={15}
                      />

                      {loading ===
                      alert.alert_id
                        ? "Acknowledging..."
                        : "Acknowledge Alert"}
                    </button>
                  </>
                )}

                {alert.status ===
                  "ACKNOWLEDGED" && (
                  <div className="acknowledged-details">
                    <span>
                      <CheckCircle2
                        size={14}
                      />
                      Acknowledged
                    </span>

                    {alert.acknowledgement_note && (
                      <p>
                        {
                          alert.acknowledgement_note
                        }
                      </p>
                    )}
                  </div>
                )}
              </div>
            </article>
          )
        )}

        {alerts.length ===
          0 && (
          <div className="empty-state">
            <CheckCircle2
              size={30}
            />

            <strong>
              No alerts
            </strong>

            <p>
              No GoldTrace response alerts are
              currently available.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
