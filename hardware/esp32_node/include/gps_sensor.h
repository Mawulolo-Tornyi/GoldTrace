#pragma once

#include <Arduino.h>


struct GPSReading
{
    bool healthy;

    bool receiving_data;

    bool fix_valid;

    double latitude;

    double longitude;

    float altitude_m;

    float speed_kmh;

    float hdop;

    uint32_t satellites;

    uint32_t fix_age_ms;

    uint32_t characters_processed;
};


bool initializeGPSSensor();


void updateGPSSensor(
    unsigned long duration_ms
);


GPSReading readGPSSensor();
