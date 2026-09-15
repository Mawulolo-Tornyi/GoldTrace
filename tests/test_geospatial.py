from src.geospatial import GeospatialEngine

def test_between_nodes_returns_segment_and_geojson():
    loc=GeospatialEngine().resolve('BETWEEN_NODE_A_AND_NODE_B','GT-TEST','CRITICAL')
    assert loc['segment_id']=='SEGMENT_A_B'
    assert loc['centroid']['latitude']
    assert loc['geojson']['geometry']['type']=='LineString'
    first=loc['geojson']['geometry']['coordinates'][0]
    assert first[0] < 0 and first[1] > 0  # GeoJSON lon,lat order
