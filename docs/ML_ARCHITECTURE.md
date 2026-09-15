# GoldTrace ML Architecture

GoldTrace is a hybrid multi-model system. It intentionally avoids a single rule such as “muddy water = galamsey.”

1. Sensor validation checks packet freshness, missing/corrupt buffers and plausible ranges.
2. Audio processing extracts spectral/energy features. A compact PyTorch CNN candidate is also trained on development waveforms.
3. Vibration processing extracts time/frequency features. A compact PyTorch 1D CNN candidate is also trained.
4. Environmental ML models turbidity/temperature and upstream/downstream change.
5. IsolationForest provides an anomaly score but cannot independently trigger a CRITICAL alert.
6. Node-comparison features combine turbidity, machine probability, vibration probability and persistence.
7. A fusion classifier predicts SAFE, environmental change, machinery activity, possible mining, or high-risk mining activity.
8. The confidence and rule-based risk engine require corroborating evidence before escalation.
9. Localization maps the event to a monitored river segment.
10. The alert policy separately determines whether the event is safe to dispatch externally.

PyTorch is used where deep learning can add pattern-recognition value; scikit-learn remains appropriate for the tabular environmental/anomaly/fusion layers. Computationally expensive training belongs on a workstation; the Raspberry Pi performs inference.
