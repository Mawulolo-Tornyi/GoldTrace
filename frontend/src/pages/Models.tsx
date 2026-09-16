import {
  BrainCircuit,
  Cpu,
  Database,
} from "lucide-react";

import {
  useQuery,
} from "@tanstack/react-query";

import {
  modelsApi,
} from "../api/goldtraceApi";

import { useLiveStore } from "../store/liveStore";
import { normalizeModels } from "../api/normalizers";

import type {
  ModelInfo,
} from "../types";

const demoModels:
  ModelInfo[] = [
    {
      id:
        "audio",
      name:
        "Audio Classification Model",
      version:
        "goldtrace_audio_v1",
      framework:
        "Scikit-learn / PyTorch",
      runtime:
        "Development",
      status:
        "LOADED",
    },

    {
      id:
        "vibration",
      name:
        "Vibration Classification Model",
      version:
        "goldtrace_vibration_v1",
      framework:
        "Scikit-learn / PyTorch",
      runtime:
        "Development",
      status:
        "LOADED",
    },

    {
      id:
        "environment",
      name:
        "Environmental Model",
      version:
        "goldtrace_environment_v1",
      framework:
        "Scikit-learn",
      runtime:
        "Development",
      status:
        "LOADED",
    },

    {
      id:
        "anomaly",
      name:
        "Anomaly Detection Model",
      version:
        "goldtrace_anomaly_v1",
      framework:
        "Isolation Forest",
      runtime:
        "Development",
      status:
        "LOADED",
    },

    {
      id:
        "fusion",
      name:
        "Sensor Fusion Model",
      version:
        "goldtrace_fusion_v1",
      framework:
        "Scikit-learn",
      runtime:
        "Development",
      status:
        "LOADED",
    },
  ];

export default function Models() {
  const demoMode =
    useLiveStore(
      (state) =>
        state.demoMode
    );

  const query =
    useQuery({
      queryKey:
        ["goldtrace-models"],

      queryFn:
        async () =>
          (
            await modelsApi.all()
          ).data,

      enabled:
        !demoMode,

      retry:
        1,
    });

  const models = demoMode ? demoModels : normalizeModels(query.data);

  return (
    <div>
      <div className="page-heading models-heading">
        <div>
          <span className="eyebrow purple">
            MACHINE
            INTELLIGENCE
          </span>

          <h2>
            ML Models
          </h2>

          <p>
            Models currently available
            to the GoldTrace inference
            pipeline.
          </p>
        </div>

        {demoMode && (
          <div className="model-demo-notice">
            DEMO MODEL METADATA
          </div>
        )}
      </div>

      {!demoMode &&
        query.isLoading && (
          <div className="empty-state">
            <BrainCircuit
              size={30}
            />

            <strong>
              Loading models
            </strong>
          </div>
        )}

      {!demoMode &&
        query.isError && (
          <div className="error-panel">
            <strong>
              Unable to load model
              information.
            </strong>

            <p>
              The endpoint
              GET /models could not
              be reached.
            </p>

            <button
              onClick={() =>
                query.refetch()
              }
            >
              Retry
            </button>
          </div>
        )}

      <div className="models-page-grid">
        {models.map(
          (model) => (
            <article
              className="model-information-card"
              key={
                model.id
              }
            >
              <div className="model-information-top">
                <div className="model-icon">
                  <BrainCircuit
                    size={21}
                  />
                </div>

                <span
                  className={
                    model.status.toUpperCase() ===
                    "LOADED"
                      ? "model-loaded"
                      : "model-unavailable"
                  }
                >
                  {
                    model.status
                  }
                </span>
              </div>

              <h3>
                {model.name}
              </h3>

              <p>
                {model.version}
              </p>

              <div className="model-properties">
                <div>
                  <Cpu
                    size={14}
                  />

                  <span>
                    Framework
                  </span>

                  <strong>
                    {
                      model.framework
                    }
                  </strong>
                </div>

                <div>
                  <Database
                    size={14}
                  />

                  <span>
                    Runtime
                  </span>

                  <strong>
                    {
                      model.runtime
                    }
                  </strong>
                </div>
              </div>

              {model.metric_name &&
                model.metric_value !==
                  undefined && (
                  <div className="model-metric">
                    <span>
                      {
                        model.metric_name
                      }
                    </span>

                    <strong>
                      {
                        model.metric_value
                      }
                    </strong>
                  </div>
                )}

              {model.last_trained && (
                <div className="model-trained">
                  Last trained:{" "}
                  {
                    model.last_trained
                  }
                </div>
              )}
            </article>
          )
        )}
      </div>
    </div>
  );
}

