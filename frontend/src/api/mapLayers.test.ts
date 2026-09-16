import {
  describe,
  expect,
  it,
} from "vitest";

import {
  normalizeMapEvents,
  normalizeRiskLines,
  normalizeRiverLines,
  normalizeSegmentLines,
} from "./mapLayers";


describe(
  "GoldTrace GIS normalization",
  () => {

    const feature = {
      type:
        "Feature",

      properties: {
        segment_id:
          "SEGMENT_A_B",

        river_id:
          "RIVER_001",

        river_name:
          "Example River",

        from_node:
          "NODE_A",

        to_node:
          "NODE_B",
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
            -0.1814,
            5.6081,
          ],
        ],
      },
    };


    it(
      "converts GeoJSON longitude latitude into Leaflet latitude longitude",
      () => {
        const lines =
          normalizeRiverLines({
            type:
              "FeatureCollection",

            features: [
              feature,
            ],
          });

        expect(
          lines
        ).toHaveLength(1);

        expect(
          lines[0].positions[0]
        ).toEqual([
          5.6037,
          -0.187,
        ]);

        expect(
          lines[0].positions[2]
        ).toEqual([
          5.6081,
          -0.1814,
        ]);
      }
    );


    it(
      "normalizes monitored segment features",
      () => {
        const lines =
          normalizeSegmentLines([
            feature,
          ]);

        expect(
          lines
        ).toHaveLength(1);

        expect(
          lines[0].segment_id
        ).toBe(
          "SEGMENT_A_B"
        );

        expect(
          lines[0].river_id
        ).toBe(
          "RIVER_001"
        );
      }
    );


    it(
      "normalizes event centroid for map markers",
      () => {
        const events =
          normalizeMapEvents([
            {
              event_id:
                "GT-20260915-000001",

              location: {
                zone_code:
                  "BETWEEN_NODE_A_AND_NODE_B",

                segment_id:
                  "SEGMENT_A_B",

                river_id:
                  "RIVER_001",

                river_name:
                  "Example River",

                centroid: {
                  latitude:
                    5.60575,

                  longitude:
                    -0.184425,
                },
              },
            },
          ]);

        expect(
          events
        ).toHaveLength(1);

        expect(
          events[0].latitude
        ).toBeCloseTo(
          5.60575
        );

        expect(
          events[0].longitude
        ).toBeCloseTo(
          -0.184425
        );
      }
    );


    it(
      "deduplicates repeated risk zones for one event and segment",
      () => {
        const criticalFeature = {
          ...feature,

          properties: {
            ...feature.properties,

            risk:
              "CRITICAL",

            event_id:
              "GT-EVENT-1",
          },
        };

        const highFeature = {
          ...feature,

          properties: {
            ...feature.properties,

            risk:
              "HIGH",

            event_id:
              "GT-EVENT-1",
          },
        };

        const lines =
          normalizeRiskLines([
            {
              event_id:
                "GT-EVENT-1",

              risk:
                "HIGH",

              geojson:
                highFeature,
            },

            {
              event_id:
                "GT-EVENT-1",

              risk:
                "CRITICAL",

              geojson:
                criticalFeature,
            },

            {
              event_id:
                "GT-EVENT-1",

              risk:
                "HIGH",

              geojson:
                highFeature,
            },
          ]);

        expect(
          lines
        ).toHaveLength(1);

        expect(
          lines[0].risk
        ).toBe(
          "CRITICAL"
        );

        expect(
          lines[0].event_id
        ).toBe(
          "GT-EVENT-1"
        );
      }
    );
  }
);
