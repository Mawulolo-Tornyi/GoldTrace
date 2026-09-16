import {
  describe,
  expect,
  it,
} from "vitest";

import {
  normalizeHistoricalEventMap,
} from "./mapLayers";


describe(
  "historical event GIS",
  () => {
    it(
      "normalizes event specific historical GIS data",
      () => {
        const result =
          normalizeHistoricalEventMap({
            event_id:
              "GT-20260915-000001",

            map: {
              center: [
                5.60575,
                -0.184425,
              ],

              suspected_segment: {
                segment_id:
                  "SEGMENT_A_B",

                risk:
                  "CRITICAL",

                geojson: {
                  type:
                    "Feature",

                  properties: {
                    segment_id:
                      "SEGMENT_A_B",

                    river_id:
                      "RIVER_001",

                    river_name:
                      "Example River",

                    event_id:
                      "GT-20260915-000001",

                    risk:
                      "CRITICAL",

                    zone_code:
                      "BETWEEN_NODE_A_AND_NODE_B",
                  },

                  geometry: {
                    type:
                      "LineString",

                    coordinates: [
                      [
                        -0.187,
                        5.6037,
                      ],

                      [
                        -0.1856,
                        5.605,
                      ],

                      [
                        -0.1837,
                        5.6062,
                      ],

                      [
                        -0.1814,
                        5.6081,
                      ],
                    ],
                  },
                },
              },
            },
          });


        expect(
          result.riskZones
        ).toHaveLength(1);

        expect(
          result.riskZones[0].risk
        ).toBe(
          "CRITICAL"
        );

        expect(
          result.riskZones[0].segment_id
        ).toBe(
          "SEGMENT_A_B"
        );


        expect(
          result.eventPoints
        ).toHaveLength(1);

        expect(
          result.eventPoints[0].event_id
        ).toBe(
          "GT-20260915-000001"
        );

        expect(
          result.eventPoints[0].latitude
        ).toBeCloseTo(
          5.60575
        );

        expect(
          result.eventPoints[0].longitude
        ).toBeCloseTo(
          -0.184425
        );
      }
    );
  }
);
