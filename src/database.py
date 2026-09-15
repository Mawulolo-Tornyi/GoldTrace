from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .config import ROOT, load_settings


def _now(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

SCHEMA="""
CREATE TABLE IF NOT EXISTS nodes(node_id TEXT PRIMARY KEY, metadata TEXT);
CREATE TABLE IF NOT EXISTS rivers(river_id TEXT PRIMARY KEY, metadata TEXT);
CREATE TABLE IF NOT EXISTS river_segments(segment_id TEXT PRIMARY KEY, payload TEXT);
CREATE TABLE IF NOT EXISTS sensor_readings(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, node_id TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS audio_results(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, node_id TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS vibration_results(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, node_id TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS environment_results(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, node_id TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS features(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, event_id TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY, payload TEXT);
CREATE TABLE IF NOT EXISTS event_locations(event_id TEXT PRIMARY KEY, payload TEXT);
CREATE TABLE IF NOT EXISTS risk_zones(id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT, risk TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, event_id TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS alert_deliveries(delivery_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT, agency_id TEXT, channel TEXT, destination TEXT, created_at TEXT, attempted_at TEXT, delivered_at TEXT, status TEXT, retry_count INTEGER DEFAULT 0, provider_response TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS agency_recipients(agency_id TEXT PRIMARY KEY, payload TEXT);
CREATE TABLE IF NOT EXISTS outbound_alert_queue(queue_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT, agency_id TEXT, channel TEXT, destination TEXT, message TEXT, location TEXT, created_at TEXT, next_retry_at TEXT, attempt_count INTEGER DEFAULT 0, status TEXT DEFAULT 'PENDING', last_error TEXT);
CREATE TABLE IF NOT EXISTS agency_dispatches(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, event_id TEXT, risk TEXT, status TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS sensor_health(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, node_id TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS model_versions(name TEXT, version TEXT, payload TEXT, PRIMARY KEY(name,version));
CREATE TABLE IF NOT EXISTS system_logs(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, level TEXT, message TEXT);
CREATE TABLE IF NOT EXISTS baselines(node_id TEXT PRIMARY KEY, payload TEXT);
"""

class Database:
    def __init__(self,path:str|Path|None=None):
        p=Path(path or load_settings()['database']['path']); self.path=p if p.is_absolute() else ROOT/p; self.path.parent.mkdir(parents=True,exist_ok=True); self.initialize()
    def connect(self):
        con=sqlite3.connect(self.path); con.row_factory=sqlite3.Row; return con
    def initialize(self):
        with self.connect() as con: con.executescript(SCHEMA)
    def save_prediction(self,result:dict):
        with self.connect() as con: con.execute('INSERT INTO predictions(ts,event_id,payload) VALUES(?,?,?)',(result.get('timestamp'),result.get('event_id'),json.dumps(result)))
        if result.get('event_id') and result.get('location'):
            self.save_event_location(result['event_id'], result['location'], result.get('risk_level','UNKNOWN'))
    def latest_prediction(self):
        with self.connect() as con: row=con.execute('SELECT payload FROM predictions ORDER BY id DESC LIMIT 1').fetchone()
        return json.loads(row['payload']) if row else None
    def list_predictions(self,limit:int=100):
        with self.connect() as con: rows=con.execute('SELECT payload FROM predictions ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
        return [json.loads(r['payload']) for r in rows]
    def get_prediction(self,event_id:str):
        with self.connect() as con: row=con.execute('SELECT payload FROM predictions WHERE event_id=? ORDER BY id DESC LIMIT 1',(event_id,)).fetchone()
        return json.loads(row['payload']) if row else None
    def save_sensor_reading(self, packet:dict):
        with self.connect() as con: con.execute('INSERT INTO sensor_readings(ts,node_id,payload) VALUES(?,?,?)',(packet.get('timestamp'),packet.get('node_id'),json.dumps(packet)))
    def save_alert(self, result:dict, message:str):
        payload={'event_id':result.get('event_id'),'risk_level':result.get('risk_level'),'message':message,'result':result,'status':'DISPATCHED'}
        with self.connect() as con:
            cur=con.execute('INSERT INTO alerts(ts,event_id,payload) VALUES(?,?,?)',(result.get('timestamp'),result.get('event_id'),json.dumps(payload)))
            return int(cur.lastrowid)
    def list_alerts(self, limit:int=100):
        with self.connect() as con: rows=con.execute('SELECT id,payload FROM alerts ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
        out=[]
        for r in rows:
            p=json.loads(r['payload']); p['alert_id']=r['id']; out.append(p)
        return out
    def get_alert(self, alert_id:int):
        with self.connect() as con: row=con.execute('SELECT id,payload FROM alerts WHERE id=?',(alert_id,)).fetchone()
        if not row: return None
        p=json.loads(row['payload']); p['alert_id']=row['id']; return p
    def acknowledge_alert(self,alert_id:int,by:str,notes:str=''):
        item=self.get_alert(alert_id)
        if not item: return None
        item['status']='ACKNOWLEDGED'; item['acknowledged_by']=by; item['acknowledged_at']=_now(); item['notes']=notes
        with self.connect() as con: con.execute('UPDATE alerts SET payload=? WHERE id=?',(json.dumps({k:v for k,v in item.items() if k!='alert_id'}),alert_id))
        return item
    def save_event_location(self,event_id:str,location:dict,risk:str):
        with self.connect() as con:
            con.execute('INSERT OR REPLACE INTO event_locations(event_id,payload) VALUES(?,?)',(event_id,json.dumps(location)))
            con.execute('INSERT INTO risk_zones(event_id,risk,payload) VALUES(?,?,?)',(event_id,risk,json.dumps(location.get('geojson'))))
    def list_event_locations(self,limit:int=200):
        with self.connect() as con: rows=con.execute('SELECT event_id,payload FROM event_locations ORDER BY rowid DESC LIMIT ?',(limit,)).fetchall()
        return [{'event_id':r['event_id'],'location':json.loads(r['payload'])} for r in rows]
    def list_risk_zones(self,limit:int=200):
        with self.connect() as con: rows=con.execute('SELECT event_id,risk,payload FROM risk_zones ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
        return [{'event_id':r['event_id'],'risk':r['risk'],'geojson':json.loads(r['payload']) if r['payload'] else None} for r in rows]
    def create_alert_delivery(self,event_id,agency_id,channel,destination,status='PENDING'):
        with self.connect() as con:
            cur=con.execute('INSERT INTO alert_deliveries(event_id,agency_id,channel,destination,created_at,status) VALUES(?,?,?,?,?,?)',(event_id,agency_id,channel,destination,_now(),status)); return int(cur.lastrowid)
    def update_alert_delivery(self,delivery_id:int,status:str,provider_response:str='',error:str|None=None):
        now=_now(); delivered=now if status=='SENT' else None
        with self.connect() as con: con.execute('UPDATE alert_deliveries SET attempted_at=?,delivered_at=?,status=?,provider_response=?,error=? WHERE delivery_id=?',(now,delivered,status,provider_response,error,delivery_id))
    def list_alert_deliveries(self,event_id:str|None=None):
        q='SELECT * FROM alert_deliveries'; params=()
        if event_id: q+=' WHERE event_id=?'; params=(event_id,)
        q+=' ORDER BY delivery_id DESC'
        with self.connect() as con: rows=con.execute(q,params).fetchall()
        return [dict(r) for r in rows]
    def enqueue_alert(self,event_id,agency_id,channel,destination,message,location):
        with self.connect() as con:
            cur=con.execute('INSERT INTO outbound_alert_queue(event_id,agency_id,channel,destination,message,location,created_at,next_retry_at,status) VALUES(?,?,?,?,?,?,?,?,?)',(event_id,agency_id,channel,destination,message,json.dumps(location),_now(),_now(),'PENDING')); return int(cur.lastrowid)
    def pending_alert_queue(self):
        with self.connect() as con: rows=con.execute("SELECT * FROM outbound_alert_queue WHERE status IN ('PENDING','RETRYING') ORDER BY queue_id").fetchall()
        return [dict(r) for r in rows]
    def update_queue_attempt(self,queue_id:int,success:bool,error:str|None=None):
        with self.connect() as con:
            con.execute('UPDATE outbound_alert_queue SET attempt_count=attempt_count+1,status=?,last_error=?,next_retry_at=? WHERE queue_id=?',('SENT' if success else 'RETRYING',error,_now(),queue_id))
    def mark_queue_exhausted(self,queue_id:int):
        with self.connect() as con: con.execute("UPDATE outbound_alert_queue SET status='FAILED' WHERE queue_id=?",(queue_id,))
    def record_agency_dispatch(self,event_id,risk,status,payload):
        with self.connect() as con: con.execute('INSERT INTO agency_dispatches(ts,event_id,risk,status,payload) VALUES(?,?,?,?,?)',(_now(),event_id,risk,status,json.dumps(payload)))
    def has_recent_agency_dispatch(self,event_id:str,risk:str)->bool:
        with self.connect() as con: row=con.execute("SELECT 1 FROM agency_dispatches WHERE event_id=? AND risk=? AND status IN ('SENT','SIMULATED','QUEUED') ORDER BY id DESC LIMIT 1",(event_id,risk)).fetchone()
        return bool(row)
    def list_agency_dispatches(self,limit:int=100):
        with self.connect() as con: rows=con.execute('SELECT * FROM agency_dispatches ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
        out=[]
        for r in rows:
            d=dict(r); d['payload']=json.loads(d['payload']) if d.get('payload') else {}; out.append(d)
        return out
