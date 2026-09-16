import {
  describe,
  expect,
  it,
} from "vitest";

import {
  normalizePrediction,
} from "./normalizers";


describe(
  "historical prediction metadata",
  () => {
    it(
      "preserves human description and recommendation",
      () => {
        const result =
          normalizePrediction({
            event_id:
              "GT-20260915-000001",

            prediction:
              "HIGH_RISK_MINING_ACTIVITY",

            risk_level:
              "CRITICAL",

            confidence:
              0.9127,

            suspected_zone:
              "BETWEEN_NODE_A_AND_NODE_B",

            human_description:
              "Suspected galamsey/mining activity requiring investigation",

            recommendation:
              "Security/environmental authorities should investigate the monitored river section between Node A and Node B.",

            evidence: {
              persistence_seconds:
                42,

              reasons: [
                "Strong downstream turbidity increase",
                "Machine-like acoustic signature",
              ],
            },

            location: {
              segment_id:
                "SEGMENT_A_B",
            },
          });


        expect(result).not.toBeNull();

        expect(
          result?.human_description
        ).toBe(
          "Suspected galamsey/mining activity requiring investigation"
        );

        expect(
          result?.recommendation
        ).toContain(
          "authorities should investigate"
        );

        expect(
          result?.duration_seconds
        ).toBe(42);
      }
    );
  }
);
