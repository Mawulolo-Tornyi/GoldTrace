#include <Arduino.h>

#include <Wire.h>

#include <Adafruit_ADS1X15.h>

#include <math.h>

#include "config.h"
#include "battery_sensor.h"


// ============================================================
// BATTERY ADC
// ============================================================

static Adafruit_ADS1115 battery_adc;


static bool battery_ready =
    false;


static constexpr uint8_t
BATTERY_ADC_CHANNEL =
    2;


static constexpr uint16_t
BATTERY_SAMPLE_COUNT =
    20;


// ============================================================
// HELPERS
// ============================================================

static float clampValue(
    float value,
    float minimum,
    float maximum
)
{
    if (
        value < minimum
    )
    {
        return minimum;
    }


    if (
        value > maximum
    )
    {
        return maximum;
    }


    return value;
}


static float voltageToPercentage(
    float voltage
)
{
    float range =
        BATTERY_FULL_V -
        BATTERY_EMPTY_V;


    if (
        range <= 0.0f
    )
    {
        return 0.0f;
    }


    float percentage =
        (
            (
                voltage -
                BATTERY_EMPTY_V
            )
            /
            range
        )
        *
        100.0f;


    return clampValue(
        percentage,
        0.0f,
        100.0f
    );
}


// ============================================================
// INITIALIZATION
// ============================================================

bool initializeBatterySensor()
{
#if ENABLE_BATTERY_MONITOR

    Serial.println(
        "Initializing battery monitor..."
    );


    Wire.begin(
        PIN_I2C_SDA,
        PIN_I2C_SCL
    );


    battery_ready =
        battery_adc.begin();


    if (
        !battery_ready
    )
    {
        Serial.println(
            "Battery ADS1115: NOT DETECTED"
        );


        return false;
    }


    battery_adc.setGain(
        GAIN_ONE
    );


    battery_adc.setDataRate(
        RATE_ADS1115_860SPS
    );


    if (
        BATTERY_DIVIDER_RATIO <= 0.0f
    )
    {
        Serial.println(
            "Battery divider ratio is invalid."
        );


        battery_ready =
            false;


        return false;
    }


    Serial.println(
        "Battery monitor: READY"
    );


    Serial.print(
        "Divider ratio: "
    );


    Serial.println(
        BATTERY_DIVIDER_RATIO,
        3
    );


    return true;

#else

    Serial.println(
        "Battery monitor: DISABLED IN CONFIG"
    );


    battery_ready =
        false;


    return false;

#endif
}


// ============================================================
// BATTERY READING
// ============================================================

BatteryReading readBatterySensor()
{
    BatteryReading reading = {
#if ENABLE_BATTERY_MONITOR
        true,
#else
        false,
#endif
        false,
        0,
        0.0f,
        0.0f,
        0.0f,
        false
    };


#if !ENABLE_BATTERY_MONITOR

    return reading;

#else

    if (
        !battery_ready
    )
    {
        return reading;
    }


    long raw_total =
        0;


    float adc_voltage_total =
        0.0f;


    for (
        uint16_t index = 0;
        index < BATTERY_SAMPLE_COUNT;
        index++
    )
    {
        int16_t raw =
            battery_adc.readADC_SingleEnded(
                BATTERY_ADC_CHANNEL
            );


        float adc_voltage =
            battery_adc.computeVolts(
                raw
            );


        raw_total +=
            raw;


        adc_voltage_total +=
            adc_voltage;


        delay(
            5
        );
    }


    float adc_voltage =
        adc_voltage_total /
        BATTERY_SAMPLE_COUNT;


    float battery_voltage =
        adc_voltage *
        BATTERY_DIVIDER_RATIO;


    /*
     * Reject obviously invalid values.
     */

    if (
        !isfinite(
            battery_voltage
        )
        ||
        battery_voltage < 0.0f
    )
    {
        return reading;
    }


    float percentage =
        voltageToPercentage(
            battery_voltage
        );


    reading.healthy =
        true;


    reading.raw =
        static_cast<int16_t>(
            raw_total /
            BATTERY_SAMPLE_COUNT
        );


    reading.adc_voltage =
        adc_voltage;


    reading.battery_voltage =
        battery_voltage;


    reading.percentage =
        percentage;


    reading.low_battery =
        battery_voltage <=
        BATTERY_EMPTY_V;


    return reading;

#endif
}
