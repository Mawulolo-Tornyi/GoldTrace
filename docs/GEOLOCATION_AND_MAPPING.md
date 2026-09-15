# Geolocation and Mapping

GoldTrace initially performs **segment localization**, not exact-machine GPS localization. Fixed monitoring-node coordinates are registered at installation. River geometry is stored as GeoJSON.

For the two-node prototype, normal upstream Node A plus abnormal downstream Node B maps to the monitored segment `SEGMENT_A_B`. `src/geospatial.py` returns segment metadata, a centroid, map bounds and GeoJSON. GeoJSON uses the required `[longitude, latitude]` order.

The frontend can consume `/map/nodes`, `/map/segments`, `/map/events`, `/map/risk-zones`, and `/map/events/{event_id}` to render nodes and highlight suspected river sections. Real deployments must replace the example coordinates and geometry with surveyed values.

Future precision improvements can add more nodes, GNSS, acoustic/vibration localization or verified imagery without changing the event-location interface.
