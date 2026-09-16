import type { LiveState } from "../types";

export const demoState: LiveState = {
  nodes: [
    {
      node_id: "NODE_A",
      name: "River Monitoring Node A",

      status: "ONLINE",

      river_id: "RIVER_001",
      river_name: "Example River",

      position_order: 1,
      position_type: "UPSTREAM",

      latitude: 5.6037,
      longitude: -0.187,

      turbidity: 18.6,
      temperature: 26.4,

      environment: "NORMAL_RIVER",

      audio_class: "NORMAL_ENVIRONMENT",
      audio_machine_probability: 0.07,

      vibration_class: "NORMAL_GROUND",
      vibration_probability: 0.08,

      vibration_rms: 0.18,
      vibration_peak: 0.31,
      dominant_frequency: 14.2,

      battery: 89,
      rssi: -71,
      snr: 8.4,

      risk: "LOW",

      sensor_health: {
        turbidity: "HEALTHY",
        microphone: "HEALTHY",
        geophone: "HEALTHY",
        temperature: "HEALTHY",
        lora: "HEALTHY",
        power: "HEALTHY",
      },

      last_seen: new Date().toISOString(),
    },

    {
      node_id: "NODE_B",
      name: "River Monitoring Node B",

      status: "ONLINE",

      river_id: "RIVER_001",
      river_name: "Example River",

      position_order: 2,
      position_type: "DOWNSTREAM",

      latitude: 5.6081,
      longitude: -0.1814,

      turbidity: 92.5,
      temperature: 27.1,

      environment: "ABNORMAL",

      audio_class: "EXCAVATOR_LIKE",
      audio_machine_probability: 0.91,

      vibration_class: "HEAVY_MACHINERY",
      vibration_probability: 0.87,

      vibration_rms: 1.82,
      vibration_peak: 3.41,
      dominant_frequency: 41.8,

      battery: 83,
      rssi: -76,
      snr: 6.2,

      risk: "CRITICAL",

      sensor_health: {
        turbidity: "HEALTHY",
        microphone: "HEALTHY",
        geophone: "HEALTHY",
        temperature: "HEALTHY",
        lora: "HEALTHY",
        power: "HEALTHY",
      },

      last_seen: new Date().toISOString(),
    },
  ],

  prediction: {
    classification:
      "HIGH_RISK_MINING_ACTIVITY",

    risk: "CRITICAL",

    confidence: 0.93,

    suspected_zone:
      "BETWEEN_NODE_A_AND_NODE_B",

    river_segment:
      "SEGMENT_A_B",

    duration_seconds: 42,

    event_id:
      "GT-DEMO-000001",

    human_description:
      "Suspected galamsey/mining activity requiring investigation",

    recommendation:
      "Security/environmental authorities should investigate the monitored river section between Node A and Node B.",

    reasons: [
      "Strong downstream turbidity increase",
      "Excavator-like acoustic signature",
      "Heavy machinery vibration",
      "Activity persisted for 42 seconds",
      "Multiple sensors agree",
      "Upstream Node A remained normal",
    ],
  },

  events: [
    {
      event_id:
        "GT-DEMO-000001",

      timestamp:
        new Date().toISOString(),

      prediction:
        "HIGH_RISK_MINING_ACTIVITY",

      risk:
        "CRITICAL",

      confidence:
        0.93,

      zone:
        "Node A to Node B",

      segment_id:
        "SEGMENT_A_B",

      duration_seconds:
        42,

      status:
        "ACTIVE",
    },
  ],

  alerts: [
    {
      alert_id:
        "ALERT-DEMO-001",

      event_id:
        "GT-DEMO-000001",

      severity:
        "CRITICAL",

      location:
        "SEGMENT_A_B",

      timestamp:
        new Date().toISOString(),

      message:
        "Suspected galamsey/mining activity requiring investigation.",

      status:
        "ACTIVE",
    },
  ],

  system: {
    raspberry_pi: "DEMO",
    api: "ONLINE",
    websocket: "DEMO",
    lora: "DEMO",
    cellular: "DEMO",
    ml_engine: "ONLINE",
    database: "ONLINE",

    cpu: 21,
    ram: 38,
    storage: 27,
    temperature: 46,

    uptime: "Demo session",

    nodes_online: 2,
    nodes_offline: 0,

    last_prediction:
      new Date().toISOString(),
  },
};

