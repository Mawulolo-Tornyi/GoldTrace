from __future__ import annotations
from typing import Any
from .config import load_settings

RANK = {'UNKNOWN': -1, 'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}


def evaluate_agency_alert(result: dict[str, Any]) -> dict[str, Any]:
    cfg = load_settings().get('agency_alerts', {})
    mode = str(cfg.get('dispatch_mode', 'DEMO')).upper()
    if not cfg.get('enabled', False):
        return {'eligible': False, 'reason': 'Agency alerts disabled', 'dispatch_mode': mode}
    if result.get('prediction') == 'SYSTEM_UNCERTAIN' or result.get('risk_level') == 'UNKNOWN':
        return {'eligible': False, 'reason': 'System uncertain', 'dispatch_mode': mode}

    risk = str(result.get('risk_level', 'UNKNOWN'))
    threshold = 'HIGH' if mode == 'AUTOMATIC_HIGH_AND_CRITICAL' else ('CRITICAL' if mode == 'AUTOMATIC_CRITICAL' else str(cfg.get('dispatch_threshold', 'CRITICAL')))
    if RANK.get(risk, -1) < RANK.get(threshold, 3):
        return {'eligible': False, 'reason': f'Risk below {threshold}', 'dispatch_mode': mode}

    confidence = float(result.get('confidence', 0.0))
    if confidence < float(cfg.get('minimum_confidence', 0.85)):
        return {'eligible': False, 'reason': 'Confidence below agency threshold', 'dispatch_mode': mode}

    evidence = result.get('evidence', {})
    agreeing = 0
    if abs(float(evidence.get('turbidity_difference', 0.0))) >= 25: agreeing += 1
    if float(evidence.get('audio_machine_probability', 0.0)) >= 0.70: agreeing += 1
    if float(evidence.get('vibration_machinery_probability', 0.0)) >= 0.70: agreeing += 1
    if evidence.get('persistent_activity'): agreeing += 1
    minimum_agree = int(cfg.get('minimum_agreeing_sensors', 3))
    if agreeing < minimum_agree:
        return {'eligible': False, 'reason': 'Insufficient independent evidence', 'dispatch_mode': mode, 'agreeing_signals': agreeing}

    persistence = float(evidence.get('persistence_seconds', 0.0))
    if persistence < float(cfg.get('minimum_persistence_seconds', 30.0)):
        return {'eligible': False, 'reason': 'Persistence threshold not met', 'dispatch_mode': mode, 'agreeing_signals': agreeing}

    if cfg.get('require_location', True) and not result.get('location'):
        return {'eligible': False, 'reason': 'No suspected location available', 'dispatch_mode': mode, 'agreeing_signals': agreeing}

    return {
        'eligible': True,
        'reason': 'Validated persistent CRITICAL multi-sensor event',
        'dispatch_mode': mode,
        'agreeing_signals': agreeing,
    }
