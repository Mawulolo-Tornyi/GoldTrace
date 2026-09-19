#include <Arduino.h>

#include <Wire.h>

#include <Adafruit_ADS1X15.h>

#include <math.h>

#include "config.h"
#include "vibration_sensor.h"


static Adafruit_ADS1115 vibration_adc;


static bool vibration_ready =
    false;


// ============================================================
// SETTINGS
// ============================================================

static constexpr uint8_t
VIBRATION_ADC_CHANNEL =
    1;


static constexpr uint16_t
VIBRATION_SAMPLE_COUNT =
    128;


// ============================================================
// INITIALIZATION
// ============================================================

bool initializeVibrationSensor()
{
    Serial.println(
        "Initializing geophone / vibration sensor..."
    );


    Wire.begin(
        PIN_I2C_SDA,
        PIN_I2C_SCL
    );


    vibration_ready =
        vibration_adc.begin();


    if (
        !vibration_ready
    )
    {
        Serial.println(
            "Vibration ADS1115: NOT DETECTED"
        );


        return false;
    }


    /*
     * ADS1115 GAIN_ONE:
     *
     * Full-scale measurement range is approximately
     * +/- 4.096 V.
     *
     * The conditioned geophone output must remain
     * inside the ADC electrical limits.
     */

    vibration_adc.setGain(
        GAIN_ONE
    );


    /*
     * Use the highest ADS1115 data rate available
     * in the Adafruit library.
     */

    vibration_adc.setDataRate(
        RATE_ADS1115_860SPS
    );


    Serial.println(
        "Vibration ADS1115: READY"
    );


    return true;
}


// ============================================================
// READ GEOPHONE WINDOW
// ============================================================

VibrationReading readVibrationSensor()
{
    VibrationReading reading = {
        false,
        0.0f,
        0.0f,
        0.0f,
        0.0f,
        0.0f,
        0.0f,
        0
    };


    if (
        !vibration_ready
    )
    {
        return reading;
    }


    float samples[
        VIBRATION_SAMPLE_COUNT
    ];


    float sum =
        0.0f;


    float minimum =
        1000000.0f;


    float maximum =
        -1000000.0f;


    unsigned long started_us =
        micros();


    for (
        uint16_t index = 0;
        index < VIBRATION_SAMPLE_COUNT;
        index++
    )
    {
        int16_t raw =
            vibration_adc.readADC_SingleEnded(
                VIBRATION_ADC_CHANNEL
            );


        float voltage =
            vibration_adc.computeVolts(
                raw
            );


        samples[
            index
        ] =
            voltage;


        sum +=
            voltage;


        if (
            voltage < minimum
        )
        {
            minimum =
                voltage;
        }


        if (
            voltage > maximum
        )
        {
            maximum =
                voltage;
        }
    }


    unsigned long elapsed_us =
        micros() -
        started_us;


    if (
        elapsed_us == 0
    )
    {
        elapsed_us =
            1;
    }


    float mean =
        sum /
        VIBRATION_SAMPLE_COUNT;


    float square_sum =
        0.0f;


    float peak =
        0.0f;


    uint16_t zero_crossings =
        0;


    float previous_centered =
        0.0f;


    for (
        uint16_t index = 0;
        index < VIBRATION_SAMPLE_COUNT;
        index++
    )
    {
        /*
         * Geophone amplifier circuits commonly bias the
         * waveform above 0 V.
         *
         * Remove the DC offset before vibration analysis.
         */

        float centered =
            samples[
                index
            ] -
            mean;


        square_sum +=
            centered *
            centered;


        float magnitude =
            fabsf(
                centered
            );


        if (
            magnitude >
            peak
        )
        {
            peak =
                magnitude;
        }


        if (
            index > 0
        )
        {
            bool crossed_zero =
                (
                    previous_centered < 0.0f &&
                    centered >= 0.0f
                )
                ||
                (
                    previous_centered >= 0.0f &&
                    centered < 0.0f
                );


            if (
                crossed_zero
            )
            {
                zero_crossings++;
            }
        }


        previous_centered =
            centered;
    }


    float rms =
        sqrtf(
            square_sum /
            VIBRATION_SAMPLE_COUNT
        );


    float zero_crossing_rate =
        static_cast<float>(
            zero_crossings
        ) /
        static_cast<float>(
            VIBRATION_SAMPLE_COUNT -
            1
        );


    float sample_rate_hz =
        (
            static_cast<float>(
                VIBRATION_SAMPLE_COUNT
            )
            *
            1000000.0f
        )
        /
        static_cast<float>(
            elapsed_us
        );


    reading.healthy =
        true;


    reading.mean_voltage =
        mean;


    reading.rms =
        rms;


    reading.peak =
        peak;


    reading.peak_to_peak =
        maximum -
        minimum;


    reading.zero_crossing_rate =
        zero_crossing_rate;


    reading.sample_rate_hz =
        sample_rate_hz;


    reading.sample_count =
        VIBRATION_SAMPLE_COUNT;


    return reading;
}
