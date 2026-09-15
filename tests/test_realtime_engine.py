from src.realtime_engine import RealtimeEngine
from src.mock_sensor_stream import scenario_packets
from src.model_manager import ModelManager
from src.database import Database

def test_sensor_failure_uncertain(tmp_path):
    e=RealtimeEngine(database=Database(tmp_path/"db.sqlite")); a,b=scenario_packets("sensor_failure"); r=e.process_pair(a,b,30); assert r["prediction"]=="SYSTEM_UNCERTAIN"
def test_high_risk_not_safe(tmp_path):
    e=RealtimeEngine(database=Database(tmp_path/"db.sqlite")); a,b=scenario_packets("high_risk_mining"); r=e.process_pair(a,b,42); assert r["risk_level"] in {"HIGH","CRITICAL"}
