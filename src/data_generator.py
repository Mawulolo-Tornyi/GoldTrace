from __future__ import annotations

import argparse
from pathlib import Path
import math
import uuid

import numpy as np
import pandas as pd

from .config import ROOT
from .utils import set_seed

SCENARIOS = [
    "NORMAL_RIVER", "RAIN", "HEAVY_RAIN", "THUNDERSTORM", "RUNOFF", "FLOOD_TURBIDITY",
    "WIND", "PEOPLE", "ANIMALS", "MOTORBIKE", "CAR", "TRUCK", "BOAT", "GENERATOR",
    "FARM_MACHINERY", "CONSTRUCTION", "WATER_PUMP", "EXCAVATOR", "MULTIPLE_MACHINES",
    "SENSOR_NOISE", "SENSOR_FAILURE", "COMMUNICATION_FAILURE",
    "POSSIBLE_MINING_ACTIVITY", "HIGH_RISK_MINING_ACTIVITY",
]

MACHINE_SCENARIOS = {
    "MOTORBIKE", "CAR", "TRUCK", "BOAT", "GENERATOR", "FARM_MACHINERY", "CONSTRUCTION",
    "WATER_PUMP", "EXCAVATOR", "MULTIPLE_MACHINES", "POSSIBLE_MINING_ACTIVITY",
    "HIGH_RISK_MINING_ACTIVITY",
}


def _label_for(s: str) -> tuple[str, str, str, str]:
    env = "NORMAL_RIVER"
    audio = "NORMAL_ENVIRONMENT"
    vib = "NORMAL_GROUND"
    fusion = "SAFE"
    if s in {"RAIN", "RUNOFF"}:
        env, audio, fusion = "RAINFALL_RUNOFF", "RAIN", "SUSPICIOUS_ENVIRONMENTAL_CHANGE"
    elif s in {"HEAVY_RAIN", "THUNDERSTORM", "FLOOD_TURBIDITY"}:
        env, audio, fusion = "HEAVY_RAIN_EVENT", "HEAVY_RAIN", "SUSPICIOUS_ENVIRONMENTAL_CHANGE"
    elif s == "WIND":
        audio = "WIND"
    elif s == "PEOPLE":
        audio, vib = "HUMAN_ACTIVITY", "FOOTSTEPS"
        fusion = "MACHINERY_ACTIVITY" if np.random.random() < 0.05 else "SAFE"
    elif s == "ANIMALS":
        vib = "ANIMAL_MOVEMENT"
    elif s in MACHINE_SCENARIOS:
        fusion = "MACHINERY_ACTIVITY"
        if s == "MOTORBIKE": audio, vib = "MOTORBIKE", "MOTORBIKE"
        elif s == "CAR": audio, vib = "VEHICLE", "VEHICLE_PASSING"
        elif s == "TRUCK": audio, vib = "TRUCK", "TRUCK"
        elif s == "BOAT": audio, vib = "BOAT", "CONTINUOUS_ENGINE"
        elif s == "GENERATOR": audio, vib = "GENERATOR", "CONTINUOUS_ENGINE"
        elif s == "FARM_MACHINERY": audio, vib = "FARM_MACHINERY", "HEAVY_MACHINERY"
        elif s == "CONSTRUCTION": audio, vib = "CONSTRUCTION_MACHINERY", "CONSTRUCTION_ACTIVITY"
        elif s == "WATER_PUMP": audio, vib = "WATER_PUMP", "WATER_PUMP_VIBRATION"
        elif s == "EXCAVATOR": audio, vib = "EXCAVATOR_LIKE", "EXCAVATOR_LIKE_VIBRATION"
        elif s == "MULTIPLE_MACHINES": audio, vib = "MULTIPLE_MACHINES", "HEAVY_MACHINERY"
        elif s == "POSSIBLE_MINING_ACTIVITY":
            env, audio, vib, fusion = "DOWNSTREAM_DISTURBANCE", "WATER_PUMP", "HEAVY_MACHINERY", "POSSIBLE_MINING_ACTIVITY"
        elif s == "HIGH_RISK_MINING_ACTIVITY":
            env, audio, vib, fusion = "DOWNSTREAM_DISTURBANCE", "EXCAVATOR_LIKE", "EXCAVATOR_LIKE_VIBRATION", "HIGH_RISK_MINING_ACTIVITY"
    elif s in {"SENSOR_NOISE", "SENSOR_FAILURE", "COMMUNICATION_FAILURE"}:
        env, audio, vib, fusion = "UNKNOWN_ENVIRONMENTAL_CHANGE", "UNKNOWN_AUDIO", "UNKNOWN_VIBRATION", "SYSTEM_UNCERTAIN"
    return env, audio, vib, fusion


def _base_ranges(s: str, rng: np.random.Generator) -> dict[str, float]:
    # Deliberately overlapping distributions. These are development-only surrogates.
    turb_a = rng.normal(18, 8)
    turb_b = turb_a + rng.normal(1, 5)
    temp_a = rng.normal(26.5, 1.5)
    temp_b = temp_a + rng.normal(0.1, 0.4)
    audio_a = abs(rng.normal(0.08, 0.05))
    audio_b = abs(rng.normal(0.09, 0.06))
    vib_a = abs(rng.normal(0.06, 0.04))
    vib_b = abs(rng.normal(0.07, 0.05))
    machine = 0.05
    vib_machine = 0.05
    persistence = max(1.0, rng.gamma(2.0, 4.0))

    if s in {"RAIN", "RUNOFF"}:
        turb_b += rng.normal(25, 18); audio_b += abs(rng.normal(0.18, 0.08)); persistence += rng.uniform(20, 90)
    if s in {"HEAVY_RAIN", "THUNDERSTORM", "FLOOD_TURBIDITY"}:
        turb_a += rng.normal(30, 22); turb_b += rng.normal(55, 30); audio_a += 0.25; audio_b += 0.35; vib_b += 0.08; persistence += rng.uniform(30, 180)
    if s in MACHINE_SCENARIOS:
        strength = rng.uniform(0.35, 0.95)
        audio_b += strength + rng.normal(0, 0.12)
        vib_b += strength * rng.uniform(0.6, 1.0) + rng.normal(0, 0.08)
        machine = np.clip(strength + rng.normal(0.05, 0.12), 0, 1)
        vib_machine = np.clip(strength + rng.normal(0.02, 0.14), 0, 1)
        persistence += rng.uniform(5, 80)
    if s == "EXCAVATOR":
        turb_b += rng.normal(15, 15)
    if s == "WATER_PUMP":
        turb_b += rng.normal(7, 12)
    if s == "POSSIBLE_MINING_ACTIVITY":
        turb_b += rng.normal(45, 22); persistence += rng.uniform(15, 80); machine = max(machine, rng.uniform(0.65, 0.95)); vib_machine = max(vib_machine, rng.uniform(0.6, 0.92))
    if s == "HIGH_RISK_MINING_ACTIVITY":
        turb_b += rng.normal(75, 30); persistence += rng.uniform(30, 180); machine = max(machine, rng.uniform(0.8, 0.99)); vib_machine = max(vib_machine, rng.uniform(0.78, 0.99))
    if s == "WIND":
        audio_a += rng.uniform(0.15, 0.5); audio_b += rng.uniform(0.15, 0.5)
    if s in {"PEOPLE", "ANIMALS"}:
        vib_b += rng.uniform(0.05, 0.25); audio_b += rng.uniform(0.02, 0.2)
    if s in {"SENSOR_NOISE", "SENSOR_FAILURE", "COMMUNICATION_FAILURE"}:
        turb_b += rng.normal(0, 80); audio_b += abs(rng.normal(0, 0.6)); vib_b += abs(rng.normal(0, 0.6))

    return dict(
        turbidity_a=max(0, turb_a), turbidity_b=max(0, turb_b),
        temp_a=temp_a, temp_b=temp_b,
        audio_rms_a=max(0, audio_a), audio_rms_b=max(0, audio_b),
        vibration_rms_a=max(0, vib_a), vibration_rms_b=max(0, vib_b),
        audio_machine_probability_a=np.clip(rng.beta(1.5, 12), 0, 1),
        audio_machine_probability_b=np.clip(machine, 0, 1),
        vibration_machinery_probability_a=np.clip(rng.beta(1.4, 13), 0, 1),
        vibration_machinery_probability_b=np.clip(vib_machine, 0, 1),
        persistence_seconds=float(persistence),
    )


def generate_dataset(samples: int = 100_000, seed: int = 42) -> pd.DataFrame:
    set_seed(seed)
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    event_size = 20
    weights = np.ones(len(SCENARIOS), dtype=float)
    weights[SCENARIOS.index("NORMAL_RIVER")] = 2.0
    weights /= weights.sum()
    event_count = int(np.ceil(samples / event_size))
    event_scenarios = rng.choice(SCENARIOS, size=event_count, p=weights)
    for i in range(samples):
        event_idx = i // event_size
        session_idx = event_idx // 10
        scenario = str(event_scenarios[event_idx])
        env, audio, vib, fusion = _label_for(scenario)
        vals = _base_ranges(scenario, rng)
        turb_diff = vals["turbidity_b"] - vals["turbidity_a"]
        audio_diff = vals["audio_rms_b"] - vals["audio_rms_a"]
        vib_diff = vals["vibration_rms_b"] - vals["vibration_rms_a"]
        row = {
            "event_id": f"SYN-E{event_idx:06d}",
            "session_id": f"SYN-S{session_idx:05d}",
            "location_id": f"LOC-{event_idx % 12:02d}",
            "scenario": scenario,
            **vals,
            "turbidity_difference": turb_diff,
            "turbidity_ratio": vals["turbidity_b"] / max(vals["turbidity_a"], 1.0),
            "turbidity_percent_increase": 100.0 * turb_diff / max(vals["turbidity_a"], 1.0),
            "temperature_difference": vals["temp_b"] - vals["temp_a"],
            "audio_rms_difference": audio_diff,
            "vibration_rms_difference": vib_diff,
            "audio_machine_probability_difference": vals["audio_machine_probability_b"] - vals["audio_machine_probability_a"],
            "vibration_machinery_probability_difference": vals["vibration_machinery_probability_b"] - vals["vibration_machinery_probability_a"],
            "anomaly_score": float(np.clip(rng.beta(2, 7) + (0.35 if fusion in {"POSSIBLE_MINING_ACTIVITY", "HIGH_RISK_MINING_ACTIVITY", "SYSTEM_UNCERTAIN"} else 0), 0, 1)),
            "battery_voltage_a": float(rng.normal(12.4, 0.35)),
            "battery_voltage_b": float(rng.normal(12.3, 0.4)),
            "lora_rssi_a": float(rng.normal(-78, 10)),
            "lora_rssi_b": float(rng.normal(-80, 11)),
            "environment_label": env,
            "audio_label": audio,
            "vibration_label": vib,
            "fusion_label": fusion,
            "verified": False,
        }
        # Inject realistic missing values and outliers.
        if rng.random() < 0.012:
            row[str(rng.choice(["turbidity_b", "audio_rms_b", "vibration_rms_b", "temp_b"]))] = np.nan
        if rng.random() < 0.005:
            row["turbidity_b"] = float(max(0, row.get("turbidity_b", 0) or 0) + rng.uniform(150, 600))
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GoldTrace synthetic development data")
    parser.add_argument("--samples", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/synthetic/goldtrace_sensor_windows.csv")
    args = parser.parse_args()
    df = generate_dataset(args.samples, args.seed)
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Generated {len(df):,} synthetic windows -> {out}")
    print("WARNING: Synthetic metrics validate software architecture only, not real-world accuracy.")


if __name__ == "__main__":
    main()
