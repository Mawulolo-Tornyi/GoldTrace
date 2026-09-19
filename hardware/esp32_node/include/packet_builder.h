#pragma once

#include <Arduino.h>

#include "sensor_types.h"


String buildSensorPacket(
    const SensorSnapshot &snapshot,
    uint32_t boot_id,
    uint32_t sequence_number
);
