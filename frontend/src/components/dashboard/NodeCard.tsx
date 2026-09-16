import {
  BatteryMedium,
  Radio,
  Thermometer,
  Waves,
} from "lucide-react";

import type { SensorNode } from "../../types";

import {
  integerWithUnit,
  percent,
  relativeTime,
  riskClass,
  valueWithUnit,
} from "../../utils/formatters";

interface Props {
  node: SensorNode;
}

export function NodeCard({
  node,
}: Props) {
  return (
    <article className="node-card">
      <div className="node-card-top">
        <div>
          <span className="node-position">
            {node.position_type}
          </span>

          <h3>{node.node_id}</h3>

          <p>{node.name}</p>
        </div>

        <span
          className={`risk-badge ${riskClass(
            node.risk
          )}`}
        >
          {node.risk}
        </span>
      </div>

      <div className="node-online-row">
        <span
          className={
            node.status === "ONLINE"
              ? "status-dot online"
              : "status-dot offline"
          }
        />

        <span>{node.status}</span>

        <span className="last-seen">
          {relativeTime(node.last_seen)}
        </span>
      </div>

      <div className="sensor-grid">
        <div className="sensor-value">
          <span className="sensor-label">
            <Waves size={15} />
            Turbidity
          </span>

          <strong>
            {valueWithUnit(node.turbidity, " NTU", 1)}
          </strong>
        </div>

        <div className="sensor-value">
          <span className="sensor-label">
            <Thermometer size={15} />
            Water Temp.
          </span>

          <strong>
            {valueWithUnit(node.temperature, "°C", 1)}
          </strong>
        </div>

        <div className="sensor-value">
          <span>
            Audio Classification
          </span>

          <strong>
            {node.audio_class}
          </strong>
        </div>

        <div className="sensor-value">
          <span>
            Machine Probability
          </span>

          <strong>
            {percent(
              node.audio_machine_probability
            )}
          </strong>
        </div>

        <div className="sensor-value">
          <span>
            Vibration
          </span>

          <strong>
            {node.vibration_class}
          </strong>
        </div>

        <div className="sensor-value">
          <span>
            Machinery Probability
          </span>

          <strong>
            {percent(
              node.vibration_probability
            )}
          </strong>
        </div>

        <div className="sensor-value">
          <span className="sensor-label">
            <BatteryMedium size={15} />
            Battery
          </span>

          <strong>
            {integerWithUnit(node.battery, "%")}
          </strong>
        </div>

        <div className="sensor-value">
          <span className="sensor-label">
            <Radio size={15} />
            LoRa RSSI
          </span>

          <strong>
            {integerWithUnit(node.rssi, " dBm")}
          </strong>
        </div>
      </div>
    </article>
  );
}

