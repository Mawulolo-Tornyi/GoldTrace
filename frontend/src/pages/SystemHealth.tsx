import {
  Activity,
  Cpu,
  Database,
  HardDrive,
  Radio,
  Server,
  ShieldAlert,
  ShieldCheck,
  Signal,
  Thermometer,
  Wifi,
} from "lucide-react";

import { useLiveStore } from "../store/liveStore";

function isHealthyState(
  value: string
): boolean {
  const normal =
    value.toUpperCase();

  return (
    normal === "ONLINE" ||
    normal === "HEALTHY" ||
    normal === "CONNECTED" ||
    normal === "DEMO"
  );
}


function stateClass(
  value: string
): string {
  const normal =
    value.toUpperCase();

  if (
    normal === "ONLINE" ||
    normal === "HEALTHY" ||
    normal === "CONNECTED" ||
    normal === "DEMO"
  ) {
    return "system-good";
  }

  if (
    normal === "OFFLINE" ||
    normal === "NOT CONNECTED" ||
    normal === "DISCONNECTED" ||
    normal === "FAILED" ||
    normal === "ERROR"
  ) {
    return "system-bad";
  }

  return "system-neutral";
}

interface ProgressProps {
  label: string;
  value: number;
  icon:
    React.ReactNode;
}

function ResourceProgress({
  label,
  value,
  icon,
}: ProgressProps) {
  const available =
    Number.isFinite(value);

  const safeValue =
    available
      ? Math.max(
          0,
          Math.min(
            100,
            value
          )
        )
      : 0;

  return (
    <article className="resource-card">
      <div className="resource-card-top">
        <div>
          {icon}

          <span>
            {label}
          </span>
        </div>

        <strong>
          {available
            ? `${Math.round(safeValue)}%`
            : "—"}
        </strong>
      </div>

      <div className="resource-progress">
        <span
          style={{
            width:
              `${safeValue}%`,
          }}
        />
      </div>
    </article>
  );
}

export default function SystemHealth() {
  const system =
    useLiveStore(
      (state) =>
        state.system
    );

  const nodes =
    useLiveStore(
      (state) =>
        state.nodes
    );

  const connected =
    useLiveStore(
      (state) =>
        state.connected
    );

  const onlineNodes =
    nodes.filter(
      (node) =>
        node.status ===
        "ONLINE"
    ).length;

  const staleNodes =
    nodes.filter(
      (node) =>
        node.status ===
        "STALE"
    ).length;

  const offlineNodes =
    nodes.filter(
      (node) =>
        node.status ===
        "OFFLINE"
    ).length;

  const coreServicesHealthy =
    isHealthyState(
      system.raspberry_pi
    ) &&
    isHealthyState(
      system.ml_engine
    ) &&
    isHealthyState(
      system.database
    );

  const fieldEvidenceHealthy =
    nodes.length > 0 &&
    onlineNodes ===
      nodes.length &&
    staleNodes === 0 &&
    offlineNodes === 0;

  const evidenceReady =
    connected &&
    coreServicesHealthy &&
    fieldEvidenceHealthy;

  const evidenceBlocked =
    !connected ||
    nodes.length === 0 ||
    offlineNodes ===
      nodes.length;

  const trustState =
    evidenceReady
      ? "ready"
      : evidenceBlocked
      ? "blocked"
      : "degraded";

  const services = [
    {
      label:
        "Raspberry Pi",
      value:
        system.raspberry_pi,
      icon:
        <Server size={18} />,
    },

    {
      label:
        "ML Engine",
      value:
        system.ml_engine,
      icon:
        <Cpu size={18} />,
    },

    {
      label:
        "Database",
      value:
        system.database,
      icon:
        <Database size={18} />,
    },

    {
      label:
        "LoRa",
      value:
        system.lora,
      icon:
        <Radio size={18} />,
    },

    {
      label:
        "4G / Cellular",
      value:
        system.cellular,
      icon:
        <Signal size={18} />,
    },

    {
      label:
        "WebSocket",
      value:
        connected
          ? "CONNECTED"
          : "OFFLINE",
      icon:
        <Wifi size={18} />,
    },
  ];

  return (
    <div>
      <div className="page-heading system-health-heading">
        <div>
          <span className="eyebrow">
            INFRASTRUCTURE
            MONITORING
          </span>

          <h2>
            System Health
          </h2>

          <p>
            Gateway resources,
            connectivity, database,
            communications and ML
            engine health.
          </p>
        </div>

        <div className="system-uptime">
          <span>
            SYSTEM UPTIME
          </span>

          <strong>
            {system.uptime}
          </strong>
        </div>
      </div>

      <div
        className={
          `evidence-trust-gate ${trustState}`
        }
      >
        <div className="evidence-trust-icon">
          {
            evidenceReady
              ? (
                  <ShieldCheck
                    size={24}
                  />
                )
              : (
                  <ShieldAlert
                    size={24}
                  />
                )
          }
        </div>

        <div className="evidence-trust-copy">
          <span>
            EVIDENCE TRUST GATE
          </span>

          <strong>
            {
              trustState === "ready"
                ? "READY FOR ESCALATION EVALUATION"
                : trustState === "blocked"
                ? "EVIDENCE TRUST NOT READY"
                : "EVIDENCE TRUST DEGRADED"
            }
          </strong>

          <p>
            {
              trustState === "ready"
                ? (
                    "Core services, live connection and all field nodes "
                    + "are healthy. Incoming evidence can be evaluated "
                    + "against GoldTrace escalation rules."
                  )
                : trustState === "blocked"
                ? (
                    "Critical field or communication availability is "
                    + "missing. Sensor evidence should not be relied on "
                    + "for automatic escalation."
                  )
                : (
                    "One or more field-health conditions are degraded. "
                    + "GoldTrace should verify sensor evidence before "
                    + "escalation."
                  )
            }
          </p>
        </div>

        <div className="evidence-trust-metrics">
          <div>
            <span>ONLINE</span>
            <strong>
              {onlineNodes}/{nodes.length}
            </strong>
          </div>

          <div>
            <span>STALE</span>
            <strong>
              {staleNodes}
            </strong>
          </div>

          <div>
            <span>OFFLINE</span>
            <strong>
              {offlineNodes}
            </strong>
          </div>

          <div>
            <span>LIVE LINK</span>
            <strong>
              {
                connected
                  ? "CONNECTED"
                  : "OFFLINE"
              }
            </strong>
          </div>
        </div>
      </div>


      <div className="service-health-grid">
        {services.map(
          ({
            label,
            value,
            icon,
          }) => (
            <article
              className="service-health-card"
              key={label}
            >
              <div className="service-icon">
                {icon}
              </div>

              <div>
                <span>
                  {label}
                </span>

                <strong
                  className={
                    stateClass(
                      value
                    )
                  }
                >
                  {value}
                </strong>
              </div>
            </article>
          )
        )}
      </div>

      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              GATEWAY / RUNTIME
            </span>

            <h2>
              Resource Usage
            </h2>
          </div>
        </div>

        <div className="resource-health-grid">
          <ResourceProgress
            label="CPU Usage"
            value={
              system.cpu
            }
            icon={
              <Cpu size={17} />
            }
          />

          <ResourceProgress
            label="RAM Usage"
            value={
              system.ram
            }
            icon={
              <Activity
                size={17}
              />
            }
          />

          <ResourceProgress
            label="Storage"
            value={
              system.storage
            }
            icon={
              <HardDrive
                size={17}
              />
            }
          />

          <article className="temperature-card">
            <div>
              <Thermometer
                size={18}
              />

              <span>
                Pi Temperature
              </span>
            </div>

            <strong>
              {Number.isFinite(
                system.temperature
              )
                ? `${system.temperature.toFixed(1)}°C`
                : "—"}
            </strong>
          </article>
        </div>
      </div>

      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              FIELD NETWORK
            </span>

            <h2>
              Node Connectivity
            </h2>
          </div>
        </div>

        <div className="system-stat-grid">
          <article>
            <span>
              TOTAL NODES
            </span>

            <strong>
              {nodes.length}
            </strong>
          </article>

          <article>
            <span>
              ONLINE
            </span>

            <strong className="system-good">
              {onlineNodes}
            </strong>
          </article>

          <article>
            <span>
              STALE
            </span>

            <strong className="system-warning">
              {staleNodes}
            </strong>
          </article>

          <article>
            <span>
              OFFLINE
            </span>

            <strong className="system-bad">
              {offlineNodes}
            </strong>
          </article>
        </div>
      </div>

      <div className="system-last-prediction">
        <span>
          LAST SUCCESSFUL PREDICTION
        </span>

        <strong>
          {system.last_prediction
            ? new Date(
                system.last_prediction
              ).toLocaleString()
            : "No prediction received"}
        </strong>
      </div>
    </div>
  );
}

