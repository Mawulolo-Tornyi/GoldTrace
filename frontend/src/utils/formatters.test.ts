import {
  describe,
  expect,
  it,
} from "vitest";

import {
  formatNumber,
  integerWithUnit,
  percent,
  riskClass,
  valueWithUnit,
} from "./formatters";


describe(
  "GoldTrace telemetry formatters",
  () => {

    it(
      "shows unavailable percentage as a dash",
      () => {
        expect(
          percent(Number.NaN)
        ).toBe("—");
      }
    );


    it(
      "does not convert missing numeric telemetry into fake zero",
      () => {
        expect(
          formatNumber(Number.NaN)
        ).toBe("—");
      }
    );


    it(
      "formats real turbidity correctly",
      () => {
        expect(
          valueWithUnit(
            92.5294,
            " NTU",
            1
          )
        ).toBe("92.5 NTU");
      }
    );


    it(
      "shows unavailable sensor value without a misleading unit",
      () => {
        expect(
          valueWithUnit(
            Number.NaN,
            "°C",
            1
          )
        ).toBe("—");
      }
    );


    it(
      "formats battery percentage when available",
      () => {
        expect(
          integerWithUnit(
            83.2,
            "%"
          )
        ).toBe("83%");
      }
    );


    it(
      "shows unavailable battery as a dash",
      () => {
        expect(
          integerWithUnit(
            Number.NaN,
            "%"
          )
        ).toBe("—");
      }
    );


    it(
      "converts probability from decimal to percentage",
      () => {
        expect(
          percent(0.913)
        ).toBe("91%");
      }
    );


    it(
      "preserves percentage-style values",
      () => {
        expect(
          percent(91.3)
        ).toBe("91%");
      }
    );


    it(
      "maps CRITICAL risk to critical styling",
      () => {
        expect(
          riskClass("CRITICAL")
        ).toBe("risk-critical");
      }
    );


    it(
      "maps HIGH risk to high styling",
      () => {
        expect(
          riskClass("HIGH")
        ).toBe("risk-high");
      }
    );
  }
);
