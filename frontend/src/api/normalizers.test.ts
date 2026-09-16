import {
  describe,
  expect,
  it,
} from "vitest";

import {
  mergeRiskUpdate,
  normalizeAlerts,
  normalizeNode,
  normalizePrediction,
  normalizeRisk,
  normalizeSystem,
} from "./normalizers";


describe(
  "GoldTrace API normalizers",
  () => {

    it(
      "normalizes a real CRITICAL backend prediction",
      () => {
        const prediction =
          normalizePrediction({
            event_id:
              "GT-20260915-000001",

            timestamp:
              "2026-09-15T12:23:35Z",

            prediction:
              "HIGH_RISK_MINING_ACTIVITY",

            risk_level:
              "CRITICAL",

            confidence:
              0.913,

            suspected_zone:
              "BETWEEN_NODE_A_AND_NODE_B",

            location: {
              segment_id:
                "SEGMENT_A_B",
            },

            evidence: {
              persistence_seconds:
                42,

              reasons: [
                "Strong downstream turbidity increase",
                "Machine-like acoustic signature",
                "Heavy machinery vibration",
              ],
            },

            human_description:
              "Suspected galamsey/mining activity requiring investigation",
          });

        expect(
          prediction
        ).not.toBeNull();

        expect(
          prediction?.classification
        ).toBe(
          "HIGH_RISK_MINING_ACTIVITY"
        );

        expect(
          prediction?.risk
        ).toBe("CRITICAL");

        expect(
          prediction?.confidence
        ).toBeCloseTo(0.913);

        expect(
          prediction?.suspected_zone
        ).toBe(
          "BETWEEN_NODE_A_AND_NODE_B"
        );

        expect(
          prediction?.river_segment
        ).toBe(
          "SEGMENT_A_B"
        );

        expect(
          prediction?.duration_seconds
        ).toBe(42);
      }
    );


    it(
      "merges a HIGH to CRITICAL live risk update",
      () => {
        const current =
          normalizePrediction({
            event_id:
              "GT-LIVE-1",

            prediction:
              "POSSIBLE_MINING_ACTIVITY",

            risk_level:
              "HIGH",

            confidence:
              0.88,
          });

        const updated =
          mergeRiskUpdate(
            {
              prediction:
                "HIGH_RISK_MINING_ACTIVITY",

              risk_level:
                "CRITICAL",

              confidence:
                0.93,
            },

            current
          );

        expect(
          updated?.classification
        ).toBe(
          "HIGH_RISK_MINING_ACTIVITY"
        );

        expect(
          updated?.risk
        ).toBe("CRITICAL");

        expect(
          updated?.confidence
        ).toBeCloseTo(0.93);
      }
    );


    it(
      "merges backend ML node results with topology",
      () => {
        const node =
          normalizeNode(
            {
              node_id:
                "NODE_B",

              name:
                "Downstream Node",

              latitude:
                5.6081,

              longitude:
                -0.1814,

              status:
                "ONLINE",

              river_id:
                "RIVER_001",

              river_name:
                "Example River",

              position_order:
                2,

              position_type:
                "DOWNSTREAM",
            },

            undefined,

            "CRITICAL",

            {
              environment:
                "UNKNOWN_ENVIRONMENTAL_CHANGE",

              audio:
                "MOTORBIKE",

              vibration:
                "CONSTRUCTION_ACTIVITY",

              audio_machine_probability:
                0.9554,

              vibration_machinery_probability:
                1.0,

              health:
                "HEALTHY",

              turbidity_ntu:
                92.5295,
            }
          );

        expect(
          node.node_id
        ).toBe("NODE_B");

        expect(
          node.status
        ).toBe("ONLINE");

        expect(
          node.risk
        ).toBe("CRITICAL");

        expect(
          node.turbidity
        ).toBeCloseTo(
          92.5295
        );

        expect(
          node.audio_class
        ).toBe("MOTORBIKE");

        expect(
          node.vibration_class
        ).toBe(
          "CONSTRUCTION_ACTIVITY"
        );

        expect(
          node.audio_machine_probability
        ).toBeCloseTo(
          0.9554
        );

        expect(
          node.vibration_probability
        ).toBe(1);

        expect(
          node.sensor_health.turbidity
        ).toBe("HEALTHY");

        expect(
          node.sensor_health.microphone
        ).toBe("HEALTHY");

        expect(
          node.sensor_health.geophone
        ).toBe("HEALTHY");
      }
    );


    it(
      "does not fabricate missing environmental telemetry",
      () => {
        const node =
          normalizeNode({
            node_id:
              "NODE_TEST",

            latitude:
              5.60,

            longitude:
              -0.18,

            status:
              "ONLINE",
          });

        expect(
          Number.isNaN(
            node.temperature
          )
        ).toBe(true);

        expect(
          Number.isNaN(
            node.battery
          )
        ).toBe(true);

        expect(
          Number.isNaN(
            node.rssi
          )
        ).toBe(true);

        expect(
          Number.isNaN(
            node.snr ?? Number.NaN
          )
        ).toBe(true);

        expect(
          Number.isNaN(
            node.dominant_frequency ??
              Number.NaN
          )
        ).toBe(true);
      }
    );


    it(
      "handles an unknown node without crashing",
      () => {
        const node =
          normalizeNode({
            node_id:
              "NODE_NEW",

            latitude:
              "5.7001",

            longitude:
              "-0.2201",
          });

        expect(
          node.node_id
        ).toBe("NODE_NEW");

        expect(
          node.latitude
        ).toBeCloseTo(
          5.7001
        );

        expect(
          node.longitude
        ).toBeCloseTo(
          -0.2201
        );

        expect(
          node.risk
        ).toBe("UNKNOWN");
      }
    );


    it(
      "keeps DISPATCHED alerts active until operator acknowledgement",
      () => {
        const alerts =
          normalizeAlerts([
            {
              alert_id:
                7,

              event_id:
                "GT-EVENT-1",

              risk_level:
                "CRITICAL",

              status:
                "DISPATCHED",

              message:
                "Suspected galamsey/mining activity requiring investigation.",
            },
          ]);

        expect(
          alerts
        ).toHaveLength(1);

        expect(
          alerts[0].status
        ).toBe("ACTIVE");

        expect(
          alerts[0].severity
        ).toBe("CRITICAL");
      }
    );


    it(
      "deduplicates multiple alert records for the same event",
      () => {
        const alerts =
          normalizeAlerts([
            {
              alert_id:
                7,

              event_id:
                "GT-EVENT-2",

              risk_level:
                "CRITICAL",

              status:
                "DISPATCHED",

              message:
                "First alert",
            },

            {
              alert_id:
                8,

              event_id:
                "GT-EVENT-2",

              risk_level:
                "CRITICAL",

              status:
                "DISPATCHED",

              message:
                "Repeated alert",
            },
          ]);

        expect(
          alerts
        ).toHaveLength(1);

        expect(
          alerts[0].event_id
        ).toBe(
          "GT-EVENT-2"
        );
      }
    );


    it(
      "normalizes live backend system health",
      () => {
        const system =
          normalizeSystem({
            system:
              "GoldTrace",

            nodes_seen: [
              "NODE_A",
              "NODE_B",
            ],

            websocket_clients:
              1,

            models: {
              audio_loaded:
                true,

              vibration_loaded:
                true,

              environment_loaded:
                true,

              anomaly_loaded:
                true,

              fusion_loaded:
                true,
            },
          });

        expect(
          system.raspberry_pi
        ).toBe("CONNECTED");

        expect(
          system.websocket
        ).toBe("CONNECTED");

        expect(
          system.lora
        ).toBe("CONNECTED");

        expect(
          system.ml_engine
        ).toBe("ONLINE");

        expect(
          Number.isNaN(
            system.cpu
          )
        ).toBe(true);

        expect(
          Number.isNaN(
            system.ram
          )
        ).toBe(true);

        expect(
          Number.isNaN(
            system.temperature
          )
        ).toBe(true);
      }
    );


    it(
      "converts unsupported risk labels to UNKNOWN",
      () => {
        expect(
          normalizeRisk(
            "SOMETHING_INVALID"
          )
        ).toBe("UNKNOWN");

        expect(
          normalizeRisk(
            undefined
          )
        ).toBe("UNKNOWN");
      }
    );
  }
);


