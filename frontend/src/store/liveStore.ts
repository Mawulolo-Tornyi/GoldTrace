import { create } from "zustand";

import type {
  Alert,
  GoldTraceEvent,
  LiveState,
  Prediction,
  SensorNode,
  SystemStatus,
} from "../types";

import { demoState } from "../utils/demoData";

interface GoldTraceStore
  extends LiveState {
  demoMode: boolean;
  connected: boolean;

  lastUpdate: string | null;

  setConnected:
    (connected: boolean) => void;

  updateNode:
    (node: SensorNode) => void;

  setPrediction:
    (prediction: Prediction) => void;

  addEvent:
    (event: GoldTraceEvent) => void;

  addAlert:
    (alert: Alert) => void;

  setSystem:
    (system: SystemStatus) => void;

  acknowledgeAlertLocally:
    (
      alertId: string,
      note?: string
    ) => void;
}

const demoMode =
  import.meta.env.VITE_DEMO_MODE ===
  "true";

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

export const useLiveStore =
  create<GoldTraceStore>(
    (set) => ({
      nodes:
        demoMode
          ? demoState.nodes
          : [],

      prediction:
        demoMode
          ? demoState.prediction
          : null,

      events:
        demoMode
          ? demoState.events
          : [],

      alerts:
        demoMode
          ? demoState.alerts
          : [],

      system:
        demoMode
          ? demoState.system
          : emptySystem,

      demoMode,

      connected:
        demoMode,

      lastUpdate:
        demoMode
          ? new Date().toISOString()
          : null,

      setConnected:
        (connected) =>
          set({
            connected,
          }),

      updateNode:
        (node) =>
          set((state) => {
            const exists =
              state.nodes.some(
                (item) =>
                  item.node_id ===
                  node.node_id
              );

            return {
              nodes: exists
                ? state.nodes.map(
                    (item) =>
                      item.node_id ===
                      node.node_id
                        ? {
                            ...item,
                            ...node,
                          }
                        : item
                  )
                : [
                    ...state.nodes,
                    node,
                  ],

              lastUpdate:
                new Date().toISOString(),
            };
          }),

      setPrediction:
        (prediction) =>
          set({
            prediction,

            lastUpdate:
              new Date().toISOString(),
          }),

      addEvent:
        (event) =>
          set((state) => ({
            events: [
              event,

              ...state.events.filter(
                (item) =>
                  item.event_id !==
                  event.event_id
              ),
            ].slice(0, 100),

            lastUpdate:
              new Date().toISOString(),
          })),

      addAlert:
        (alert) =>
          set((state) => ({
            alerts: [
              alert,

              ...state.alerts.filter(
                (item) => {
                  if (
                    alert.event_id &&
                    item.event_id
                  ) {
                    return (
                      item.event_id !==
                      alert.event_id
                    );
                  }

                  return (
                    item.alert_id !==
                    alert.alert_id
                  );
                }
              ),
            ].slice(0, 100),

            lastUpdate:
              new Date().toISOString(),
          })),

      setSystem:
        (system) =>
          set({
            system,

            lastUpdate:
              new Date().toISOString(),
          }),

      acknowledgeAlertLocally:
        (
          alertId,
          note
        ) =>
          set((state) => ({
            alerts:
              state.alerts.map(
                (alert) =>
                  alert.alert_id ===
                  alertId
                    ? {
                        ...alert,

                        status:
                          "ACKNOWLEDGED",

                        acknowledgement_note:
                          note,

                        acknowledged_at:
                          new Date().toISOString(),
                      }
                    : alert
              ),
          })),
    })
  );

