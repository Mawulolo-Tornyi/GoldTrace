from __future__ import annotations
from datetime import datetime, timezone
import numpy as np

SCENARIOS=["normal","rain","heavy_rain","runoff","vehicle","motorbike","boat","construction","water_pump","excavator","possible_mining","high_risk_mining","sensor_failure","communication_failure","mixed_rain_and_vehicle","mixed_rain_and_machinery"]


def _audio(sr:int,seconds:float,kind:str,rng):
    n=int(sr*seconds); t=np.arange(n)/sr; x=.02*rng.normal(size=n)
    if kind in {"vehicle","motorbike","boat","construction","water_pump","excavator","possible_mining","high_risk_mining","mixed_rain_and_vehicle","mixed_rain_and_machinery"}:
        f={"motorbike":120,"vehicle":90,"boat":70,"water_pump":55,"excavator":38}.get(kind,45)
        x += .35*np.sin(2*np.pi*f*t)+.18*np.sin(2*np.pi*2*f*t)
    if "rain" in kind: x += .15*rng.normal(size=n)
    return np.clip(x,-1,1).astype(float).tolist()


def _vibration(sr:int,seconds:float,kind:str,rng):
    n=int(sr*seconds); t=np.arange(n)/sr; x=.015*rng.normal(size=n)
    if kind in {"vehicle","motorbike","construction","water_pump","excavator","possible_mining","high_risk_mining","mixed_rain_and_vehicle","mixed_rain_and_machinery"}:
        f={"motorbike":22,"vehicle":14,"water_pump":28,"excavator":8}.get(kind,10)
        x += .5*np.sin(2*np.pi*f*t)+.15*np.sin(2*np.pi*3*f*t)
    return x.astype(float).tolist()


def scenario_packets(scenario:str="normal",seed:int=42,timestamp:datetime|None=None)->tuple[dict,dict]:
    if scenario not in SCENARIOS: raise ValueError(f"unknown scenario {scenario}")
    rng=np.random.default_rng(seed); now=timestamp or datetime.now(timezone.utc); iso=now.isoformat().replace("+00:00","Z")
    a_t=18+rng.normal(0,2); b_t=a_t+rng.normal(1,2)
    if scenario in {"rain","runoff"}: b_t+=30
    if scenario=="heavy_rain": a_t+=35; b_t+=55
    if scenario in {"possible_mining"}: b_t+=45
    if scenario in {"high_risk_mining","excavator"}: b_t+=75 if scenario=="high_risk_mining" else 18
    if scenario=="mixed_rain_and_vehicle": a_t+=25; b_t+=45
    if scenario=="mixed_rain_and_machinery": a_t+=25; b_t+=65
    packet_common={"timestamp":iso,"water_temperature_c":26.2,"audio_sample_rate":16000,"vibration_sample_rate":1000,"battery_voltage":12.4,"lora_rssi":-78,"lora_snr":7.0}
    a={**packet_common,"node_id":"NODE_A","turbidity_raw":1800,"turbidity_ntu":max(0,float(a_t)),"audio_samples":_audio(16000,2,"normal",rng),"vibration_samples":_vibration(1000,2,"normal",rng)}
    b_kind=scenario
    b={**packet_common,"node_id":"NODE_B","turbidity_raw":2500,"turbidity_ntu":max(0,float(b_t)),"audio_samples":_audio(16000,2,b_kind,rng),"vibration_samples":_vibration(1000,2,b_kind,rng)}
    if scenario=="sensor_failure": b["turbidity_ntu"]=None; b["audio_samples"]=[]
    if scenario=="communication_failure": b["timestamp"]="2020-01-01T00:00:00Z"
    return a,b
