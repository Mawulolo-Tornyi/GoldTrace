from src.river_topology import RiverTopology

def test_node_order_and_segment():
    t=RiverTopology()
    assert t.get_node('NODE_A')['position_type']=='UPSTREAM'
    assert t.get_node('NODE_B')['position_type']=='DOWNSTREAM'
    assert t.find_segment('NODE_A','NODE_B')['properties']['segment_id']=='SEGMENT_A_B'
