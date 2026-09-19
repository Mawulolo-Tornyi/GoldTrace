#pragma once

#include <Arduino.h>


struct BatteryReading
{
    bool enabled;

    bool healthy;

    int16_t raw;

    float adc_voltage;

    float battery_voltage;

    float percentage;

    bool low_battery;
};


bool initializeBatterySensor();


BatteryReading readBatterySensor();
