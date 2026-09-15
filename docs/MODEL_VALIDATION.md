# Model Validation

All packaged training/evaluation metrics are based on synthetic development data and validate only the software pipeline. They must not be quoted as real field accuracy.

The synthetic generator creates 100,000 processed windows with event/session IDs and overlapping conditions such as normal river, rain, flood turbidity, vehicles, pumps, excavators, sensor failure and mining-like multi-sensor events. Training/evaluation splits are event-aware where implemented to reduce leakage.

The final validation package also checks critical behavioral requirements: normal/rain/vehicle conditions do not generate agency dispatch, `SYSTEM_UNCERTAIN` never dispatches, a persistent multi-sensor high-risk scenario localizes to a river segment and creates a DEMO agency dispatch, failed deliveries enter a retry queue, and repeated events are deduplicated.

Before field use, collect synchronized labelled data at multiple physical locations and reserve unseen locations for final testing.
