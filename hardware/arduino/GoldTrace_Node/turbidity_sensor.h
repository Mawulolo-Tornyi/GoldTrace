#pragma once

#include <Arduino.h>


struct TurbidityReading
{
    bool healthy;

    int16_t raw;

    float voltage;

    float ntu;
};


bool initializeTurbiditySensor();


TurbidityReading readTurbiditySensor();
