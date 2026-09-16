import {
  useEffect,
  useRef,
} from "react";

import {
  toast,
} from "sonner";

import {
  alertsApi,
  eventsApi,
  nodesApi,
  predictionsApi,
  systemApi,
} from "../api/goldtraceApi";

import {
  mergeRiskUpdate,
  normalizeAlert,
  normalizeAlerts,
  normalizeEvent,
  normalizeEvents,
  normalizeNode,
  normalizeNodes,
  normalizePrediction,
  normalizeSystem,
  predictionNodeResults,
} from "../api/normalizers";

import {
  useLiveStore,
} from "../store/liveStore";

import type {
  Prediction,
  SensorNode,
} from "../types";


const WS_URL =
  import.meta.env.VITE_WS_URL ||
  "ws://127.0.0.1:8000/ws/live";


function isObject(
  value: unknown
): value is Record<
  string,
  unknown
> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}


function applyPredictionToNodes(
  rawPrediction: unknown,
  prediction: Prediction | null
) {
  const results =
    predictionNodeResults(
      rawPrediction
    );

  for (
    const [
      nodeId,
      nodeResult,
    ] of Object.entries(
      results
    )
  ) {
    const store =
      useLiveStore.getState();

    const existing =
      store.nodes.find(
        (node) =>
          node.node_id ===
          nodeId
      );

    if (!existing) {
      continue;
    }

    store.updateNode(
      normalizeNode(
        {
          node_id:
            nodeId,
        },

        existing,

        prediction?.risk,

        nodeResult
      )
    );
  }
}


export function useGoldTraceRuntime() {
  const retryDelay =
    useRef(1000);

  useEffect(() => {
    const initial =
      useLiveStore.getState();

    // DEMO
    if (initial.demoMode) {
      initial.setConnected(
        true
      );

      const timer =
        window.setInterval(
          () => {
            const current =
              useLiveStore.getState();

            current.nodes.forEach(
              (node) => {
                const upstream =
                  node.position_type ===
                  "UPSTREAM";

                const jitter =
                  () =>
                    Math.random() -
                    0.5;

                current.updateNode({
                  ...node,

                  turbidity:
                    Math.max(
                      0,

                      (
                        upstream
                          ? 18.6
                          : 92.5
                      ) +
                        jitter() *
                          (
                            upstream
                              ? 1.7
                              : 7
                          )
                    ),

                  temperature:
                    Math.max(
                      0,
                      node.temperature +
                        jitter() *
                          0.25
                    ),

                  audio_machine_probability:
                    Math.min(
                      1,
                      Math.max(
                        0,

                        (
                          upstream
                            ? 0.07
                            : 0.91
                        ) +
                          jitter() *
                            0.045
                      )
                    ),

                  vibration_probability:
                    Math.min(
                      1,
                      Math.max(
                        0,

                        (
                          upstream
                            ? 0.08
                            : 0.87
                        ) +
                          jitter() *
                            0.04
                      )
                    ),

                  rssi:
                    Math.round(
                      node.rssi +
                        jitter() *
                          3
                    ),

                  last_seen:
                    new Date()
                      .toISOString(),
                });
              }
            );
          },
          2500
        );

      return () =>
        window.clearInterval(
          timer
        );
    }


    let socket:
      WebSocket | null =
      null;

    let reconnectTimer:
      number | undefined;
    let stopped =
      false;


    async function bootstrap() {
      const results =
        await Promise.allSettled([
          nodesApi.all(),
          predictionsApi.latest(),
          alertsApi.all(),
          eventsApi.all(),
          systemApi.status(),
        ]);

      const [
        nodesResult,
        predictionResult,
        alertsResult,
        eventsResult,
        systemResult,
      ] = results;


      const rawPrediction =
        predictionResult.status ===
        "fulfilled"
          ? predictionResult
              .value.data
          : null;


      const prediction =
        normalizePrediction(
          rawPrediction
        );


      if (
        nodesResult.status ===
        "fulfilled"
      ) {
        useLiveStore.setState({
          nodes:
            normalizeNodes(
              nodesResult
                .value.data,

              rawPrediction
            ),
        });
      }


      if (prediction) {
        useLiveStore
          .getState()
          .setPrediction(
            prediction
          );

        applyPredictionToNodes(
          rawPrediction,
          prediction
        );
      }


      if (
        alertsResult.status ===
        "fulfilled"
      ) {
        useLiveStore.setState({
          alerts:
            normalizeAlerts(
              alertsResult
                .value.data
            ),
        });
      }


      if (
        eventsResult.status ===
        "fulfilled"
      ) {
        useLiveStore.setState({
          events:
            normalizeEvents(
              eventsResult
                .value.data
            ),
        });
      }


      if (
        systemResult.status ===
        "fulfilled"
      ) {
        useLiveStore
          .getState()
          .setSystem(
            normalizeSystem(
              systemResult
                .value.data
            )
          );
      }
    }


    function scheduleReconnect() {
      if (stopped) {
        return;
      }

      if (reconnectTimer) {
        window.clearTimeout(
          reconnectTimer
        );
      }

      reconnectTimer =
        window.setTimeout(
          () => {
            retryDelay.current =
              Math.min(
                retryDelay.current *
                  2,
                30000
              );

            connect();
          },

          retryDelay.current
        );
    }


    function handlePacket(
      rawText: string
    ) {
      try {
        const packet:
          unknown =
          JSON.parse(
            rawText
          );

        if (
          !isObject(packet)
        ) {
          return;
        }

        const type =
          packet.type;

        const data =
          packet.data;


        switch (type) {
          case "sensor_update": {
            if (
              !isObject(data) ||
              typeof data.node_id !==
                "string"
            ) {
              return;
            }

            const store =
              useLiveStore.getState();

            const existing =
              store.nodes.find(
                (node) =>
                  node.node_id ===
                  data.node_id
              );

            const node =
              normalizeNode(
                data,
                existing,
                store.prediction
                  ?.risk
              );

            store.updateNode(
              node
            );

            break;
          }


          case "prediction_update": {
            const prediction =
              normalizePrediction(
                data
              );

            if (!prediction) {
              return;
            }

            const store =
              useLiveStore.getState();

            store.setPrediction(
              prediction
            );

            applyPredictionToNodes(
              data,
              prediction
            );

            break;
          }


          case "risk_update": {
            const store =
              useLiveStore.getState();

            const merged =
              mergeRiskUpdate(
                data,
                store.prediction
              );

            if (merged) {
              store.setPrediction(
                merged
              );
            }

            break;
          }


          case "event": {
            const event =
              normalizeEvent(
                data
              );

            if (event) {
              useLiveStore
                .getState()
                .addEvent(
                  event
                );
            }

            break;
          }


          case "alert": {
            const alert =
              normalizeAlert(
                data
              );

            if (!alert) {
              return;
            }

            useLiveStore
              .getState()
              .addAlert(
                alert
              );

            if (
              alert.severity ===
              "CRITICAL"
            ) {
              toast.error(
                "CRITICAL GOLDTRACE ALERT",
                {
                  description:
                    alert.message ||
                    "Suspected galamsey/mining activity requiring investigation.",
                }
              );
            }

            break;
          }


          case "node_status": {
            if (
              !isObject(data) ||
              typeof data.node_id !==
                "string"
            ) {
              return;
            }

            const store =
              useLiveStore.getState();

            const existing =
              store.nodes.find(
                (node) =>
                  node.node_id ===
                  data.node_id
              );

            if (!existing) {
              return;
            }

            store.updateNode(
              normalizeNode(
                data,
                existing,
                store.prediction
                  ?.risk
              )
            );

            break;
          }


          case "system_status": {
            useLiveStore
              .getState()
              .setSystem(
                normalizeSystem(
                  data
                )
              );

            break;
          }


          case "heartbeat":
            useLiveStore
              .getState()
              .setConnected(
                true
              );

            break;


          default:
            console.warn(
              "Unknown GoldTrace WebSocket packet:",
              packet
            );
        }
      } catch (error) {
        console.error(
          "Malformed GoldTrace WebSocket message:",
          error
        );
      }
    }


    function connect() {
      if (stopped) {
        return;
      }

      useLiveStore
        .getState()
        .setConnected(
          false
        );

      try {
        socket =
          new WebSocket(
            WS_URL
          );
      } catch {
        scheduleReconnect();
        return;
      }


      socket.onopen =
        () => {
          retryDelay.current =
            1000;

          useLiveStore
            .getState()
            .setConnected(
              true
            );
        };


      socket.onmessage =
        (event) => {
          handlePacket(
            String(
              event.data
            )
          );
        };


      socket.onerror =
        () => {
          useLiveStore
            .getState()
            .setConnected(
              false
            );
        };


      socket.onclose =
        () => {
          useLiveStore
            .getState()
            .setConnected(
              false
            );

          scheduleReconnect();
        };
    }


    bootstrap()
      .catch(
        (error) => {
          console.error(
            "GoldTrace REST bootstrap failed:",
            error
          );
        }
      )
      .finally(
        () => {
          connect();
        }
      );


    const staleTimer =
      window.setInterval(
        () => {
          const store =
            useLiveStore.getState();

          const now =
            Date.now();

          store.nodes.forEach(
            (
              node: SensorNode
            ) => {
              if (
                !node.last_seen
              ) {
                return;
              }

              const timestamp =
                new Date(
                  node.last_seen
                ).getTime();

              if (
                !Number.isFinite(
                  timestamp
                )
              ) {
                return;
              }

              if (
                now -
                  timestamp >
                  60000 &&
                node.status ===
                  "ONLINE"
              ) {
                store.updateNode({
                  ...node,
                  status:
                    "STALE",
                });
              }
            }
          );
        },

        10000
      );


    return () => {
      stopped =
        true;

      if (reconnectTimer) {
        window.clearTimeout(
          reconnectTimer
        );
      }

      if (staleTimer) {
        window.clearInterval(
          staleTimer
        );
      }

      socket?.close();
    };
  }, []);
}


