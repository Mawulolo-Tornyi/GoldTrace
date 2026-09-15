# GoldTrace ML System

**GoldTrace — Smart River-Based Illegal Mining Detection, Localization and Security Alert System**

> Detect the activity. Trace the source. Locate the area. Alert the authorities. Protect the river.

GoldTrace is a Raspberry-Pi-oriented environmental intelligence system for detecting **suspected** mining/galamsey activity from multiple independent signals. It combines river turbidity, machinery audio, ground vibration, temperature, upstream/downstream comparison, anomaly detection, temporal persistence, geospatial localization, and a controlled agency-alerting workflow.

## Important interpretation

GoldTrace is an **early-warning and investigation-support system**. It does not legally confirm illegal mining. A `CRITICAL` result means that multiple sensor channels jointly resemble a high-risk mining event and the monitored river section should be investigated.

The development package includes synthetic data so the software can be built and tested before field recordings exist. **Synthetic metrics are not evidence of real-world accuracy.** Retrain and independently validate with synchronized real river, audio, vibration, weather, machinery, and location data before field deployment.

## Architecture

```text
Node A sensors -> ESP32-S3 -> LoRa --\
                                     Raspberry Pi 5
Node B sensors -> ESP32-S3 -> LoRa --/     |
                                           +-> packet/sensor validation
                                           +-> signal preprocessing
                                           +-> audio ML / PyTorch CNN candidate
                                           +-> vibration ML / PyTorch CNN candidate
                                           +-> environmental ML
                                           +-> IsolationForest anomaly detection
                                           +-> sensor fusion classifier
                                           +-> confidence + risk engine
                                           +-> event persistence
                                           +-> river-segment localization
                                           +-> GeoJSON/map payload
                                           +-> SQLite
                                           +-> FastAPI
                                           +-> alert policy
                                           +-> SIM7600 / webhook / email channel
                                           +-> authorized agencies (production only)
```

## Current development build

- 100,000-window synthetic development dataset
- Audio feature model: scikit-learn ExtraTrees
- Audio deep-learning candidate: compact PyTorch 2D CNN
- Vibration feature model: scikit-learn ExtraTrees
- Vibration deep-learning candidate: compact PyTorch 1D CNN
- Environmental model: scikit-learn candidate comparison
- Anomaly model: IsolationForest
- Fusion model: scikit-learn candidate comparison with high-risk recall / false-positive-aware selection
- Event tracking and persistence
- Upstream/downstream localization
- GeoJSON river segment output for frontend maps
- SQLite event, risk-zone, alert, delivery and outbound-queue storage
- FastAPI map, event, alert and agency endpoints
- SIM7600 production SMS adapter using AT commands
- Mock SMS mode for safe development/competition demonstrations
- Offline alert queue, retry and deduplication
- 31 automated tests in the packaged build

The included example node coordinates and river geometry are placeholders for development. Replace them with surveyed deployment locations before field use.

## Safe alerting modes

`config/settings.yaml` ships with:

```yaml
agency_alerts:
  enabled: true
  production_mode: false
  dispatch_mode: DEMO
```

`DEMO` generates and records alerts but never sends a real SMS/webhook. Real external dispatch requires an administrator to intentionally enable production mode, configure approved recipients, and connect a working SIM7600/network channel.

A CRITICAL agency alert is eligible only when configured requirements are satisfied, including confidence, persistence, multi-sensor agreement, valid location, sensor health, deduplication and cooldown checks. `SYSTEM_UNCERTAIN` never triggers an automatic agency alert.

## Location and map output

For the initial two-node topology:

- Node A normal + Node B abnormal -> `BETWEEN_NODE_A_AND_NODE_B`
- Node A abnormal + Node B abnormal -> `UPSTREAM_OF_NODE_A_OR_WIDESPREAD_EVENT`
- Node A abnormal + Node B normal -> `NODE_A_LOCAL_ANOMALY`
- both normal -> `NO_SUSPECTED_ZONE`

When a segment is suspected, GoldTrace returns node coordinates, river segment ID, centroid, bounds and GeoJSON. The future React/Leaflet frontend can highlight that exact monitored river segment. GoldTrace does **not** claim exact excavator coordinates unless future localization hardware supports that precision.

## Quick start

```bash
python -m venv venv
# Linux/Raspberry Pi
source venv/bin/activate
# Windows PowerShell
# .\venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
python -m src.data_generator --samples 100000
python -m src.train_all
python -m src.evaluate
python -m src.export_models
pytest -q
python main.py --mode demo --scenario high_risk_mining
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

The packaged build already contains trained **synthetic-development** candidate models and the generated dataset. Retraining is optional for inspecting the demo, but mandatory once real field data is collected.

## Main API endpoints

```text
GET  /health
GET  /system/status
GET  /latest-prediction
GET  /events
GET  /events/{event_id}
GET  /alerts
GET  /alerts/{alert_id}
GET  /alerts/{alert_id}/deliveries
GET  /nodes
GET  /sensor-health
GET  /risk
GET  /map/nodes
GET  /map/rivers
GET  /map/segments
GET  /map/events
GET  /map/risk-zones
GET  /map/events/{event_id}
GET  /agency-recipients
GET  /agency-alert/status
POST /predict
POST /sensor-data
POST /calibrate
POST /alerts/{alert_id}/acknowledge
POST /alerts/{alert_id}/retry
POST /alerts/{alert_id}/dispatch
```

## Node and agency configuration

Development examples live in:

- `config/nodes.example.yaml`
- `config/rivers.example.geojson`
- `config/agencies.example.yaml`

Do not commit real passwords, API secrets or sensitive operational credentials. Recipient phone numbers can be supplied through environment variables such as `GOLDTRACE_AGENCY_001_PHONE`.

## SIM7600

The production adapter is `src/notifications/sim7600_sms.py`. It checks AT response, SIM state, network registration, enables text SMS mode, sends the message, parses the modem response, and reports success/failure. Install `pyserial` on the Raspberry Pi and set the correct `/dev/ttyUSB*` modem port in configuration.

## Edge models

The package includes PyTorch checkpoints and verified TorchScript exports for audio/vibration. The source also supports ONNX export. In this build environment ONNX export could not be completed because the required ONNX exporter dependency was unavailable to install; `reports/onnx_export.json` records that limitation. On a normal development machine, install `onnx`, `onnxscript`, and `onnxruntime`, then run:

```bash
python -m src.export_models
```

The runtime automatically falls back to the scikit-learn audio/vibration models when an ONNX model is not present.

## Key reports

- `reports/model_evaluation.json`
- `reports/audio_training.json`
- `reports/vibration_training.json`
- `reports/environment_training.json`
- `reports/fusion_training.json`
- `reports/onnx_export.json`
- `reports/edge_benchmark.json`
- `reports/scenario_validation.json`
- `reports/validation_summary.json`

## Documentation

See `docs/` for ML architecture, mapping/localization, security-agency integration, alerting architecture, real-data collection, validation and Raspberry Pi deployment.
