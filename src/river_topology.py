from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import yaml

from .config import ROOT, load_settings


def _load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    with p.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _load_json(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    with p.open('r', encoding='utf-8') as f:
        return json.load(f)


class RiverTopology:
    def __init__(self, nodes_file: str | Path | None = None, rivers_file: str | Path | None = None):
        settings = load_settings()
        self.nodes_file = nodes_file or settings.get('nodes', {}).get('file', 'config/nodes.example.yaml')
        self.rivers_file = rivers_file or settings.get('rivers', {}).get('file', 'config/rivers.example.geojson')
        self.nodes = {n['node_id']: n for n in _load_yaml(self.nodes_file).get('nodes', [])}
        fc = _load_json(self.rivers_file)
        self.features = fc.get('features', [])
        self.segments = {
            f.get('properties', {}).get('segment_id'): f
            for f in self.features
            if f.get('properties', {}).get('segment_id')
        }

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self.nodes.get(node_id)

    def list_nodes(self) -> list[dict[str, Any]]:
        return list(self.nodes.values())

    def list_segments(self) -> list[dict[str, Any]]:
        return self.features

    def find_segment(self, from_node: str, to_node: str) -> dict[str, Any] | None:
        for feature in self.features:
            p = feature.get('properties', {})
            if p.get('from_node') == from_node and p.get('to_node') == to_node:
                return feature
            if p.get('from_node') == to_node and p.get('to_node') == from_node:
                return feature
        return None

    def ordered_nodes(self, river_id: str) -> list[dict[str, Any]]:
        nodes = [n for n in self.nodes.values() if n.get('river_id') == river_id]
        return sorted(nodes, key=lambda n: int(n.get('position_order', 9999)))
