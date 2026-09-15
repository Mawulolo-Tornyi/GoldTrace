from __future__ import annotations
from datetime import datetime, timezone
from .config import load_settings

RANK={"LOW":0,"MEDIUM":1,"HIGH":2,"CRITICAL":3,"UNKNOWN":-1}

class AlertManager:
    def __init__(self): self.last_sent:dict[str,datetime]={}
    def should_alert(self,event_id:str|None,risk:str)->bool:
        if not event_id: return False
        minimum=load_settings()["alerts"]["minimum_risk"]
        if RANK.get(risk,-1)<RANK.get(minimum,2): return False
        now=datetime.now(timezone.utc); cooldown=float(load_settings()["alerts"]["cooldown_seconds"]); last=self.last_sent.get(event_id)
        if last and (now-last).total_seconds()<cooldown: return False
        self.last_sent[event_id]=now; return True
    def format_alert(self,result:dict)->str:
        e=result.get("evidence",{})
        return f"GOLDTRACE ALERT\nRisk: {result.get('risk_level')}\nZone: {result.get('suspected_zone')}\nTurbidity change: {e.get('turbidity_difference',0):+.1f} NTU\nMachine audio: {100*e.get('audio_machine_probability',0):.0f}%\nHeavy vibration: {100*e.get('vibration_machinery_probability',0):.0f}%"
