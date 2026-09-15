# Alerting Architecture

GoldTrace separates **detection**, **risk assessment**, **alert eligibility**, and **delivery**. This prevents a single noisy sensor or one ML probability from immediately contacting an external recipient.

Flow: `risk engine -> event persistence -> localization -> alert policy -> dispatcher -> channel -> delivery record / retry queue`.

Default deployment is `DEMO`, so no real message leaves the computer. `SYSTEM_UNCERTAIN` is never eligible. A normal CRITICAL policy requires sufficient confidence, multiple agreeing sensor signals, persistence, a known suspected location, and deduplication/cooldown approval.

Delivery channels are isolated behind a common notification interface. The package provides mock SMS, SIM7600 SMS, HTTP webhook and optional email implementations. Failed deliveries are placed in SQLite `outbound_alert_queue` and can be retried. Delivery records distinguish `PENDING`, `SENT`, `FAILED`, `RETRYING`, and acknowledged alert state.

Production contacts must be approved and configured by the deployment operator. Do not populate public source code with arbitrary government or emergency phone numbers.
