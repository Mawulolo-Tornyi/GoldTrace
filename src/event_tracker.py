from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import itertools

_counter=itertools.count(1)

@dataclass
class TrackedEvent:
    event_id:str
    event_start_time:datetime
    last_seen_time:datetime
    consecutive_detection_count:int=1
    maximum_risk:str='LOW'
    confidences:list[float]=field(default_factory=list)
    nodes_involved:set[str]=field(default_factory=set)
    classification_history:list[str]=field(default_factory=list)

    @property
    def duration(self)->float:
        return max(0.0,(self.last_seen_time-self.event_start_time).total_seconds())

class EventTracker:
    def __init__(self): self.active:TrackedEvent|None=None
    def update(self,prediction:str,risk:str,confidence:float,nodes:list[str],now:datetime|None=None)->dict:
        now=now or datetime.now(timezone.utc); abnormal=prediction not in {'SAFE','SYSTEM_UNCERTAIN'}
        if not abnormal:
            if self.active is None:
                return {'event_id':None,'active':False,'duration':0.0,'closed':False}
            closed=self.active
            payload={'event_id':closed.event_id,'active':False,'duration':closed.duration,'closed':True,'maximum_risk':closed.maximum_risk}
            self.active=None
            return payload
        if self.active is None:
            eid=f"GT-{now.strftime('%Y%m%d')}-{next(_counter):06d}"; self.active=TrackedEvent(eid,now,now)
        else:
            self.active.last_seen_time=now; self.active.consecutive_detection_count+=1
        rank={'LOW':0,'MEDIUM':1,'HIGH':2,'CRITICAL':3,'UNKNOWN':-1}
        if rank.get(risk,-1)>rank.get(self.active.maximum_risk,-1): self.active.maximum_risk=risk
        self.active.confidences.append(float(confidence)); self.active.nodes_involved.update(nodes); self.active.classification_history.append(prediction)
        return {'event_id':self.active.event_id,'active':True,'duration':self.active.duration,'consecutive_detection_count':self.active.consecutive_detection_count,'maximum_risk':self.active.maximum_risk,'mean_confidence':sum(self.active.confidences)/len(self.active.confidences),'nodes_involved':sorted(self.active.nodes_involved)}
