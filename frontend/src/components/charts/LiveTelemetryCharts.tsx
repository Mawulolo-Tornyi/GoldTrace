import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  useEffect,
  useState,
} from "react";

import type {
  SensorNode,
} from "../../types";

interface Props {
  nodes: SensorNode[];
}

interface ChartPoint {
  time: string;

  nodeA_turbidity?: number;
  nodeB_turbidity?: number;

  nodeA_audio?: number;
  nodeB_audio?: number;

  nodeA_vibration?: number;
  nodeB_vibration?: number;
}

const MAX_POINTS = 40;

export function LiveTelemetryCharts({
  nodes,
}: Props) {
  const [history, setHistory] =
    useState<ChartPoint[]>([]);

  useEffect(() => {
    if (
      nodes.length === 0
    ) {
      return;
    }

    const nodeA =
      nodes.find(
        (node) =>
          node.position_order ===
            1 ||
          node.node_id ===
            "NODE_A"
      );

    const nodeB =
      nodes.find(
        (node) =>
          node.position_order ===
            2 ||
          node.node_id ===
            "NODE_B"
      );

    const point:
      ChartPoint = {
      time:
        new Date().toLocaleTimeString(
          [],
          {
            hour:
              "2-digit",
            minute:
              "2-digit",
            second:
              "2-digit",
          }
        ),

      nodeA_turbidity:
        nodeA?.turbidity,

      nodeB_turbidity:
        nodeB?.turbidity,

      nodeA_audio:
        nodeA
          ? nodeA.audio_machine_probability *
            100
          : undefined,

      nodeB_audio:
        nodeB
          ? nodeB.audio_machine_probability *
            100
          : undefined,

      nodeA_vibration:
        nodeA
          ? nodeA.vibration_probability *
            100
          : undefined,

      nodeB_vibration:
        nodeB
          ? nodeB.vibration_probability *
            100
          : undefined,
    };

    const timer =
      window.setTimeout(
        () => {
          setHistory(
            (current) =>
              [
                ...current,
                point,
              ].slice(
                -MAX_POINTS
              )
          );
        },
        0
      );

    return () => {
      window.clearTimeout(
        timer
      );
    };
  }, [nodes]);

  return (
    <div className="telemetry-grid">
      <TelemetryChart
        title="Live Turbidity"
        unit="NTU"
        data={history}
        nodeAKey="nodeA_turbidity"
        nodeBKey="nodeB_turbidity"
      />

      <TelemetryChart
        title="Audio Machine Probability"
        unit="%"
        data={history}
        nodeAKey="nodeA_audio"
        nodeBKey="nodeB_audio"
        max={100}
      />

      <TelemetryChart
        title="Vibration Machinery Probability"
        unit="%"
        data={history}
        nodeAKey="nodeA_vibration"
        nodeBKey="nodeB_vibration"
        max={100}
      />
    </div>
  );
}

interface TelemetryChartProps {
  title: string;
  unit: string;

  data: ChartPoint[];

  nodeAKey:
    keyof ChartPoint;

  nodeBKey:
    keyof ChartPoint;

  max?: number;
}

function TelemetryChart({
  title,
  unit,
  data,
  nodeAKey,
  nodeBKey,
  max,
}: TelemetryChartProps) {
  return (
    <article className="chart-card">
      <div className="chart-heading">
        <div>
          <span className="eyebrow">
            LIVE TELEMETRY
          </span>

          <h3>
            {title}
          </h3>
        </div>

        <span className="chart-unit">
          {unit}
        </span>
      </div>

      <div className="chart-area">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart
            data={data}
          >
            <CartesianGrid
              stroke="#17271c"
              strokeDasharray="4 4"
            />

            <XAxis
              dataKey="time"
              minTickGap={28}
              tick={{
                fill:
                  "#6f8376",
                fontSize: 9,
              }}
            />

            <YAxis
              domain={
                max
                  ? [0, max]
                  : [
                      0,
                      "auto",
                    ]
              }
              tick={{
                fill:
                  "#6f8376",
                fontSize: 9,
              }}
            />

            <Tooltip
              contentStyle={{
                background:
                  "#080d0a",

                border:
                  "1px solid #264231",

                borderRadius:
                  10,

                fontSize:
                  11,
              }}
            />

            <Legend />

            <Line
              type="monotone"
              dataKey={
                nodeAKey
              }
              name="Node A"
              stroke="#22c55e"
              strokeWidth={2}
              dot={false}
              isAnimationActive={
                false
              }
            />

            <Line
              type="monotone"
              dataKey={
                nodeBKey
              }
              name="Node B"
              stroke="#a855f7"
              strokeWidth={2}
              dot={false}
              isAnimationActive={
                false
              }
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}

