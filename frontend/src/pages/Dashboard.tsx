import {
  Activity,
  BrainCircuit,
  MapPin,
  RadioTower,
  ShieldAlert,
} from "lucide-react";

import { MetricCard } from "../components/common/MetricCard";
import { NodeCard } from "../components/dashboard/NodeCard";
import { GoldTraceMap } from "../components/map/GoldTraceMap";
import { LiveTelemetryCharts } from "../components/charts/LiveTelemetryCharts";

import { useLiveStore } from "../store/liveStore";

import {
  percent,
  riskClass,
} from "../utils/formatters";

export default function Dashboard() {
  const nodes = useLiveStore(
    (state) => state.nodes
  );

  const prediction = useLiveStore(
    (state) => state.prediction
  );

  const alerts = useLiveStore(
    (state) => state.alerts
  );

  const connected = useLiveStore(
    (state) => state.connected
  );

  const demoMode = useLiveStore(
    (state) => state.demoMode
  );

  const lastUpdate = useLiveStore(
    (state) => state.lastUpdate
  );

  const system = useLiveStore(
    (state) => state.system
  );

  const activeAlerts =
    alerts.filter(
      (alert) =>
        alert.status === "ACTIVE"
    ).length;

  return (
    <div className="dashboard">
      <section className="hero-status">
        <div>
          <span className="eyebrow">
            CURRENT RIVER INTELLIGENCE
          </span>

          <h2>
            Detect the activity.
            Trace the source.
            Protect the river.
          </h2>

          <p>
            GoldTrace combines river turbidity,
            acoustic signatures, ground vibration
            and machine learning to identify and
            localize suspicious activity.
          </p>
        </div>

        <div className="hero-meta">
          <span>
            {demoMode
              ? "DEMO DATA"
              : connected
              ? "LIVE SENSOR DATA"
              : "NO LIVE CONNECTION"}
          </span>

          <small>
            Last update:{" "}
            {lastUpdate
              ? new Date(
                  lastUpdate
                ).toLocaleTimeString()
              : "Never"}
          </small>
        </div>
      </section>

      <section className="metrics-grid">
        <MetricCard
          title="CURRENT RISK"
          value={
            <span
              className={
                prediction
                  ? riskClass(
                      prediction.risk
                    )
                  : "risk-unknown"
              }
            >
              {prediction?.risk ||
                "UNKNOWN"}
            </span>
          }
          subtitle={
            prediction?.classification ||
            "Waiting for prediction"
          }
          icon={
            <ShieldAlert size={20} />
          }
          accent={
            prediction?.risk ===
            "CRITICAL"
              ? "red"
              : "green"
          }
        />

        <MetricCard
          title="ML CONFIDENCE"
          value={
            prediction
              ? percent(
                  prediction.confidence
                )
              : "—"
          }
          subtitle="Sensor-fusion confidence"
          icon={
            <BrainCircuit size={20} />
          }
          accent="purple"
        />

        <MetricCard
          title="SUSPECTED ZONE"
          value={
            prediction?.river_segment ||
            "None"
          }
          subtitle={
            prediction?.suspected_zone ||
            "No active investigation zone"
          }
          icon={<MapPin size={20} />}
        />

        <MetricCard
          title="ACTIVE ALERTS"
          value={activeAlerts}
          subtitle={
            activeAlerts > 0
              ? "Operator attention required"
              : "No active alerts"
          }
          icon={<Activity size={20} />}
          accent={
            activeAlerts > 0
              ? "red"
              : "green"
          }
        />
      </section>

      <section className="system-strip">
        <div>
          <span className="status-dot online" />
          <span>
            ML ENGINE
          </span>
          <strong>
            {system.ml_engine}
          </strong>
        </div>

        <div>
          <span className="status-dot online" />
          <span>
            DATABASE
          </span>
          <strong>
            {system.database}
          </strong>
        </div>

        <div>
          <RadioTower size={15} />
          <span>
            LORA
          </span>
          <strong>
            {system.lora}
          </strong>
        </div>

        <div>
          <span>
            4G
          </span>
          <strong>
            {system.cellular}
          </strong>
        </div>

        <div>
          <span>
            NODES
          </span>
          <strong>
            {nodes.length}
          </strong>
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              LIVE GIS
            </span>

            <h2>
              River Monitoring Map
            </h2>
          </div>

          <span className="section-meta">
            Dynamic node coordinates
          </span>
        </div>

        <div className="dashboard-map-card">
          <GoldTraceMap
            nodes={nodes}
            prediction={prediction}
            height={460}
          />
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              FIELD SENSOR NETWORK
            </span>

            <h2>
              River Monitoring Nodes
            </h2>
          </div>

          <span className="section-meta">
            {nodes.filter(
              (node) =>
                node.status === "ONLINE"
            ).length}{" "}
            online
          </span>
        </div>

        <div className="node-grid">
          {nodes.map((node) => (
            <NodeCard
              key={node.node_id}
              node={node}
            />
          ))}

          {nodes.length === 0 && (
            <div className="empty-state">
              <RadioTower size={30} />

              <strong>
                No field nodes available
              </strong>

              <p>
                Connect the GoldTrace gateway
                or enable DEMO MODE.
              </p>
            </div>
          )}
        </div>
      </section>

      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              LIVE ANALYTICS
            </span>

            <h2>
              Sensor Trends
            </h2>
          </div>
        </div>

        <LiveTelemetryCharts
          nodes={nodes}
        />
      </div>

      {prediction && (
        <section className="evidence-card">
          <div className="section-title-row">
            <div>
              <span className="eyebrow purple">
                EXPLAINABLE AI
              </span>

              <h2>
                Why GoldTrace Alerted
              </h2>
            </div>

            <span
              className={`risk-badge ${riskClass(
                prediction.risk
              )}`}
            >
              {prediction.risk}
            </span>
          </div>

          <div className="prediction-summary">
            <div>
              <span>
                CLASSIFICATION
              </span>

              <strong>
                {
                  prediction.classification
                }
              </strong>
            </div>

            <div>
              <span>
                CONFIDENCE
              </span>

              <strong className="purple-text">
                {percent(
                  prediction.confidence
                )}
              </strong>
            </div>

            <div>
              <span>
                DURATION
              </span>

              <strong>
                {
                  prediction.duration_seconds
                }
                s
              </strong>
            </div>

            <div>
              <span>
                EVENT
              </span>

              <strong>
                {prediction.event_id}
              </strong>
            </div>
          </div>

          <div className="evidence-grid">
            {prediction.reasons.map(
              (reason, index) => (
                <div
                  key={index}
                  className="evidence-item"
                >
                  <span className="evidence-check">
                    ✓
                  </span>

                  <span>
                    {reason}
                  </span>
                </div>
              )
            )}
          </div>
        </section>
      )}
    </div>
  );
}


