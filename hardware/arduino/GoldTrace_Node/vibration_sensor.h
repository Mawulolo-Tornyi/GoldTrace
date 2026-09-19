#pragma once

#include <Arduino.h>


struct VibrationReading
{
    bool healthy;

    float mean_voltage;

    float rms;

    float peak;

    float peak_to_peak;

    float zero_crossing_rate;

    float sample_rate_hz;

    uint16_t sample_count;
};


bool initializeVibrationSensor();


VibrationReading readVibrationSensor();
