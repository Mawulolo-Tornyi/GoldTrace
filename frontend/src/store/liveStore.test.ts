import {
  beforeEach,
  describe,
  expect,
  it,
} from "vitest";

import { useLiveStore } from "./liveStore";

import type {
  Alert,
  SystemStatus,
} from "../types";


const emptySystem: SystemStatus = {
  raspberry_pi: "UNKNOWN",
  api: "UNKNOWN",
  websocket: "UNKNOWN",
  lora: "UNKNOWN",
  cellular: "UNKNOWN",
  ml_engine: "UNKNOWN",
  database: "UNKNOWN",

  cpu: Number.NaN,
  ram: Number.NaN,
  storage: Number.NaN,
  temperature: Number.NaN,

  uptime: "Unknown",

  nodes_online: 0,
  nodes_offline: 0,
};


describe(
  "GoldTrace live store",
  () => {

    beforeEach(() => {
      useLiveStore.setState({
        nodes: [],
        prediction: null,
        events: [],
        alerts: [],
        system: emptySystem,
        connected: false,
        lastUpdate: null,
      });
    });


    it(
      "keeps unknown system metrics unavailable",
      () => {
        const system =
          useLiveStore.getState().system;

        expect(
          Number.isNaN(system.cpu)
        ).toBe(true);

        expect(
          Number.isNaN(system.ram)
        ).toBe(true);

        expect(
          Number.isNaN(system.storage)
        ).toBe(true);

        expect(
          Number.isNaN(
            system.temperature
          )
        ).toBe(true);
      }
    );


    it(
      "deduplicates live alerts for the same event",
      () => {
        const first: Alert = {
          alert_id: "7",
          event_id: "GT-EVENT-1",
          severity: "CRITICAL",
          location: "SEGMENT_A_B",
          timestamp:
            "2026-09-15T12:00:00Z",
          message:
            "Suspected galamsey/mining activity requiring investigation.",
          status: "ACTIVE",
        };

        const second: Alert = {
          ...first,
          alert_id: "8",
          timestamp:
            "2026-09-15T12:00:05Z",
        };

        useLiveStore
          .getState()
          .addAlert(first);

        useLiveStore
          .getState()
          .addAlert(second);

        const alerts =
          useLiveStore.getState().alerts;

        expect(alerts).toHaveLength(1);

        expect(
          alerts[0].alert_id
        ).toBe("8");

        expect(
          alerts[0].event_id
        ).toBe("GT-EVENT-1");
      }
    );


    it(
      "keeps alerts from different events",
      () => {
        const first: Alert = {
          alert_id: "10",
          event_id: "GT-EVENT-A",
          severity: "HIGH",
          location: "SEGMENT_A_B",
          timestamp:
            "2026-09-15T12:00:00Z",
          message: "Event A",
          status: "ACTIVE",
        };

        const second: Alert = {
          ...first,
          alert_id: "11",
          event_id: "GT-EVENT-B",
          message: "Event B",
        };

        useLiveStore
          .getState()
          .addAlert(first);

        useLiveStore
          .getState()
          .addAlert(second);

        expect(
          useLiveStore.getState().alerts
        ).toHaveLength(2);
      }
    );
  }
);
