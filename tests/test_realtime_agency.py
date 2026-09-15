from src.realtime_engine import RealtimeEngine
from src.mock_sensor_stream import scenario_packets
from src.database import Database


def test_critical_event_localizes_and_creates_demo_dispatch(tmp_path):
    e=RealtimeEngine(database=Database(tmp_path/'db.sqlite'))
    a,b=scenario_packets('high_risk_mining',seed=42)
    r=e.process_pair(a,b,42)
    assert r['risk_level']=='CRITICAL'
    assert r['suspected_zone']=='BETWEEN_NODE_A_AND_NODE_B'
    assert r['location']['segment_id']=='SEGMENT_A_B'
    assert r['map']['suspected_segment']['geometry']['type']=='LineString'
    assert r['agency_alert']['eligible'] is True
    assert r['agency_alert']['dispatch_status']=='SIMULATED'


def test_rain_and_vehicle_do_not_dispatch_agency_alerts(tmp_path):
    e=RealtimeEngine(database=Database(tmp_path/'db.sqlite'))
    for scenario in ('heavy_rain','vehicle'):
        a,b=scenario_packets(scenario,seed=42)
        r=e.process_pair(a,b,8)
        assert r['agency_alert']['eligible'] is False
