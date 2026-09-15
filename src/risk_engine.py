from __future__ import annotations
from .config import load_settings

CLASS_RISK={"SAFE":"LOW","SUSPICIOUS_ENVIRONMENTAL_CHANGE":"MEDIUM","MACHINERY_ACTIVITY":"MEDIUM","POSSIBLE_MINING_ACTIVITY":"HIGH","HIGH_RISK_MINING_ACTIVITY":"CRITICAL","SYSTEM_UNCERTAIN":"UNKNOWN"}


def assess_risk(fusion_class:str, confidence:float, features:dict, sensor_health:list[str])->dict:
    cfg=load_settings()["risk"]
    if not sensor_health or sum(h in {"HEALTHY","DEGRADED"} for h in sensor_health)/len(sensor_health) < (1-float(cfg["uncertain_sensor_fraction"])):
        return {"prediction":"SYSTEM_UNCERTAIN","risk_level":"UNKNOWN","reasons":["Insufficient healthy sensor coverage"]}
    t=float(features.get("turbidity_difference",0)); a=float(features.get("audio_machine_probability_b",0)); v=float(features.get("vibration_machinery_probability_b",0)); p=float(features.get("persistence_seconds",0)); reasons=[]
    pred=fusion_class; risk=CLASS_RISK.get(pred,"UNKNOWN")
    if t>=cfg["turbidity_difference_critical"] and a>=cfg["machine_probability_high"] and v>=cfg["vibration_probability_high"] and p>=cfg["critical_persistence_seconds"] and confidence>=cfg["confidence_minimum"]:
        pred="HIGH_RISK_MINING_ACTIVITY"; risk="CRITICAL"; reasons += ["Strong downstream turbidity increase","Machine-like acoustic signature","Heavy machinery vibration","Abnormal conditions persisted","Multiple sensors agree"]
    elif (a>=cfg["machine_probability_high"] or v>=cfg["vibration_probability_high"]) and t<cfg["turbidity_difference_high"]:
        pred="MACHINERY_ACTIVITY"; risk="MEDIUM"; reasons += ["Machinery signature detected","River disturbance evidence is limited"]
    elif (t>=cfg["turbidity_difference_high"] or max(float(features.get("turbidity_a",0) or 0), float(features.get("turbidity_b",0) or 0)) >= 50.0) and a<cfg["machine_probability_high"] and v<cfg["vibration_probability_high"]:
        pred="SUSPICIOUS_ENVIRONMENTAL_CHANGE"; risk="MEDIUM"; reasons += ["River turbidity is elevated without matching machinery signatures"]
    if not reasons: reasons=[f"Fusion model supports {pred}"]
    return {"prediction":pred,"risk_level":risk,"reasons":reasons}
