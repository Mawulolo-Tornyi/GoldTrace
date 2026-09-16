import {
  BatteryMedium,
  ChevronRight,
  MapPin,
  Radio,
  Waves,
} from "lucide-react";

import { Link } from "react-router-dom";

import { useLiveStore } from "../store/liveStore";

import {
  formatNumber,
  relativeTime,
  riskClass,
} from "../utils/formatters";

export default function Nodes() {
  const nodes = useLiveStore(
    (state) => state.nodes
  );

  return (
    <div>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            FIELD INFRASTRUCTURE
          </span>

          <h2>
            Monitoring Nodes
          </h2>

          <p>
            Inspect GoldTrace river sensor nodes,
            communications, power and sensor health.
          </p>
        </div>
      </div>

      {nodes.length === 0 ? (
        <div className="empty-state">
          <Radio size={30} />

          <strong>
            No monitoring nodes available
          </strong>

          <p>
            Waiting for the GoldTrace gateway to
            provide node information.
          </p>
        </div>
      ) : (
        <div className="nodes-page-grid">
          {nodes.map((node) => (
            <article
              className="node-overview-card"
              key={node.node_id}
            >
              <div className="node-overview-header">
                <div>
                  <span className="node-position">
                    {node.position_type}
                  </span>

                  <h3>
                    {node.node_id}
                  </h3>

                  <p>
                    {node.river_name}
                  </p>
                </div>

                <span
                  className={`risk-badge ${riskClass(
                    node.risk
                  )}`}
                >
                  {node.risk}
                </span>
              </div>

              <div className="node-overview-status">
                <span
                  className={
                    node.status === "ONLINE"
                      ? "status-dot online"
                      : "status-dot offline"
                  }
                />

                <strong>
                  {node.status}
                </strong>

                <span>
                  {relativeTime(
                    node.last_seen
                  )}
                </span>
              </div>

              <div className="node-overview-values">
                <div>
                  <Waves size={16} />
                  <span>
                    Turbidity
                  </span>
                  <strong>
                    {formatNumber(
                      node.turbidity
                    )}{" "}
                    NTU
                  </strong>
                </div>

                <div>
                  <BatteryMedium size={16} />
                  <span>
                    Battery
                  </span>
                  <strong>
                    {node.battery}%
                  </strong>
                </div>

                <div>
                  <Radio size={16} />
                  <span>
                    LoRa
                  </span>
                  <strong>
                    {node.rssi} dBm
                  </strong>
                </div>

                <div>
                  <MapPin size={16} />
                  <span>
                    Position
                  </span>
                  <strong>
                    {node.position_type}
                  </strong>
                </div>
              </div>

              <Link
                to={`/nodes/${node.node_id}`}
                className="details-button"
              >
                View Node Details

                <ChevronRight size={16} />
              </Link>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
