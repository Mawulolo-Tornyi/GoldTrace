#pragma once

#include <Arduino.h>


struct AudioFeatures
{
    bool healthy = false;

    float rms = 0.0f;

    float peak = 0.0f;

    float zero_crossing_rate = 0.0f;

    float sample_rate_hz = 0.0f;
};


struct VibrationFeatures
{
    bool healthy = false;

    float rms = 0.0f;

    float peak = 0.0f;

    float sample_rate_hz = 0.0f;
};


struct SensorSnapshot
{
    // --------------------------------------------------------
    // WATER / ENVIRONMENT
    // --------------------------------------------------------

    float turbidity_ntu = 0.0f;

    float turbidity_voltage = 0.0f;


    float temperature_c = 0.0f;

    bool temperature_valid = false;


    // --------------------------------------------------------
    // AUDIO
    // --------------------------------------------------------

    AudioFeatures audio;


    // --------------------------------------------------------
    // GROUND VIBRATION
    // --------------------------------------------------------

    VibrationFeatures vibration;


    // --------------------------------------------------------
    // POWER
    // --------------------------------------------------------

    float battery_percent = 0.0f;

    float battery_voltage = 0.0f;

    bool battery_valid = false;


    // --------------------------------------------------------
    // LOCATION
    // --------------------------------------------------------

    double latitude = 0.0;

    double longitude = 0.0;

    bool gps_valid = false;

    uint32_t gps_satellites = 0;

    float gps_hdop = 0.0f;


    // --------------------------------------------------------
    // HARDWARE HEALTH
    // --------------------------------------------------------

    bool ads1115_healthy = false;
};
