import {
  Activity,
  ArrowLeft,
  BatteryMedium,
  MapPin,
  Radio,
  Thermometer,
  Waves,
} from "lucide-react";

import {
  Link,
  useParams,
} from "react-router-dom";

import { GoldTraceMap } from "../components/map/GoldTraceMap";

import { useLiveStore } from "../store/liveStore";

import {
  formatNumber,
  integerWithUnit,
  percent,
  relativeTime,
  riskClass,
  valueWithUnit,
} from "../utils/formatters";

export default function NodeDetails() {
  const { id } = useParams();

  const nodes = useLiveStore(
    (state) => state.nodes
  );

  const prediction = useLiveStore(
    (state) => state.prediction
  );

  const node = nodes.find(
    (item) =>
      item.node_id === id
  );

  if (!node) {
    return (
      <div>
        <Link
          to="/nodes"
          className="back-link"
        >
          <ArrowLeft size={15} />
          Back to nodes
        </Link>

        <div className="empty-state">
          <strong>
            Node not found
          </strong>

          <p>
            GoldTrace has not received this node
            from the gateway.
          </p>
        </div>
      </div>
    );
  }

  const sensorHealth =
    Object.entries(
      node.sensor_health
    );

  return (
    <div>
      <Link
        to="/nodes"
        className="back-link"
      >
        <ArrowLeft size={15} />
        Back to nodes
      </Link>

      <div className="details-heading">
        <div>
          <span className="eyebrow">
            FIELD SENSOR NODE
          </span>

          <h2>
            {node.node_id}
          </h2>

          <p>
            {node.name}
          </p>
        </div>

        <div className="details-heading-badges">
          <span
            className={`risk-badge ${riskClass(
              node.risk
            )}`}
          >
            {node.risk}
          </span>

          <span
            className={
              node.status === "ONLINE"
                ? "status-pill online-status"
                : "status-pill offline-status"
            }
          >
            {node.status}
          </span>
        </div>
      </div>

      <div className="node-detail-grid">
        <article className="detail-panel">
          <span className="detail-label">
            NODE INFORMATION
          </span>

          <div className="detail-list">
            <div>
              <span>
                River
              </span>
              <strong>
                {node.river_name}
              </strong>
            </div>

            <div>
              <span>
                Position
              </span>
              <strong>
                {node.position_type}
              </strong>
            </div>

            <div>
              <span>
                Latitude
              </span>
              <strong>
                {formatNumber(node.latitude, 6)}
              </strong>
            </div>

            <div>
              <span>
                Longitude
              </span>
              <strong>
                {formatNumber(node.longitude, 6)}
              </strong>
            </div>

            <div>
              <span>
                Last Contact
              </span>
              <strong>
                {relativeTime(
                  node.last_seen
                )}
              </strong>
            </div>
          </div>
        </article>

        <article className="detail-panel">
          <span className="detail-label">
            COMMUNICATION & POWER
          </span>

          <div className="detail-list">
            <div>
              <span>
                <BatteryMedium size={14} />
                Battery
              </span>

              <strong>
                {integerWithUnit(node.battery, "%")}
              </strong>
            </div>

            <div>
              <span>
                <Radio size={14} />
                LoRa RSSI
              </span>

              <strong>
                {integerWithUnit(node.rssi, " dBm")}
              </strong>
            </div>

            <div>
              <span>
                LoRa SNR
              </span>

              <strong>
                {valueWithUnit(node.snr ?? Number.NaN, " dB", 1)}
              </strong>
            </div>

            <div>
              <span>
                Connection
              </span>

              <strong>
                {node.status}
              </strong>
            </div>
          </div>
        </article>
      </div>

      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              CURRENT TELEMETRY
            </span>

            <h2>
              Sensor Values
            </h2>
          </div>
        </div>

        <div className="sensor-detail-grid">
          <article>
            <Waves size={20} />

            <span>
              Turbidity
            </span>

            <strong>
              {valueWithUnit(node.turbidity, " NTU", 1)}
            </strong>
          </article>

          <article>
            <Thermometer size={20} />

            <span>
              Temperature
            </span>

            <strong>
              {valueWithUnit(node.temperature, "°C", 1)}
            </strong>
          </article>

          <article>
            <Activity size={20} />

            <span>
              Audio Machine Probability
            </span>

            <strong>
              {percent(
                node.audio_machine_probability
              )}
            </strong>
          </article>

          <article>
            <Activity size={20} />

            <span>
              Vibration Probability
            </span>

            <strong>
              {percent(
                node.vibration_probability
              )}
            </strong>
          </article>
        </div>
      </div>

      <div className="node-detail-grid dashboard-section">
        <article className="detail-panel">
          <span className="detail-label">
            ML CLASSIFICATIONS
          </span>

          <div className="detail-list">
            <div>
              <span>
                Environment
              </span>

              <strong>
                {node.environment}
              </strong>
            </div>

            <div>
              <span>
                Audio
              </span>

              <strong>
                {node.audio_class}
              </strong>
            </div>

            <div>
              <span>
                Vibration
              </span>

              <strong>
                {node.vibration_class}
              </strong>
            </div>

            <div>
              <span>
                Dominant Frequency
              </span>

              <strong>
                {valueWithUnit(node.dominant_frequency ?? Number.NaN, " Hz", 1)}
              </strong>
            </div>
          </div>
        </article>

        <article className="detail-panel">
          <span className="detail-label">
            SENSOR HEALTH
          </span>

          <div className="health-list">
            {sensorHealth.map(
              ([sensor, status]) => (
                <div key={sensor}>
                  <span>
                    {sensor.replace(
                      "_",
                      " "
                    )}
                  </span>

                  <strong
                    className={`sensor-health health-${String(
                      status
                    ).toLowerCase()}`}
                  >
                    {status}
                  </strong>
                </div>
              )
            )}
          </div>
        </article>
      </div>

      <div className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              GIS LOCATION
            </span>

            <h2>
              Node Position
            </h2>
          </div>

          <span className="section-meta">
            <MapPin size={13} />
            GPS
          </span>
        </div>

        <div className="dashboard-map-card">
          <GoldTraceMap
            nodes={[node]}
            prediction={prediction}
            height={430}
          />
        </div>
      </div>
    </div>
  );
}

