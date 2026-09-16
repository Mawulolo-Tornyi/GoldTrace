import {
  Activity,
  Cpu,
  Database,
  HardDrive,
  Radio,
  Server,
  Signal,
  Thermometer,
  Wifi,
} from "lucide-react";

import { useLiveStore } from "../store/liveStore";

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
            Raspberry Pi resources,
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
              RASPBERRY PI
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
              {
                nodes.filter(
                  (node) =>
                    node.status ===
                    "ONLINE"
                ).length
              }
            </strong>
          </article>

          <article>
            <span>
              STALE
            </span>

            <strong className="system-warning">
              {
                nodes.filter(
                  (node) =>
                    node.status ===
                    "STALE"
                ).length
              }
            </strong>
          </article>

          <article>
            <span>
              OFFLINE
            </span>

            <strong className="system-bad">
              {
                nodes.filter(
                  (node) =>
                    node.status ===
                    "OFFLINE"
                ).length
              }
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

