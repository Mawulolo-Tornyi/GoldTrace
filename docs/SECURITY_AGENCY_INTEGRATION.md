# Security / Environmental Agency Integration

GoldTrace can notify **configured authorized contacts** when a validated event reaches the configured dispatch policy. This is an investigation alert, not a legal finding.

The system sends a concise incident message containing event ID, risk, confidence, suspected monitored river section, approximate centroid, district/region metadata, sensor evidence, duration and an optional map link.

## Safety gates

Production dispatch requires all of the following by default:

- agency alerts enabled
- explicit production mode
- qualifying risk threshold
- minimum confidence
- minimum agreeing independent signals
- minimum persistence
- a valid location
- non-uncertain system state
- no duplicate within cooldown
- configured approved recipient(s)
- working communications channel

Competition/development should remain in `DEMO` mode.

## SIM7600

`SIM7600SMSChannel` communicates over serial AT commands. Configure the modem serial port and install `pyserial`. Network failures do not discard the incident; failed messages are queued in SQLite for retry.
