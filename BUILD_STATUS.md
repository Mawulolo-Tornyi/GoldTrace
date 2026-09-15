# GoldTrace Build Status

This package implements the GoldTrace ML, localization, geospatial mapping, controlled agency-alerting, database, API and Raspberry Pi integration architecture described in the supplied master specification.

## Validation completed in the build environment

- Python compile check: passed
- Automated tests: 34 passed
- Synthetic development dataset: 100,000 windows
- High-risk demo: `HIGH_RISK_MINING_ACTIVITY` / `CRITICAL`
- High-risk localization: `BETWEEN_NODE_A_AND_NODE_B` / `SEGMENT_A_B`
- Map output: GeoJSON generated
- Agency alert policy: eligible for validated high-risk demo
- Default agency dispatch: `SIMULATED` (safe DEMO mode)
- Normal river: no agency alert
- Heavy rain: no agency alert
- Vehicle-only scenario: no agency alert
- Sensor failure: `SYSTEM_UNCERTAIN`, no agency alert
- Offline delivery queue / retry: automated test coverage
- Alert deduplication: automated test coverage
- PyTorch audio/vibration checkpoints: included
- TorchScript edge exports: included and verified against PyTorch output
- scikit-learn environment/anomaly/fusion models: included

## Known build-environment limitation

ONNX export source is implemented, but the sandbox did not have the required `onnxscript`/ONNX exporter dependency and internet package installation was unavailable. Therefore this package includes verified TorchScript edge exports and the ONNX export code, but not generated ONNX binaries. On a development machine install the ONNX dependencies listed in the README and run `python -m src.export_models`.

## Important field-use limitation

All included training/evaluation data is synthetic development data. The included metrics validate software behavior only and must not be represented as real-world field accuracy. Real deployment requires synchronized labelled river, audio, vibration, weather, machinery and location data, plus approval/configuration of authorized alert recipients.
