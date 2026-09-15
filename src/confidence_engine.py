from __future__ import annotations
import numpy as np

HEALTH_SCORE={'HEALTHY':1.0,'DEGRADED':0.7,'FAILED':0.2,'UNKNOWN':0.4}


def calculate_confidence(
    fusion: float,
    audio: float,
    vibration: float,
    environment: float,
    sensor_health: list[str],
    sync_quality: float = 1.0,
    ood_score: float = 0.0,
    available_fraction: float = 1.0,
    evidence_strengths: list[float] | None = None,
) -> float:
    """Estimate confidence in the *incident-level* decision.

    Exact audio/vibration class confidence is useful, but GoldTrace primarily needs
    confidence that independent sensors jointly support a suspicious event. When
    evidence_strengths are provided, the score therefore gives substantial weight
    to machine/vibration/turbidity agreement instead of requiring certainty about
    the exact machine class (e.g. generator vs excavator).
    """
    model=float(np.mean([fusion,audio,vibration,environment]))
    agreement=1.0-float(np.std([audio,vibration,environment]))
    health=float(np.mean([HEALTH_SCORE.get(h,0.4) for h in sensor_health])) if sensor_health else .4
    if evidence_strengths:
        evidence=float(np.mean(np.clip(np.asarray(evidence_strengths,dtype=float),0,1)))
        score=(.42*float(fusion)+.20*evidence+.12*model+.08*agreement+.08*health+.05*float(sync_quality)+.03*float(available_fraction)+.02*(1-float(ood_score)))
    else:
        score=.38*model+.18*agreement+.18*health+.1*float(sync_quality)+.1*float(available_fraction)+.06*(1-float(ood_score))
    return float(np.clip(score,0,1))
