import type { RiskLevel } from "../types";


export function percent(
  value: number,
  fallback = "—"
): string {
  if (!Number.isFinite(value)) {
    return fallback;
  }

  if (value <= 1) {
    return `${Math.round(value * 100)}%`;
  }

  return `${Math.round(value)}%`;
}


export function formatNumber(
  value: number,
  digits = 1,
  fallback = "—"
): string {
  if (!Number.isFinite(value)) {
    return fallback;
  }

  return value.toFixed(digits);
}


export function valueWithUnit(
  value: number,
  unit: string,
  digits = 1,
  fallback = "—"
): string {
  if (!Number.isFinite(value)) {
    return fallback;
  }

  return `${value.toFixed(digits)}${unit}`;
}


export function integerWithUnit(
  value: number,
  unit: string,
  fallback = "—"
): string {
  if (!Number.isFinite(value)) {
    return fallback;
  }

  return `${Math.round(value)}${unit}`;
}


export function riskClass(
  risk: RiskLevel
): string {
  switch (risk) {
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


export function relativeTime(
  isoDate: string
): string {
  if (!isoDate) {
    return "Never";
  }

  const time =
    new Date(isoDate).getTime();

  if (!Number.isFinite(time)) {
    return "Never";
  }

  const seconds =
    Math.max(
      0,
      Math.round(
        (Date.now() - time) / 1000
      )
    );

  if (seconds < 60) {
    return `${seconds}s ago`;
  }

  const minutes =
    Math.floor(seconds / 60);

  if (minutes < 60) {
    return `${minutes}m ago`;
  }

  const hours =
    Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours}h ago`;
  }

  const days =
    Math.floor(hours / 24);

  return `${days}d ago`;
}
