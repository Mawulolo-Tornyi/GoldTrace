#pragma once

#include <Arduino.h>


struct AudioReading
{
    bool healthy;

    float mean;

    float rms;

    float peak;

    float zero_crossing_rate;

    float sample_rate_hz;

    uint16_t sample_count;

    bool clipping_detected;
};


bool initializeAudioSensor();


size_t readAudioSamples(
    float *output,
    size_t max_samples
);


AudioReading readAudioSensor();
