#include <Arduino.h>

#include <math.h>

#include "driver/i2s.h"

#include "config.h"
#include "audio_sensor.h"


// ============================================================
// I2S SETTINGS
// ============================================================

static constexpr i2s_port_t
MIC_I2S_PORT =
    I2S_NUM_0;


static constexpr uint16_t
MIC_WINDOW_SAMPLES =
    512;


static bool microphone_ready =
    false;


// ============================================================
// INITIALIZATION
// ============================================================

bool initializeAudioSensor()
{
    Serial.println(
        "Initializing INMP441 microphone..."
    );


    i2s_config_t i2s_config = {};


    i2s_config.mode =
        static_cast<i2s_mode_t>(
            I2S_MODE_MASTER |
            I2S_MODE_RX
        );


    i2s_config.sample_rate =
        AUDIO_SAMPLE_RATE;


    /*
     * INMP441 supplies 24-bit microphone data
     * inside a 32-bit I2S frame.
     */

    i2s_config.bits_per_sample =
        I2S_BITS_PER_SAMPLE_32BIT;


    /*
     * L/R pin on INMP441 should be connected
     * to GND for LEFT channel operation.
     */

    i2s_config.channel_format =
        I2S_CHANNEL_FMT_ONLY_LEFT;


    i2s_config.communication_format =
        I2S_COMM_FORMAT_STAND_I2S;


    i2s_config.intr_alloc_flags =
        ESP_INTR_FLAG_LEVEL1;


    i2s_config.dma_buf_count =
        8;


    i2s_config.dma_buf_len =
        256;


    i2s_config.use_apll =
        false;


    i2s_config.tx_desc_auto_clear =
        false;


    i2s_config.fixed_mclk =
        0;


    i2s_pin_config_t pin_config = {};


    pin_config.bck_io_num =
        PIN_I2S_BCLK;


    pin_config.ws_io_num =
        PIN_I2S_WS;


    pin_config.data_out_num =
        I2S_PIN_NO_CHANGE;


    pin_config.data_in_num =
        PIN_I2S_DIN;


    /*
     * Remove an existing driver if setup()
     * is called again during development.
     */

    i2s_driver_uninstall(
        MIC_I2S_PORT
    );


    esp_err_t result =
        i2s_driver_install(
            MIC_I2S_PORT,
            &i2s_config,
            0,
            nullptr
        );


    if (
        result != ESP_OK
    )
    {
        Serial.print(
            "INMP441 I2S driver install failed: "
        );


        Serial.println(
            static_cast<int>(
                result
            )
        );


        microphone_ready =
            false;


        return false;
    }


    result =
        i2s_set_pin(
            MIC_I2S_PORT,
            &pin_config
        );


    if (
        result != ESP_OK
    )
    {
        Serial.print(
            "INMP441 I2S pin setup failed: "
        );


        Serial.println(
            static_cast<int>(
                result
            )
        );


        i2s_driver_uninstall(
            MIC_I2S_PORT
        );


        microphone_ready =
            false;


        return false;
    }


    i2s_zero_dma_buffer(
        MIC_I2S_PORT
    );


    microphone_ready =
        true;


    Serial.println(
        "INMP441 microphone: READY"
    );


    Serial.print(
        "Audio sample rate: "
    );


    Serial.print(
        AUDIO_SAMPLE_RATE
    );


    Serial.println(
        " Hz"
    );


    return true;
}


// ============================================================
// RAW I2S → NORMALIZED FLOAT SAMPLES
// ============================================================

size_t readAudioSamples(
    float *output,
    size_t max_samples
)
{
    if (
        !microphone_ready ||
        output == nullptr ||
        max_samples == 0
    )
    {
        return 0;
    }


    /*
     * Avoid allocating a very large buffer.
     *
     * GoldTrace currently reads up to
     * MIC_WINDOW_SAMPLES per measurement window.
     */

    size_t requested_samples =
        max_samples;


    if (
        requested_samples >
        MIC_WINDOW_SAMPLES
    )
    {
        requested_samples =
            MIC_WINDOW_SAMPLES;
    }


    int32_t raw_samples[
        MIC_WINDOW_SAMPLES
    ];


    size_t bytes_requested =
        requested_samples *
        sizeof(
            int32_t
        );


    size_t bytes_read =
        0;


    esp_err_t result =
        i2s_read(
            MIC_I2S_PORT,
            raw_samples,
            bytes_requested,
            &bytes_read,
            pdMS_TO_TICKS(
                1000
            )
        );


    if (
        result != ESP_OK ||
        bytes_read == 0
    )
    {
        return 0;
    }


    size_t samples_read =
        bytes_read /
        sizeof(
            int32_t
        );


    for (
        size_t index = 0;
        index < samples_read;
        index++
    )
    {
        /*
         * INMP441 data is effectively 24-bit.
         *
         * Shift away the unused lower bits and
         * normalize approximately to -1.0 ... +1.0.
         */

        int32_t sample_24bit =
            raw_samples[
                index
            ] >> 8;


        float normalized =
            static_cast<float>(
                sample_24bit
            ) /
            8388608.0f;


        /*
         * Protect the rest of the processing chain
         * against unexpected values.
         */

        if (
            normalized > 1.0f
        )
        {
            normalized =
                1.0f;
        }


        if (
            normalized < -1.0f
        )
        {
            normalized =
                -1.0f;
        }


        output[
            index
        ] =
            normalized;
    }


    return samples_read;
}


// ============================================================
// AUDIO FEATURE WINDOW
// ============================================================

AudioReading readAudioSensor()
{
    AudioReading reading = {
        false,
        0.0f,
        0.0f,
        0.0f,
        0.0f,
        static_cast<float>(
            AUDIO_SAMPLE_RATE
        ),
        0,
        false
    };


    if (
        !microphone_ready
    )
    {
        return reading;
    }


    float samples[
        MIC_WINDOW_SAMPLES
    ];


    unsigned long started_us =
        micros();


    size_t sample_count =
        readAudioSamples(
            samples,
            MIC_WINDOW_SAMPLES
        );


    unsigned long elapsed_us =
        micros() -
        started_us;


    if (
        sample_count < 8
    )
    {
        Serial.println(
            "INMP441: insufficient audio samples."
        );


        return reading;
    }


    // ========================================================
    // MEAN
    // ========================================================

    double sum =
        0.0;


    for (
        size_t index = 0;
        index < sample_count;
        index++
    )
    {
        sum +=
            samples[
                index
            ];
    }


    float mean =
        static_cast<float>(
            sum /
            sample_count
        );


    // ========================================================
    // RMS / PEAK / ZERO CROSSINGS
    // ========================================================

    double square_sum =
        0.0;


    float peak =
        0.0f;


    uint32_t zero_crossings =
        0;


    bool clipping =
        false;


    float previous =
        samples[
            0
        ] -
        mean;


    for (
        size_t index = 0;
        index < sample_count;
        index++
    )
    {
        float centered =
            samples[
                index
            ] -
            mean;


        square_sum +=
            static_cast<double>(
                centered
            ) *
            static_cast<double>(
                centered
            );


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
            magnitude >= 0.98f
        )
        {
            clipping =
                true;
        }


        if (
            index > 0
        )
        {
            bool crossed_zero =
                (
                    previous < 0.0f &&
                    centered >= 0.0f
                )
                ||
                (
                    previous >= 0.0f &&
                    centered < 0.0f
                );


            if (
                crossed_zero
            )
            {
                zero_crossings++;
            }
        }


        previous =
            centered;
    }


    float rms =
        sqrtf(
            static_cast<float>(
                square_sum /
                sample_count
            )
        );


    float zcr =
        static_cast<float>(
            zero_crossings
        ) /
        static_cast<float>(
            sample_count -
            1
        );


    /*
     * We configure the peripheral for 16 kHz.
     *
     * elapsed_us is useful diagnostically, but I2S DMA
     * timing can include scheduling overhead, so the
     * configured rate remains the authoritative rate.
     */

    float measured_rate =
        static_cast<float>(
            AUDIO_SAMPLE_RATE
        );


    if (
        elapsed_us > 0
    )
    {
        float observed_rate =
            (
                static_cast<float>(
                    sample_count
                ) *
                1000000.0f
            )
            /
            static_cast<float>(
                elapsed_us
            );


        /*
         * Only accept the observed value when it is
         * reasonably close to the configured rate.
         */

        if (
            observed_rate >
                AUDIO_SAMPLE_RATE * 0.75f &&
            observed_rate <
                AUDIO_SAMPLE_RATE * 1.25f
        )
        {
            measured_rate =
                observed_rate;
        }
    }


    reading.healthy =
        true;


    reading.mean =
        mean;


    reading.rms =
        rms;


    reading.peak =
        peak;


    reading.zero_crossing_rate =
        zcr;


    reading.sample_rate_hz =
        measured_rate;


    reading.sample_count =
        static_cast<uint16_t>(
            sample_count
        );


    reading.clipping_detected =
        clipping;


    return reading;
}
