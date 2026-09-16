import { api } from "./client";

export const systemApi = {
  health: () =>
    api.get("/health"),

  status: () =>
    api.get("/system/status"),
};

export const nodesApi = {
  all: () =>
    api.get("/nodes"),
};

export const eventsApi = {
  all: () =>
    api.get("/events"),

  one: (id: string) =>
    api.get(
      `/events/${id}`
    ),
};

export const alertsApi = {
  all: () =>
    api.get("/alerts"),

  one: (id: string) =>
    api.get(
      `/alerts/${id}`
    ),

  acknowledge: (
    id: string,
    note: string
  ) =>
    api.post(
      `/alerts/${id}/acknowledge`,
      {
        acknowledged_by:
          "GoldTrace Operator",

        notes:
          note,
      }
    ),
};

export const predictionsApi = {
  latest: () =>
    api.get(
      "/latest-prediction"
    ),

  risk: () =>
    api.get("/risk"),
};

export const modelsApi = {
  all: () =>
    api.get("/models"),
};

export const sensorApi = {
  health: () =>
    api.get(
      "/sensor-health"
    ),

  submit: (
    packet: unknown
  ) =>
    api.post(
      "/sensor-data",
      packet
    ),
};

export const mapApi = {
  nodes: () =>
    api.get("/map/nodes"),

  events: () =>
    api.get("/map/events"),

  event: (id: string) =>
    api.get(
      `/map/events/${id}`
    ),

  riskZones: () =>
    api.get(
      "/map/risk-zones"
    ),

  rivers: () =>
    api.get("/map/rivers"),

  segments: () =>
    api.get(
      "/map/segments"
    ),
};




export const simulatorApi = {
  scenarios: () =>
    api.get(
      "/simulator/scenarios",
      {
        timeout: 30000,
      }
    ),

  reset: () =>
    api.post(
      "/simulator/reset",
      {},
      {
        timeout: 30000,
      }
    ),

  run: (
    scenario: string,
    seed = 42
  ) =>
    api.post(
      "/simulator/run",
      {
        scenario,
        seed,
      },
      {
        timeout: 30000,
      }
    ),
};
