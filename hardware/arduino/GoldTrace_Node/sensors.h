#pragma once

#include <Arduino.h>

#include "sensor_types.h"


bool initializeSensors();


SensorSnapshot readSensorSnapshot();


void pollGps(
    unsigned long duration_ms = 10
);
