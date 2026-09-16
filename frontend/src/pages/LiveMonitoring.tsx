import {
  Activity,
  Radio,
} from "lucide-react";

import { LiveTelemetryCharts } from "../components/charts/LiveTelemetryCharts";

import { NodeCard } from "../components/dashboard/NodeCard";

import { useLiveStore } from "../store/liveStore";

export default function LiveMonitoring() {
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

  const demoMode =
    useLiveStore(
      (state) =>
        state.demoMode
    );

  return (
    <div>
      <div className="page-heading live-page-heading">
        <div>
          <span className="eyebrow">
            REAL-TIME SENSOR NETWORK
          </span>

          <h2>
            Live Monitoring
          </h2>

          <p>
            Turbidity, acoustic, vibration,
            temperature, battery and LoRa
            telemetry from GoldTrace nodes.
          </p>
        </div>

        <div
          className={
            connected
              ? "live-pill"
              : "offline-pill"
          }
        >
          {connected ? (
            <Activity
              size={14}
            />
          ) : (
            <Radio
              size={14}
            />
          )}

          {demoMode
            ? "DEMO LIVE"
            : connected
            ? "CONNECTED"
            : "DISCONNECTED"}
        </div>
      </div>

      <div className="node-grid">
        {nodes.map(
          (node) => (
            <NodeCard
              key={
                node.node_id
              }
              node={node}
            />
          )
        )}
      </div>

      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              STREAMING DATA
            </span>

            <h2>
              Sensor Charts
            </h2>
          </div>

          <span className="section-meta">
            Last 40 updates
          </span>
        </div>

        <LiveTelemetryCharts
          nodes={nodes}
        />
      </div>
    </div>
  );
}
