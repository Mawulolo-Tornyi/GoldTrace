#include <Arduino.h>

#include <Wire.h>

#include <Adafruit_ADS1X15.h>

#include "config.h"
#include "turbidity_sensor.h"


static Adafruit_ADS1115 turbidity_adc;


static bool turbidity_ready =
    false;


// ============================================================
// INITIALIZATION
// ============================================================

bool initializeTurbiditySensor()
{
    Serial.println(
        "Initializing turbidity sensor..."
    );


    Wire.begin(
        PIN_I2C_SDA,
        PIN_I2C_SCL
    );


    turbidity_ready =
        turbidity_adc.begin();


    if (
        !turbidity_ready
    )
    {
        Serial.println(
            "Turbidity ADS1115: NOT DETECTED"
        );


        return false;
    }


    turbidity_adc.setGain(
        GAIN_ONE
    );


    turbidity_adc.setDataRate(
        RATE_ADS1115_860SPS
    );


    Serial.println(
        "Turbidity ADS1115: READY"
    );


    return true;
}


// ============================================================
// VOLTAGE → NTU
// ============================================================

static float voltageToNtu(
    float voltage
)
{
    /*
     * DEVELOPMENT CALIBRATION ONLY.
     *
     * We will replace this with the actual calibration curve
     * after testing the physical turbidity sensor using known
     * clean and muddy water samples.
     */

    float difference =
        TURBIDITY_CLEAR_VOLTAGE -
        voltage;


    float ntu =
        difference *
        TURBIDITY_NTU_PER_VOLT;


    if (
        ntu < 0.0f
    )
    {
        ntu =
            0.0f;
    }


    return ntu;
}


// ============================================================
// SENSOR READING
// ============================================================

TurbidityReading readTurbiditySensor()
{
    TurbidityReading reading = {
        false,
        0,
        0.0f,
        0.0f
    };


    if (
        !turbidity_ready
    )
    {
        return reading;
    }


    constexpr int sample_count =
        20;


    long raw_total =
        0;


    float voltage_total =
        0.0f;


    for (
        int index = 0;
        index < sample_count;
        index++
    )
    {
        int16_t raw =
            turbidity_adc.readADC_SingleEnded(
                0
            );


        float voltage =
            turbidity_adc.computeVolts(
                raw
            );


        raw_total +=
            raw;


        voltage_total +=
            voltage;


        delay(
            5
        );
    }


    reading.raw =
        static_cast<int16_t>(
            raw_total /
            sample_count
        );


    reading.voltage =
        voltage_total /
        sample_count;


    reading.ntu =
        voltageToNtu(
            reading.voltage
        );


    reading.healthy =
        true;


    return reading;
}
