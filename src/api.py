from __future__ import annotations
from collections import deque
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Any
import os
from .database import Database
from .model_manager import ModelManager
from .realtime_engine import RealtimeEngine
from .baseline_manager import BaselineManager
from .river_topology import RiverTopology
from .geospatial import GeospatialEngine
from .agency_registry import AgencyRegistry

app=FastAPI(title='GoldTrace ML + Geospatial + Agency Alert API',version='0.2.0')
db=Database(); models=ModelManager(); engine=RealtimeEngine(models=models,database=db)
topology=RiverTopology(); geo=GeospatialEngine(topology); registry=AgencyRegistry()
latest_packets:dict[str,dict]={}
alerts:deque[dict]=deque(maxlen=500)

def _require_admin(x_goldtrace_admin_key: str | None = Header(default=None)) -> None:
    expected = os.getenv('GOLDTRACE_ADMIN_API_KEY')
    if expected and x_goldtrace_admin_key != expected:
        raise HTTPException(403, 'admin authorization required')


def _redact_destination(value: str | None) -> str | None:
    if not value: return value
    text=str(value)
    if '@' in text:
        a,b=text.split('@',1); return (a[:2]+'***@'+b) if len(a)>2 else ('***@'+b)
    if len(text)>6: return text[:4]+'***'+text[-3:]
    return '***'


class PairRequest(BaseModel):
    node_a: dict[str,Any]
    node_b: dict[str,Any]
    persistence_seconds: float = 0.0

class AckRequest(BaseModel):
    acknowledged_by: str
    notes: str = ''

@app.get('/health')
def health(): return {'system':'GoldTrace','status':'healthy','models_loaded':models.status(),'database':True,'agency_mode':engine.agency_dispatcher.mode}

@app.get('/system/status')
def system_status(): return {'system':'GoldTrace','nodes_seen':sorted(latest_packets),'models':models.status(),'agency_mode':engine.agency_dispatcher.mode}

@app.get('/models')
def model_status(): return models.registry

@app.get('/model-metrics')
def model_metrics(): return {'note':'Run python -m src.evaluate to generate reports/model_evaluation.json'}

@app.get('/latest-prediction')
def latest_prediction(): return db.latest_prediction() or {}

@app.get('/events')
def events(limit:int=100): return db.list_predictions(limit)

@app.get('/events/{event_id}')
def event(event_id:str):
    item=db.get_prediction(event_id)
    if item: return item
    raise HTTPException(404,'event not found')

@app.get('/alerts')
def list_alerts(): return db.list_alerts()

@app.get('/alerts/{alert_id}')
def get_alert(alert_id:int):
    item=db.get_alert(alert_id)
    if not item: raise HTTPException(404,'alert not found')
    return item

@app.get('/alerts/{alert_id}/deliveries')
def deliveries(alert_id:int):
    item=db.get_alert(alert_id)
    if not item: raise HTTPException(404,'alert not found')
    return db.list_alert_deliveries(item.get('event_id'))

@app.post('/alerts/{alert_id}/acknowledge')
def acknowledge(alert_id:int, req:AckRequest, x_goldtrace_admin_key: str | None = Header(default=None, alias='X-GoldTrace-Admin-Key')):
    _require_admin(x_goldtrace_admin_key)
    item=db.acknowledge_alert(alert_id, req.acknowledged_by, req.notes)
    if not item: raise HTTPException(404,'alert not found')
    return item

@app.post('/alerts/{alert_id}/retry')
def retry_alert(alert_id:int, x_goldtrace_admin_key: str | None = Header(default=None, alias='X-GoldTrace-Admin-Key')):
    _require_admin(x_goldtrace_admin_key)
    if not db.get_alert(alert_id): raise HTTPException(404,'alert not found')
    return engine.agency_dispatcher.retry_queue()

@app.post('/alerts/{alert_id}/dispatch')
def dispatch_alert(alert_id:int, x_goldtrace_admin_key: str | None = Header(default=None, alias='X-GoldTrace-Admin-Key')):
    _require_admin(x_goldtrace_admin_key)
    item=db.get_alert(alert_id)
    if not item: raise HTTPException(404,'alert not found')
    result=item.get('result') or db.get_prediction(item.get('event_id'))
    if not result: raise HTTPException(404,'event result not found')
    return engine.agency_dispatcher.dispatch(result, force=True)

@app.get('/agency-recipients')
def agency_recipients(x_goldtrace_admin_key: str | None = Header(default=None, alias='X-GoldTrace-Admin-Key')):
    _require_admin(x_goldtrace_admin_key)
    out=[]
    for item in registry.list(True):
        x=dict(item)
        if 'phone' in x: x['phone']=_redact_destination(x.get('phone'))
        if 'email' in x: x['email']=_redact_destination(x.get('email'))
        if 'webhook_url' in x: x['webhook_url']='configured' if x.get('webhook_url') else None
        out.append(x)
    return out

@app.get('/agency-alert/status')
def agency_alert_status(): return {'mode':engine.agency_dispatcher.mode,'dispatches':db.list_agency_dispatches(20),'queue':db.pending_alert_queue()}

@app.get('/sensor-health')
def sensor_health():
    latest=db.latest_prediction() or {}; return {k:v.get('health') for k,v in latest.get('node_results',{}).items()}

@app.get('/nodes')
def nodes(): return topology.list_nodes()

@app.get('/risk')
def risk():
    latest=db.latest_prediction() or {}; return {'risk_level':latest.get('risk_level','UNKNOWN'),'prediction':latest.get('prediction','SYSTEM_UNCERTAIN'),'confidence':latest.get('confidence',0.0)}

@app.get('/map/nodes')
def map_nodes(): return topology.list_nodes()

@app.get('/map/rivers')
def map_rivers(): return {'type':'FeatureCollection','features':topology.list_segments()}

@app.get('/map/segments')
def map_segments(): return topology.list_segments()

@app.get('/map/events')
def map_events(): return db.list_event_locations()

@app.get('/map/risk-zones')
def risk_zones(): return db.list_risk_zones()

@app.get('/map/events/{event_id}')
def map_event(event_id:str):
    item=db.get_prediction(event_id)
    if not item: raise HTTPException(404,'event not found')
    return geo.map_payload(item)

@app.post('/predict')
def predict(req:PairRequest): return engine.process_pair(req.node_a,req.node_b,req.persistence_seconds)

@app.post('/sensor-data')
def sensor_data(packet:dict[str,Any]):
    node=str(packet.get('node_id',''))
    if node not in {'NODE_A','NODE_B'}: raise HTTPException(400,'node_id must be NODE_A or NODE_B')
    latest_packets[node]=packet
    if {'NODE_A','NODE_B'}.issubset(latest_packets): return engine.process_pair(latest_packets['NODE_A'],latest_packets['NODE_B'])
    return {'accepted':True,'waiting_for_other_node':True}

@app.post('/calibrate')
def calibrate(payload:dict[str,Any]):
    node=str(payload.get('node_id','')); records=payload.get('records',[])
    if not node or not isinstance(records,list): raise HTTPException(400,'node_id and records list required')
    return BaselineManager(node).calibrate(records)
