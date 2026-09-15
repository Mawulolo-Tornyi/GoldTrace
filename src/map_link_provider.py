from __future__ import annotations
from urllib.parse import quote


def generate_map_link(latitude: float, longitude: float, provider: str = 'openstreetmap') -> str:
    lat = float(latitude); lon = float(longitude)
    provider = provider.lower()
    if provider == 'openstreetmap':
        return f'https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=16/{lat:.6f}/{lon:.6f}'
    if provider == 'geo':
        return f'geo:{lat:.6f},{lon:.6f}?q={quote(f"{lat:.6f},{lon:.6f} GoldTrace")}'
    return f'{lat:.6f},{lon:.6f}'
