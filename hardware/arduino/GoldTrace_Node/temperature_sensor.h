#pragma once

#include <Arduino.h>


struct TemperatureReading
{
    bool healthy;

    bool connected;

    float celsius;

    float fahrenheit;

    uint8_t resolution_bits;
};


bool initializeTemperatureSensor();


TemperatureReading readTemperatureSensor();
