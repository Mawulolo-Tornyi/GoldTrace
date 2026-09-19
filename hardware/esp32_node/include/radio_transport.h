#pragma once

#include <Arduino.h>


bool initializeLoRa();


bool transmitLoRaPacket(
    const String &packet
);


bool isLoRaReady();


int16_t getLastLoRaStatus();
