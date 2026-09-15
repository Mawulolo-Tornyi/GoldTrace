from __future__ import annotations

from copy import deepcopy
from typing import Any

from .river_topology import RiverTopology


def _center(coords: list[list[float]]) -> dict[str, float] | None:
    if not coords:
        return None
    # GeoJSON order is longitude, latitude.
    lon = sum(float(c[0]) for c in coords) / len(coords)
    lat = sum(float(c[1]) for c in coords) / len(coords)
    return {'latitude': lat, 'longitude': lon}


def _bounds(coords: list[list[float]]) -> list[list[float]]:
    if not coords:
        return []
    lons = [float(c[0]) for c in coords]
    lats = [float(c[1]) for c in coords]
    return [[min(lats), min(lons)], [max(lats), max(lons)]]


class GeospatialEngine:
    def __init__(self, topology: RiverTopology | None = None):
        self.topology = topology or RiverTopology()

    def resolve(self, zone_code: str, event_id: str | None, risk: str = 'UNKNOWN') -> dict[str, Any] | None:
        if zone_code == 'NO_SUSPECTED_ZONE':
            return None

        if zone_code == 'BETWEEN_NODE_A_AND_NODE_B':
            a = self.topology.get_node('NODE_A')
            b = self.topology.get_node('NODE_B')
            segment = self.topology.find_segment('NODE_A', 'NODE_B')
            if not a or not b or not segment:
                return None
            feature = deepcopy(segment)
            props = feature.setdefault('properties', {})
            props.update({'risk': risk, 'event_id': event_id, 'zone_code': zone_code})
            coords = feature.get('geometry', {}).get('coordinates', [])
            center = _center(coords)
            return {
                'zone_code': zone_code,
                'segment_id': props.get('segment_id'),
                'from_node': 'NODE_A',
                'to_node': 'NODE_B',
                'from_coordinates': {'latitude': a['latitude'], 'longitude': a['longitude']},
                'to_coordinates': {'latitude': b['latitude'], 'longitude': b['longitude']},
                'centroid': center,
                'river_id': a.get('river_id'),
                'river_name': a.get('river_name'),
                'district': a.get('district'),
                'region': a.get('region'),
                'geojson': feature,
                'bounds': _bounds(coords),
                'affected_nodes': ['NODE_A', 'NODE_B'],
            }

        if zone_code == 'NODE_A_LOCAL_ANOMALY':
            a = self.topology.get_node('NODE_A')
            if not a:
                return None
            feature = {
                'type': 'Feature',
                'properties': {'event_id': event_id, 'risk': risk, 'zone_code': zone_code, 'node_id': 'NODE_A'},
                'geometry': {'type': 'Point', 'coordinates': [a['longitude'], a['latitude']]},
            }
            return {
                'zone_code': zone_code,
                'segment_id': None,
                'from_node': 'NODE_A',
                'to_node': None,
                'centroid': {'latitude': a['latitude'], 'longitude': a['longitude']},
                'river_id': a.get('river_id'),
                'river_name': a.get('river_name'),
                'district': a.get('district'),
                'region': a.get('region'),
                'geojson': feature,
                'bounds': [[a['latitude'], a['longitude']], [a['latitude'], a['longitude']]],
                'affected_nodes': ['NODE_A'],
            }

        if zone_code == 'UPSTREAM_OF_NODE_A_OR_WIDESPREAD_EVENT':
            a = self.topology.get_node('NODE_A')
            if not a:
                return None
            feature = {
                'type': 'Feature',
                'properties': {'event_id': event_id, 'risk': risk, 'zone_code': zone_code, 'node_id': 'NODE_A'},
                'geometry': {'type': 'Point', 'coordinates': [a['longitude'], a['latitude']]},
            }
            return {
                'zone_code': zone_code,
                'segment_id': None,
                'from_node': None,
                'to_node': 'NODE_A',
                'centroid': {'latitude': a['latitude'], 'longitude': a['longitude']},
                'river_id': a.get('river_id'),
                'river_name': a.get('river_name'),
                'district': a.get('district'),
                'region': a.get('region'),
                'geojson': feature,
                'bounds': [[a['latitude'], a['longitude']], [a['latitude'], a['longitude']]],
                'affected_nodes': ['NODE_A', 'NODE_B'],
            }

        return None

    def map_payload(self, result: dict[str, Any]) -> dict[str, Any]:
        loc = result.get('location')
        if not loc:
            return {'event_id': result.get('event_id'), 'map': None}
        return {
            'event_id': result.get('event_id'),
            'map': {
                'center': [loc['centroid']['latitude'], loc['centroid']['longitude']],
                'zoom': 15,
                'affected_nodes': loc.get('affected_nodes', []),
                'suspected_segment': {
                    'segment_id': loc.get('segment_id'),
                    'risk': result.get('risk_level'),
                    'geometry': loc.get('geojson', {}).get('geometry'),
                    'geojson': loc.get('geojson'),
                },
                'bounds': loc.get('bounds', []),
            },
        }
