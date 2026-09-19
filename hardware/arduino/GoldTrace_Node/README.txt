GOLDTRACE ESP32 SENSOR NODE
===========================

This directory contains the Arduino IDE version of the
GoldTrace ESP32-S3 sensor-node firmware.

The same firmware is used for NODE_A and NODE_B.


NODE_A
------

Role:

    Upstream river monitoring node

Set in node_identity.h:

    #define GOLDTRACE_NODE_NUMBER 1


NODE_B
------

Role:

    Downstream river monitoring node

Set in node_identity.h:

    #define GOLDTRACE_NODE_NUMBER 2


MAIN PROGRAM
------------

Open:

    GoldTrace_Node.ino


FIRMWARE FLOW
-------------

ESP32 startup
    |
    +-- Initialize turbidity sensor
    |
    +-- Initialize geophone / vibration
    |
    +-- Initialize INMP441 microphone
    |
    +-- Initialize DS18B20
    |
    +-- Initialize GPS
    |
    +-- Initialize battery monitor
    |
    +-- Initialize LoRa
    |
    v

Read sensors
    |
    v

Create SensorSnapshot
    |
    v

Build compact JSON telemetry
    |
    v

HMAC-SHA256 authenticate packet
    |
    v

Transmit through RFM95 / SX1276
    |
    v

Raspberry Pi gateway


IMPORTANT FIELD NOTES
---------------------

1. The turbidity calibration values are temporary.

2. Battery monitoring remains disabled until the final
   battery and resistor divider are known.

3. The LoRa frequency in config.h is a development
   placeholder and must be verified before field use.

4. GPS is optional for normal fixed-node operation.

5. Do not send raw continuous microphone or vibration
   streams over LoRa.

6. A LoRa antenna must be attached before transmitting.

7. Never commit secrets.h to GitHub.
