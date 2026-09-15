from fastapi.testclient import TestClient
from src.api import app


def test_map_nodes_and_segments_available():
    c=TestClient(app)
    nodes=c.get('/map/nodes'); seg=c.get('/map/segments')
    assert nodes.status_code==200 and len(nodes.json())>=2
    assert seg.status_code==200 and seg.json()[0]['properties']['segment_id']=='SEGMENT_A_B'
