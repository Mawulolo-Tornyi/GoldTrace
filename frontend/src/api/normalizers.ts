import type {
  Alert,
  GoldTraceEvent,
  ModelInfo,
  Prediction,
  RiskLevel,
  SensorNode,
  SystemStatus,
} from "../types";

type UnknownObject =
  Record<string, unknown>;

function isObject(
  value: unknown
): value is UnknownObject {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function objectOf(
  value: unknown
): UnknownObject {
  return isObject(value)
    ? value
    : {};
}

function textFrom(
  ...values: unknown[]
): string {
  for (const value of values) {
    if (
      typeof value === "string" &&
      value.trim()
    ) {
      return value.trim();
    }

    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {
      return String(value);
    }
  }

  return "";
}

function numberFrom(
  ...values: unknown[]
): number {
  for (const value of values) {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      continue;
    }

    const result =
      Number(value);

    if (
      Number.isFinite(result)
    ) {
      return result;
    }
  }

  return Number.NaN;
}

function numberOr(
  fallback: number,
  ...values: unknown[]
): number {
  const value =
    numberFrom(...values);

  return Number.isFinite(value)
    ? value
    : fallback;
}

function stringArray(
  value: unknown
): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .filter(
      (item) =>
        typeof item === "string"
    )
    .map(
      (item) =>
        String(item)
    );
}

export function normalizeRisk(
  value: unknown
): RiskLevel {
  const risk =
    textFrom(value)
      .toUpperCase();

  switch (risk) {
    case "LOW":
    case "MEDIUM":
    case "HIGH":
    case "CRITICAL":
      return risk as RiskLevel;

    default:
      return "UNKNOWN" as RiskLevel;
  }
}

function normalizeNodeStatus(
  value: unknown
): SensorNode["status"] {
  const status =
    textFrom(value)
      .toUpperCase();

  switch (status) {
    case "ONLINE":
    case "OFFLINE":
    case "STALE":
      return status as SensorNode["status"];

    default:
      return "UNKNOWN" as SensorNode["status"];
  }
}

function normalizeHealth(
  value: unknown
): string {
  const health =
    textFrom(value)
      .toUpperCase();

  if (
    health === "HEALTHY" ||
    health === "DEGRADED" ||
    health === "FAILED"
  ) {
    return health;
  }

  return "UNKNOWN";
}

export function normalizeNode(
  rawValue: unknown,
  existing?: SensorNode,
  riskOverride?: RiskLevel,
  resultValue?: unknown
): SensorNode {
  const raw =
    objectOf(rawValue);

  const result =
    objectOf(resultValue);

  const nodeId =
    textFrom(
      raw.node_id,
      existing?.node_id
    ) || "UNKNOWN_NODE";

  const resultHealth =
    normalizeHealth(
      result.health
    );

  const rawHealth =
    objectOf(
      raw.sensor_health
    );

  const explicitStatus =
    textFrom(
      raw.status
    );

  const status =
    explicitStatus
      ? normalizeNodeStatus(
          explicitStatus
        )
      : existing?.status ||
        ("OFFLINE" as SensorNode["status"]);

  const sensorHealth = {
    turbidity:
      normalizeHealth(
        rawHealth.turbidity ||
          result.health
      ),

    audio:
      normalizeHealth(
        rawHealth.audio ||
          result.health
      ),

    vibration:
      normalizeHealth(
        rawHealth.vibration ||
          result.health
      ),

    temperature:
      normalizeHealth(
        rawHealth.temperature
      ),

    microphone:
      normalizeHealth(
        rawHealth.microphone ||
          rawHealth.audio ||
          result.health
      ),

    geophone:
      normalizeHealth(
        rawHealth.geophone ||
          rawHealth.vibration ||
          result.health
      ),

    lora:
      normalizeHealth(
        rawHealth.lora
      ),

    power:
      normalizeHealth(
        rawHealth.power
      ),

    overall:
      resultHealth,
  } as SensorNode["sensor_health"];

  const lastSeen =
    textFrom(
      raw.last_seen,
      raw.timestamp,
      raw.ts,
      existing?.last_seen
    );

  return {
    ...(existing || {}),

    node_id:
      nodeId,

    name:
      textFrom(
        raw.name,
        existing?.name,
        nodeId
      ),

    latitude:
      numberOr(
        existing?.latitude ??
          Number.NaN,
        raw.latitude,
        raw.lat
      ),

    longitude:
      numberOr(
        existing?.longitude ??
          Number.NaN,
        raw.longitude,
        raw.lng,
        raw.lon
      ),

    river_id:
      textFrom(
        raw.river_id,
        existing?.river_id
      ),

    river_name:
      textFrom(
        raw.river_name,
        existing?.river_name
      ),

    district:
      textFrom(
        raw.district
      ),

    region:
      textFrom(
        raw.region
      ),

    position_order:
      numberOr(
        existing?.position_order ??
          0,
        raw.position_order
      ),

    position_type:
      (
        textFrom(
          raw.position_type,
          existing?.position_type
        ) || "UNKNOWN"
      ) as SensorNode["position_type"],

    status,

    risk:
      normalizeRisk(
        raw.risk ||
          raw.risk_level ||
          riskOverride ||
          existing?.risk
      ),

    turbidity:
      numberOr(
        existing?.turbidity ??
          Number.NaN,

        result.turbidity_ntu,

        raw.turbidity,
        raw.turbidity_ntu,
        raw.ntu
      ),

    temperature:
      numberOr(
        existing?.temperature ??
          Number.NaN,

        raw.temperature,
        raw.temperature_c,
        raw.temp_c
      ),

    environment:
      textFrom(
        result.environment,
        raw.environment,
        existing?.environment
      ) || "UNKNOWN",

    audio_class:
      textFrom(
        result.audio,
        raw.audio_class,
        raw.audio,
        existing?.audio_class
      ) || "UNKNOWN",

    audio_machine_probability:
      numberOr(
        existing?.audio_machine_probability ??
          0,

        result.audio_machine_probability,

        raw.audio_machine_probability,
        raw.machine_probability
      ),

    vibration_class:
      textFrom(
        result.vibration,
        raw.vibration_class,
        raw.vibration,
        existing?.vibration_class
      ) || "UNKNOWN",

    vibration_probability:
      numberOr(
        existing?.vibration_probability ??
          0,

        result.vibration_machinery_probability,

        raw.vibration_probability,
        raw.vibration_machinery_probability
      ),

    dominant_frequency:
      numberOr(
        existing?.dominant_frequency ??
          Number.NaN,

        raw.dominant_frequency,
        raw.dominant_frequency_hz
      ),

    battery:
      numberOr(
        existing?.battery ??
          Number.NaN,

        raw.battery,
        raw.battery_percent,
        raw.battery_level
      ),

    rssi:
      numberOr(
        existing?.rssi ??
          Number.NaN,

        raw.rssi,
        raw.lora_rssi
      ),

    snr:
      numberOr(
        existing?.snr ??
          Number.NaN,

        raw.snr,
        raw.lora_snr
      ),

    sensor_health:
      sensorHealth,

    last_seen:
      lastSeen,
  } as SensorNode;
}


export function normalizePrediction(
  value: unknown
): Prediction | null {
  const raw =
    objectOf(value);

  if (
    Object.keys(raw).length === 0
  ) {
    return null;
  }

  const location =
    objectOf(
      raw.location
    );

  const evidence =
    objectOf(
      raw.evidence
    );

  const classification =
    textFrom(
      raw.prediction,
      raw.classification
    );

  if (
    !classification &&
    !textFrom(
      raw.risk_level,
      raw.risk
    )
  ) {
    return null;
  }

  return {
    event_id:
      textFrom(
        raw.event_id
      ) || "LIVE-EVENT",

    classification:
      classification ||
      "SYSTEM_UNCERTAIN",

    risk:
      normalizeRisk(
        raw.risk_level ||
          raw.risk
      ),

    confidence:
      numberOr(
        0,
        raw.confidence
      ),

    suspected_zone:
      textFrom(
        raw.suspected_zone,
        location.zone_code
      ) || "UNKNOWN",

    river_segment:
      textFrom(
        raw.river_segment,
        location.segment_id
      ) || "UNKNOWN",

    duration_seconds:
      numberOr(
        0,
        raw.duration_seconds,
        evidence.persistence_seconds
      ),

    human_description:
      textFrom(
        raw.human_description
      ),

    recommendation:
      textFrom(
        raw.recommendation
      ),

    reasons:
      stringArray(
        evidence.reasons ||
          raw.reasons
      ),

    timestamp:
      textFrom(
        raw.timestamp
      ),
  } as Prediction;
}


export function mergeRiskUpdate(
  value: unknown,
  current: Prediction | null
): Prediction | null {
  if (!current) {
    return normalizePrediction(
      value
    );
  }

  const raw =
    objectOf(value);

  const rawRisk =
    textFrom(
      raw.risk_level,
      raw.risk
    );

  const rawConfidence =
    numberFrom(
      raw.confidence
    );

  return {
    ...current,

    classification:
      textFrom(
        raw.prediction,
        raw.classification
      ) ||
      current.classification,

    risk:
      rawRisk
        ? normalizeRisk(
            rawRisk
          )
        : current.risk,

    confidence:
      Number.isFinite(
        rawConfidence
      )
        ? rawConfidence
        : current.confidence,
  };
}


export function predictionNodeResults(
  value: unknown
): Record<
  string,
  unknown
> {
  const raw =
    objectOf(value);

  return objectOf(
    raw.node_results
  );
}


export function normalizeNodes(
  value: unknown,
  predictionRaw?: unknown
): SensorNode[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const prediction =
    normalizePrediction(
      predictionRaw
    );

  const results =
    predictionNodeResults(
      predictionRaw
    );

  return value.map(
    (item) => {
      const meta =
        objectOf(item);

      const nodeId =
        textFrom(
          meta.node_id
        );

      return normalizeNode(
        item,
        undefined,
        prediction?.risk,
        results[nodeId]
      );
    }
  );
}


export function normalizeEvent(
  value: unknown
): GoldTraceEvent | null {
  const raw =
    objectOf(value);

  const prediction =
    normalizePrediction(
      raw.result || raw
    );

  if (!prediction) {
    return null;
  }

  const source =
    objectOf(
      raw.result || raw
    );

  return {
    event_id:
      prediction.event_id,

    timestamp:
      textFrom(
        source.timestamp
      ) ||
      new Date().toISOString(),

    prediction:
      prediction.classification,

    risk:
      prediction.risk,

    confidence:
      prediction.confidence,

    zone:
      prediction.suspected_zone,

    duration_seconds:
      prediction.duration_seconds,

    status:
      textFrom(
        raw.status
      ) ||
      (
        prediction.risk ===
          "CRITICAL" ||
        prediction.risk ===
          "HIGH"
          ? "ACTIVE"
          : "RECORDED"
      ),
  } as GoldTraceEvent;
}


export function normalizeEvents(
  value: unknown
): GoldTraceEvent[] {
  const input =
    Array.isArray(value)
      ? value
      : value
      ? [value]
      : [];

  const unique =
    new Map<
      string,
      GoldTraceEvent
    >();

  for (
    const item of input
  ) {
    const event =
      normalizeEvent(
        item
      );

    if (
      event &&
      !unique.has(
        event.event_id
      )
    ) {
      unique.set(
        event.event_id,
        event
      );
    }
  }

  return Array.from(
    unique.values()
  );
}


function normalizeAlertStatus(
  value: unknown
): string {
  const status =
    textFrom(value)
      .toUpperCase();

  if (
    status ===
      "ACKNOWLEDGED" ||
    status ===
      "RESOLVED"
  ) {
    return status;
  }

  // Backend DISPATCHED means delivery happened.
  // Operator acknowledgement is still pending.
  return "ACTIVE";
}


export function normalizeAlert(
  value: unknown
): Alert | null {
  const raw =
    objectOf(value);

  if (
    Object.keys(raw).length === 0
  ) {
    return null;
  }

  const result =
    objectOf(
      raw.result
    );

  const location =
    objectOf(
      result.location
    );

  const alertId =
    textFrom(
      raw.alert_id
    );

  if (!alertId) {
    return null;
  }

  return {
    alert_id:
      alertId,

    event_id:
      textFrom(
        raw.event_id,
        result.event_id
      ),

    severity:
      normalizeRisk(
        raw.risk_level ||
          raw.severity ||
          result.risk_level
      ),

    location:
      textFrom(
        raw.location,
        location.segment_id,
        location.zone_code,
        result.suspected_zone
      ) || "UNKNOWN",

    timestamp:
      textFrom(
        raw.timestamp,
        raw.ts,
        result.timestamp
      ) ||
      new Date().toISOString(),

    message:
      textFrom(
        raw.message,
        result.alert_message,
        result.human_description
      ) ||
      "Suspected galamsey/mining activity requiring investigation.",

    status:
      normalizeAlertStatus(
        raw.status
      ),

    acknowledgement_note:
      textFrom(
        raw.acknowledgement_note,
        raw.notes
      ),
  } as Alert;
}


export function normalizeAlerts(
  value: unknown
): Alert[] {
  const input =
    Array.isArray(value)
      ? value
      : value
      ? [value]
      : [];

  /*
   * GoldTrace may have several delivery rows
   * for the same event.
   * Show one response alert per event.
   */
  const unique =
    new Map<
      string,
      Alert
    >();

  for (
    const item of input
  ) {
    const alert =
      normalizeAlert(
        item
      );

    if (!alert) {
      continue;
    }

    const key =
      alert.event_id ||
      alert.alert_id;

    if (
      !unique.has(key)
    ) {
      unique.set(
        key,
        alert
      );
    }
  }

  return Array.from(
    unique.values()
  );
}


export function normalizeSystem(
  value: unknown
): SystemStatus {
  const raw =
    objectOf(value);

  const modelStatus =
    objectOf(
      raw.models
    );

  const loadedFlags =
    Object.entries(
      modelStatus
    )
      .filter(
        ([key]) =>
          key.endsWith(
            "_loaded"
          )
      )
      .map(
        ([, flag]) =>
          flag === true
      );

  const modelsHealthy =
    loadedFlags.length > 0 &&
    loadedFlags.every(
      Boolean
    );

  const nodesSeen =
    Array.isArray(
      raw.nodes_seen
    )
      ? raw.nodes_seen
      : [];

  const websocketClients =
    numberOr(
      0,
      raw.websocket_clients
    );

  return {
    raspberry_pi:
      textFrom(
        raw.system
      ) === "GoldTrace"
        ? "CONNECTED"
        : "UNKNOWN",

    api:
      "ONLINE",

    websocket:
      websocketClients > 0
        ? "CONNECTED"
        : "AVAILABLE",

    lora:
      nodesSeen.length > 0
        ? "CONNECTED"
        : "UNKNOWN",

    cellular:
      "UNKNOWN",

    ml_engine:
      modelsHealthy
        ? "ONLINE"
        : loadedFlags.length > 0
        ? "DEGRADED"
        : "UNKNOWN",

    database:
      "ONLINE",

    cpu:
      numberFrom(
        raw.cpu,
        raw.cpu_percent
      ),

    ram:
      numberFrom(
        raw.ram,
        raw.ram_percent
      ),

    storage:
      numberFrom(
        raw.storage,
        raw.storage_percent
      ),

    temperature:
      numberFrom(
        raw.temperature,
        raw.cpu_temperature
      ),

    uptime:
      textFrom(
        raw.uptime
      ) ||
      "Not reported",

    last_prediction:
      textFrom(
        raw.last_prediction
      ),
  } as SystemStatus;
}


function titleFromKey(
  value: string
): string {
  return value
    .replace(
      /_/g,
      " "
    )
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}


export function normalizeModels(
  value: unknown
): ModelInfo[] {
  if (
    Array.isArray(value)
  ) {
    return value.map(
      (item, index) => {
        const raw =
          objectOf(item);

        return {
          id:
            textFrom(
              raw.id,
              raw.name
            ) ||
            `model-${index}`,

          name:
            textFrom(
              raw.name
            ) ||
            `Model ${index + 1}`,

          version:
            textFrom(
              raw.version
            ) ||
            "Unknown",

          framework:
            textFrom(
              raw.framework,
              raw.library
            ) ||
            "GoldTrace ML",

          runtime:
            textFrom(
              raw.runtime
            ) ||
            "Unknown",

          status:
            textFrom(
              raw.status
            ) ||
            (
              raw.loaded === true
                ? "LOADED"
                : "UNKNOWN"
            ),

          metric_name:
            textFrom(
              raw.metric_name
            ),

          metric_value:
            numberFrom(
              raw.metric_value
            ),

          last_trained:
            textFrom(
              raw.last_trained
            ),
        } as ModelInfo;
      }
    );
  }

  const registry =
    objectOf(value);

  return Object.entries(
    registry
  ).map(
    ([key, item]) => {
      const raw =
        objectOf(item);

      const loaded =
        raw.loaded === true ||
        raw.status === "LOADED";

      return {
        id:
          textFrom(
            raw.id
          ) || key,

        name:
          textFrom(
            raw.name
          ) ||
          titleFromKey(key),

        version:
          textFrom(
            raw.version,
            raw.model_version
          ) ||
          "Unknown",

        framework:
          textFrom(
            raw.framework,
            raw.library
          ) ||
          "GoldTrace ML",

        runtime:
          textFrom(
            raw.runtime
          ) ||
          "Unknown",

        status:
          loaded
            ? "LOADED"
            : textFrom(
                raw.status
              ) ||
              "AVAILABLE",

        metric_name:
          textFrom(
            raw.metric_name
          ),

        metric_value:
          numberFrom(
            raw.metric_value
          ),

        last_trained:
          textFrom(
            raw.last_trained
          ),
      } as ModelInfo;
    }
  );
}



