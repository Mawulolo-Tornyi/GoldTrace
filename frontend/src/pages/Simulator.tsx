import {
  Activity,
  Car,
  CircleCheck,
  Clock3,
  CloudRain,
  FlaskConical,
  Hammer,
  Play,
  RadioTower,
  RefreshCcw,
  ShieldAlert,
  Waves,
  WifiOff,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import type {
  LucideIcon,
} from "lucide-react";

import { toast } from "sonner";

import {
  simulatorApi,
} from "../api/goldtraceApi";


interface SimulatorMetadata {
  mode: string;

  source: string;

  aliases:
    Record<string, string>;

  underlying_scenarios:
    string[];

  critical_wait_seconds:
    number;
}


interface SimulatorEvidence {
  persistence_seconds?: number;

  persistent_activity?: boolean;

  required_persistence_seconds?:
    number;

  multi_sensor_confirmation?:
    boolean;
}


interface SimulatorLocation {
  segment_id?: string;
}


interface AgencyAlert {
  eligible?: boolean;

  dispatch_mode?: string;

  dispatch_status?: string;

  reason?: string;
}


interface SimulatorDecision {
  event_id?: string | null;

  prediction?: string;

  human_description?: string;

  risk_level?: string;

  confidence?: number;

  suspected_zone?: string;

  recommendation?: string;

  evidence?: SimulatorEvidence;

  location?: SimulatorLocation | null;

  agency_alert?: AgencyAlert;
}


interface ScenarioCard {
  key: string;

  title: string;

  description: string;

  icon: LucideIcon;

  category:
    | "safe"
    | "environment"
    | "machinery"
    | "warning"
    | "critical"
    | "failure";
}


const scenarios:
  ScenarioCard[] = [
    {
      key: "normal",

      title:
        "Normal River",

      description:
        "Healthy river conditions with no suspicious machinery evidence.",

      icon:
        Waves,

      category:
        "safe",
    },

    {
      key: "rain",

      title:
        "Heavy Rain",

      description:
        "High turbidity caused by environmental rainfall without mining evidence.",

      icon:
        CloudRain,

      category:
        "environment",
    },

    {
      key: "vehicle",

      title:
        "Vehicle",

      description:
        "Machinery-like sound and vibration without enough river evidence for mining.",

      icon:
        Car,

      category:
        "machinery",
    },

    {
      key: "rain-vehicle",

      title:
        "Rain + Vehicle",

      description:
        "Combined rainfall and vehicle activity for false-positive resistance testing.",

      icon:
        CloudRain,

      category:
        "environment",
    },

    {
      key: "rain-machinery",

      title:
        "Rain + Machinery",

      description:
        "Environmental disturbance combined with machinery signatures.",

      icon:
        Hammer,

      category:
        "machinery",
    },

    {
      key: "excavator",

      title:
        "Excavator",

      description:
        "Strong excavator-like machine signatures without sufficient mining evidence.",

      icon:
        Hammer,

      category:
        "machinery",
    },

    {
      key: "mining",

      title:
        "Possible Mining",

      description:
        "Correlated river disturbance and machinery evidence producing HIGH risk.",

      icon:
        ShieldAlert,

      category:
        "warning",
    },

    {
      key: "critical",

      title:
        "Critical Mining",

      description:
        "Persistent multi-sensor evidence. Demonstrates HIGH progressing to CRITICAL.",

      icon:
        FlaskConical,

      category:
        "critical",
    },

    {
      key: "sensor-failure",

      title:
        "Sensor Failure",

      description:
        "Simulates unreliable sensor evidence and should produce SYSTEM_UNCERTAIN.",

      icon:
        RadioTower,

      category:
        "failure",
    },

    {
      key:
        "communication-failure",

      title:
        "Communication Failure",

      description:
        "Simulates unsynchronized node communication and safe uncertainty handling.",

      icon:
        WifiOff,

      category:
        "failure",
    },
  ];


function sleep(
  milliseconds: number
) {
  return new Promise<void>(
    (resolve) => {
      window.setTimeout(
        resolve,
        milliseconds
      );
    }
  );
}


function decisionFrom(
  data: unknown
): SimulatorDecision {
  if (
    typeof data !== "object" ||
    data === null
  ) {
    return {};
  }

  const root =
    data as Record<
      string,
      unknown
    >;

  const result =
    root.result;

  if (
    typeof result === "object" &&
    result !== null
  ) {
    return (
      result as SimulatorDecision
    );
  }

  return (
    root as SimulatorDecision
  );
}


function errorMessage(
  error: unknown
): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error
  ) {
    const response = (
      error as {
        response?: {
          data?: {
            detail?: unknown;
          };
        };
      }
    ).response;

    const detail =
      response?.data?.detail;

    if (
      typeof detail === "string"
    ) {
      return detail;
    }
  }

  if (
    error instanceof Error
  ) {
    return error.message;
  }

  return (
    "The GoldTrace simulator "
    + "request failed."
  );
}


function percentage(
  value?: number
) {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  return `${(
    value * 100
  ).toFixed(1)}%`;
}


function seconds(
  value?: number
) {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return "0.0s";
  }

  return `${value.toFixed(1)}s`;
}


function riskClassName(
  value?: string
) {
  switch (
    value?.toUpperCase()
  ) {
    case "LOW":
      return "risk-low";

    case "MEDIUM":
      return "risk-medium";

    case "HIGH":
      return "risk-high";

    case "CRITICAL":
      return "risk-critical";

    default:
      return "risk-unknown";
  }
}


export default function Simulator() {
  const [
    metadata,
    setMetadata,
  ] =
    useState<
      SimulatorMetadata | null
    >(null);

  const [
    decision,
    setDecision,
  ] =
    useState<
      SimulatorDecision | null
    >(null);

  const [
    busyScenario,
    setBusyScenario,
  ] =
    useState<string | null>(
      null
    );

  const [
    countdown,
    setCountdown,
  ] =
    useState(0);

  const [
    phase,
    setPhase,
  ] =
    useState(
      "Ready for simulation"
    );

  const [
    loadError,
    setLoadError,
  ] =
    useState<string | null>(
      null
    );


  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const response =
          await simulatorApi
            .scenarios();

        if (!active) {
          return;
        }

        setMetadata(
          response.data as SimulatorMetadata
        );

        setLoadError(null);
      } catch (error) {
        if (!active) {
          return;
        }

        setLoadError(
          errorMessage(
            error
          )
        );
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);


  async function resetSimulator(
    showToast = true
  ) {
    try {
      await simulatorApi.reset();

      setDecision(null);

      setCountdown(0);

      setPhase(
        "Simulator state reset"
      );

      if (showToast) {
        toast.success(
          "Simulator reset"
        );
      }
    } catch (error) {
      const message =
        errorMessage(
          error
        );

      toast.error(
        "Unable to reset simulator",
        {
          description:
            message,
        }
      );

      throw error;
    }
  }


  async function runScenario(
    scenario: ScenarioCard
  ) {
    if (
      busyScenario !== null
    ) {
      return;
    }

    if (!metadata) {
      toast.error(
        "Simulator unavailable",
        {
          description:
            loadError ||
            (
              "The backend simulator "
              + "metadata has not loaded."
            ),
        }
      );

      return;
    }

    if (
      metadata.mode
        .toUpperCase()
      !== "DEMO"
    ) {
      toast.error(
        "DEMO mode required",
        {
          description:
            (
              "Simulation is disabled "
              + "outside GoldTrace "
              + "DEMO dispatch mode."
            ),
        }
      );

      return;
    }

    setBusyScenario(
      scenario.key
    );

    setLoadError(null);

    try {
      await resetSimulator(
        false
      );

      setPhase(
        scenario.key ===
        "critical"
          ? "Phase 1 — collecting strong evidence"
          : `Running ${scenario.title}`
      );

      const firstResponse =
        await simulatorApi.run(
          scenario.key,
          42
        );

      let current =
        decisionFrom(
          firstResponse.data
        );

      setDecision(
        current
      );

      if (
        scenario.key !==
        "critical"
      ) {
        setPhase(
          "Simulation complete"
        );

        toast.success(
          `${scenario.title} complete`
        );

        return;
      }

      if (
        current.risk_level ===
        "CRITICAL"
      ) {
        setPhase(
          "CRITICAL state reached"
        );

        toast.success(
          "Critical simulation complete"
        );

        return;
      }

      const wait =
        Math.max(
          1,
          Math.ceil(
            metadata
              .critical_wait_seconds ||
            32
          )
        );

      setPhase(
        "Phase 2 — persistence verification"
      );

      for (
        let remaining = wait;
        remaining > 0;
        remaining -= 1
      ) {
        setCountdown(
          remaining
        );

        await sleep(
          1000
        );
      }

      setCountdown(0);

      setPhase(
        "Phase 2 — processing persistent evidence"
      );

      const secondResponse =
        await simulatorApi.run(
          scenario.key,
          43
        );

      current =
        decisionFrom(
          secondResponse.data
        );

      setDecision(
        current
      );

      setPhase(
        current.risk_level ===
        "CRITICAL"
          ? "Persistence verified — CRITICAL"
          : "Persistence evaluation complete"
      );

      if (
        current.risk_level ===
        "CRITICAL"
      ) {
        toast.error(
          "CRITICAL GoldTrace demo alert",
          {
            description:
              (
                current.human_description ||
                "Suspected galamsey/mining activity requiring investigation."
              ),
          }
        );
      } else {
        toast.success(
          "Critical scenario evaluation complete"
        );
      }
    } catch (error) {
      const message =
        errorMessage(
          error
        );

      setLoadError(
        message
      );

      setPhase(
        "Simulation failed"
      );

      toast.error(
        "Simulation failed",
        {
          description:
            message,
        }
      );
    } finally {
      setCountdown(0);

      setBusyScenario(
        null
      );
    }
  }


  const isBusy =
    busyScenario !== null;


  return (
    <div className="simulator-page">
      <section className="simulator-hero">
        <div>
          <span className="eyebrow purple">
            PRESENTATION LAB
          </span>

          <h2>
            GoldTrace River
            Scenario Simulator
          </h2>

          <p>
            Generate controlled virtual
            sensor conditions and send
            them through the real
            GoldTrace validation,
            machine-learning, risk,
            localization, database and
            live WebSocket pipeline.
          </p>
        </div>

        <div className="simulator-mode-panel">
          <span>
            DISPATCH MODE
          </span>

          <strong>
            {metadata?.mode ||
              "CHECKING"}
          </strong>

          <small>
            Simulated packets are marked
            SIMULATOR and are intended
            for demonstration only.
          </small>
        </div>
      </section>


      {loadError && (
        <div className="simulator-warning">
          <ShieldAlert
            size={18}
          />

          <div>
            <strong>
              Simulator connection issue
            </strong>

            <span>
              {loadError}
            </span>
          </div>
        </div>
      )}


      <section className="simulator-status-strip">
        <div>
          <Activity
            size={17}
          />

          <span>
            STATUS
          </span>

          <strong>
            {phase}
          </strong>
        </div>

        <div>
          <Clock3
            size={17}
          />

          <span>
            PERSISTENCE
          </span>

          <strong>
            {countdown > 0
              ? `${countdown}s`
              : decision
                  ?.evidence
                  ?.persistent_activity
              ? "VERIFIED"
              : "IDLE"}
          </strong>
        </div>

        <button
          type="button"
          className="simulator-reset-button"
          disabled={isBusy}
          onClick={() => {
            void resetSimulator();
          }}
        >
          <RefreshCcw
            size={15}
          />

          Reset
        </button>
      </section>


      <section className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow">
              CONTROL PANEL
            </span>

            <h2>
              Select a River Scenario
            </h2>
          </div>

          <span className="section-meta">
            Real backend pipeline
          </span>
        </div>


        <div className="simulator-scenario-grid">
          {scenarios.map(
            (scenario) => {
              const Icon =
                scenario.icon;

              const active =
                busyScenario ===
                scenario.key;

              return (
                <button
                  key={
                    scenario.key
                  }
                  type="button"
                  disabled={isBusy}
                  className={
                    `simulator-scenario-card simulator-${scenario.category} ${
                      active
                        ? "running"
                        : ""
                    }`
                  }
                  onClick={() => {
                    void runScenario(
                      scenario
                    );
                  }}
                >
                  <div className="simulator-card-top">
                    <span className="simulator-card-icon">
                      <Icon
                        size={21}
                      />
                    </span>

                    {active ? (
                      <Activity
                        className="simulator-spin"
                        size={17}
                      />
                    ) : (
                      <Play
                        size={16}
                      />
                    )}
                  </div>

                  <strong>
                    {scenario.title}
                  </strong>

                  <p>
                    {
                      scenario.description
                    }
                  </p>

                  <span className="simulator-run-label">
                    {active
                      ? "RUNNING"
                      : "RUN SCENARIO"}
                  </span>
                </button>
              );
            }
          )}
        </div>
      </section>


      <section className="dashboard-section">
        <div className="section-title-row">
          <div>
            <span className="eyebrow purple">
              PIPELINE OUTPUT
            </span>

            <h2>
              Latest Simulation Decision
            </h2>
          </div>
        </div>


        {!decision ? (
          <div className="simulator-empty-result">
            <FlaskConical
              size={31}
            />

            <strong>
              No simulation result yet
            </strong>

            <p>
              Select a scenario above.
              The result displayed here
              comes from the GoldTrace
              backend rather than
              frontend mock data.
            </p>
          </div>
        ) : (
          <div className="simulator-result-card">
            <div className="simulator-result-heading">
              <div>
                <span className="eyebrow">
                  DECISION
                </span>

                <h3>
                  {
                    decision
                      .human_description ||
                    decision
                      .prediction ||
                    "GoldTrace result"
                  }
                </h3>
              </div>

              <span
                className={
                  `risk-badge ${
                    riskClassName(
                      decision
                        .risk_level
                    )
                  }`
                }
              >
                {
                  decision
                    .risk_level ||
                  "UNKNOWN"
                }
              </span>
            </div>


            <div className="simulator-result-grid">
              <article>
                <span>
                  CLASSIFICATION
                </span>

                <strong>
                  {
                    decision
                      .prediction ||
                    "—"
                  }
                </strong>
              </article>

              <article>
                <span>
                  CONFIDENCE
                </span>

                <strong>
                  {percentage(
                    decision
                      .confidence
                  )}
                </strong>
              </article>

              <article>
                <span>
                  SUSPECTED ZONE
                </span>

                <strong>
                  {
                    decision
                      .suspected_zone ||
                    "—"
                  }
                </strong>
              </article>

              <article>
                <span>
                  RIVER SEGMENT
                </span>

                <strong>
                  {
                    decision
                      .location
                      ?.segment_id ||
                    "—"
                  }
                </strong>
              </article>

              <article>
                <span>
                  PERSISTENCE
                </span>

                <strong>
                  {seconds(
                    decision
                      .evidence
                      ?.persistence_seconds
                  )}
                </strong>
              </article>

              <article>
                <span>
                  PERSISTENT
                </span>

                <strong>
                  {
                    decision
                      .evidence
                      ?.persistent_activity
                      ? "YES"
                      : "NO"
                  }
                </strong>
              </article>

              <article>
                <span>
                  AGENCY MODE
                </span>

                <strong>
                  {
                    decision
                      .agency_alert
                      ?.dispatch_mode ||
                    metadata?.mode ||
                    "—"
                  }
                </strong>
              </article>

              <article>
                <span>
                  AGENCY STATUS
                </span>

                <strong>
                  {
                    decision
                      .agency_alert
                      ?.dispatch_status ||
                    "NOT_ELIGIBLE"
                  }
                </strong>
              </article>
            </div>


            {decision.recommendation && (
              <div className="simulator-recommendation">
                <CircleCheck
                  size={18}
                />

                <div>
                  <span>
                    SYSTEM RECOMMENDATION
                  </span>

                  <p>
                    {
                      decision
                        .recommendation
                    }
                  </p>
                </div>
              </div>
            )}


            {decision.event_id && (
              <div className="simulator-event-id">
                Event:{" "}
                <strong>
                  {
                    decision
                      .event_id
                  }
                </strong>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
