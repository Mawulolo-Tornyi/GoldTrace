#include <Arduino.h>

#include "esp_system.h"

#include "config.h"
#include "sensor_types.h"
#include "sensors.h"
#include "packet_builder.h"
#include "radio_transport.h"


// ============================================================
// GOLDTRACE NODE STATE
// ============================================================

static uint32_t boot_id =
    0;


static uint32_t sequence_number =
    0;


static unsigned long last_transmission_ms =
    0;


static unsigned long last_lora_retry_ms =
    0;


static bool sensor_system_ready =
    false;


static bool lora_ready =
    false;


static uint32_t successful_transmissions =
    0;


static uint32_t failed_transmissions =
    0;


static uint32_t packet_build_failures =
    0;


// ============================================================
// TIMING
// ============================================================

static constexpr unsigned long
LORA_RETRY_INTERVAL_MS =
    10000;


// ============================================================
// STARTUP BANNER
// ============================================================

static void printStartupBanner()
{
    Serial.println();
    Serial.println();
    Serial.println(
        "=============================================="
    );

    Serial.println(
        "                 GOLDTRACE"
    );

    Serial.println(
        " Smart River Mining Activity Detection Node"
    );

    Serial.println(
        "=============================================="
    );


    Serial.print(
        "Node ID: "
    );

    Serial.println(
        NODE_ID
    );


    Serial.print(
        "Boot ID: "
    );

    Serial.println(
        boot_id
    );


    Serial.print(
        "Firmware protocol: "
    );

    Serial.println(
        GOLDTRACE_PROTOCOL_VERSION
    );


    Serial.println(
        "=============================================="
    );

    Serial.println();
}


// ============================================================
// SENSOR SUMMARY
// ============================================================

static void printSensorSummary(
    const SensorSnapshot &snapshot
)
{
    Serial.println();
    Serial.println(
        "--------------- SENSOR DATA ----------------"
    );


    // --------------------------------------------------------
    // NODE
    // --------------------------------------------------------

    Serial.print(
        "Node: "
    );

    Serial.println(
        NODE_ID
    );


    // --------------------------------------------------------
    // TURBIDITY
    // --------------------------------------------------------

    Serial.print(
        "Turbidity: "
    );

    Serial.print(
        snapshot.turbidity_ntu,
        2
    );

    Serial.println(
        " NTU"
    );


    Serial.print(
        "Turbidity voltage: "
    );

    Serial.print(
        snapshot.turbidity_voltage,
        4
    );

    Serial.println(
        " V"
    );


    // --------------------------------------------------------
    // WATER TEMPERATURE
    // --------------------------------------------------------

    Serial.print(
        "Water temperature: "
    );


    if (
        snapshot.temperature_valid
    )
    {
        Serial.print(
            snapshot.temperature_c,
            2
        );

        Serial.println(
            " C"
        );
    }
    else
    {
        Serial.println(
            "NOT AVAILABLE"
        );
    }


    // --------------------------------------------------------
    // AUDIO
    // --------------------------------------------------------

    Serial.print(
        "Audio status: "
    );

    Serial.println(
        snapshot.audio.healthy
            ? "HEALTHY"
            : "FAILED"
    );


    if (
        snapshot.audio.healthy
    )
    {
        Serial.print(
            "Audio RMS: "
        );

        Serial.println(
            snapshot.audio.rms,
            6
        );


        Serial.print(
            "Audio peak: "
        );

        Serial.println(
            snapshot.audio.peak,
            6
        );


        Serial.print(
            "Audio ZCR: "
        );

        Serial.println(
            snapshot.audio.zero_crossing_rate,
            6
        );
    }


    // --------------------------------------------------------
    // VIBRATION
    // --------------------------------------------------------

    Serial.print(
        "Vibration status: "
    );

    Serial.println(
        snapshot.vibration.healthy
            ? "HEALTHY"
            : "FAILED"
    );


    if (
        snapshot.vibration.healthy
    )
    {
        Serial.print(
            "Vibration RMS: "
        );

        Serial.println(
            snapshot.vibration.rms,
            6
        );


        Serial.print(
            "Vibration peak: "
        );

        Serial.println(
            snapshot.vibration.peak,
            6
        );
    }


    // --------------------------------------------------------
    // GPS
    // --------------------------------------------------------

    Serial.print(
        "GPS fix: "
    );

    Serial.println(
        snapshot.gps_valid
            ? "VALID"
            : "NO FIX"
    );


    if (
        snapshot.gps_valid
    )
    {
        Serial.print(
            "Latitude: "
        );

        Serial.println(
            snapshot.latitude,
            6
        );


        Serial.print(
            "Longitude: "
        );

        Serial.println(
            snapshot.longitude,
            6
        );


        Serial.print(
            "Satellites: "
        );

        Serial.println(
            snapshot.gps_satellites
        );


        Serial.print(
            "HDOP: "
        );

        Serial.println(
            snapshot.gps_hdop,
            2
        );
    }


    // --------------------------------------------------------
    // BATTERY
    // --------------------------------------------------------

    Serial.print(
        "Battery: "
    );


    if (
        snapshot.battery_valid
    )
    {
        Serial.print(
            snapshot.battery_voltage,
            2
        );

        Serial.print(
            " V / "
        );

        Serial.print(
            snapshot.battery_percent,
            1
        );

        Serial.println(
            "%"
        );
    }
    else
    {
#if ENABLE_BATTERY_MONITOR

        Serial.println(
            "NOT AVAILABLE"
        );

#else

        Serial.println(
            "DISABLED"
        );

#endif
    }


    // --------------------------------------------------------
    // ANALOG SENSOR HEALTH
    // --------------------------------------------------------

    Serial.print(
        "ADS1115 health: "
    );

    Serial.println(
        snapshot.ads1115_healthy
            ? "HEALTHY"
            : "DEGRADED"
    );


    Serial.println(
        "--------------------------------------------"
    );
}


// ============================================================
// RADIO RETRY
// ============================================================

static void retryLoRaIfRequired()
{
    if (
        lora_ready &&
        isLoRaReady()
    )
    {
        return;
    }


    unsigned long now =
        millis();


    if (
        now -
        last_lora_retry_ms <
        LORA_RETRY_INTERVAL_MS
    )
    {
        return;
    }


    last_lora_retry_ms =
        now;


    Serial.println();
    Serial.println(
        "Retrying LoRa initialization..."
    );


    lora_ready =
        initializeLoRa();


    if (
        lora_ready
    )
    {
        Serial.println(
            "LoRa recovered successfully."
        );
    }
    else
    {
        Serial.print(
            "LoRa still unavailable. Status: "
        );

        Serial.println(
            getLastLoRaStatus()
        );
    }
}


// ============================================================
// COMPLETE SENSOR → LORA CYCLE
// ============================================================

static void performTransmissionCycle()
{
    Serial.println();
    Serial.println(
        "=============================================="
    );

    Serial.println(
        "        GOLDTRACE MEASUREMENT CYCLE"
    );

    Serial.println(
        "=============================================="
    );


    // --------------------------------------------------------
    // READ PHYSICAL SENSORS
    // --------------------------------------------------------

    SensorSnapshot snapshot =
        readSensorSnapshot();


    printSensorSummary(
        snapshot
    );


    // --------------------------------------------------------
    // PACKET SEQUENCE
    // --------------------------------------------------------

    uint32_t current_sequence =
        sequence_number++;


    // --------------------------------------------------------
    // BUILD AUTHENTICATED PACKET
    // --------------------------------------------------------

    String packet =
        buildSensorPacket(
            snapshot,
            boot_id,
            current_sequence
        );


    if (
        packet.length() == 0
    )
    {
        packet_build_failures++;


        Serial.println(
            "Packet creation: FAILED"
        );


        Serial.print(
            "Packet build failures: "
        );

        Serial.println(
            packet_build_failures
        );


        return;
    }


    Serial.println(
        "Packet creation: OK"
    );


    Serial.print(
        "Sequence: "
    );

    Serial.println(
        current_sequence
    );


    Serial.print(
        "Packet size: "
    );

    Serial.print(
        packet.length()
    );

    Serial.println(
        " bytes"
    );


    /*
     * Do not print the complete authenticated packet
     * during normal field operation.
     *
     * This avoids unnecessarily exposing telemetry
     * authentication data through serial logs.
     */


    // --------------------------------------------------------
    // CHECK RADIO
    // --------------------------------------------------------

    if (
        !lora_ready ||
        !isLoRaReady()
    )
    {
        failed_transmissions++;


        Serial.println(
            "Transmission: SKIPPED - LoRa unavailable"
        );


        return;
    }


    // --------------------------------------------------------
    // TRANSMIT
    // --------------------------------------------------------

    bool transmitted =
        transmitLoRaPacket(
            packet
        );


    if (
        transmitted
    )
    {
        successful_transmissions++;


        Serial.println(
            "Transmission: SUCCESS"
        );
    }
    else
    {
        failed_transmissions++;


        Serial.println(
            "Transmission: FAILED"
        );
    }


    // --------------------------------------------------------
    // NODE STATISTICS
    // --------------------------------------------------------

    Serial.print(
        "Successful transmissions: "
    );

    Serial.println(
        successful_transmissions
    );


    Serial.print(
        "Failed transmissions: "
    );

    Serial.println(
        failed_transmissions
    );


    Serial.println(
        "=============================================="
    );
}


// ============================================================
// ARDUINO SETUP
// ============================================================

void setup()
{
    Serial.begin(
        115200
    );


    /*
     * Give the serial interface a short time to become
     * available without permanently waiting for a PC.
     */

    delay(
        1500
    );


    // --------------------------------------------------------
    // UNIQUE BOOT IDENTIFIER
    // --------------------------------------------------------

    boot_id =
        esp_random();


    if (
        boot_id == 0
    )
    {
        boot_id =
            1;
    }


    printStartupBanner();


    // --------------------------------------------------------
    // SENSOR SUITE
    // --------------------------------------------------------

    sensor_system_ready =
        initializeSensors();


    if (
        sensor_system_ready
    )
    {
        Serial.println(
            "Sensor system startup: READY"
        );
    }
    else
    {
        /*
         * Do not crash the complete node because one
         * physical sensor is unavailable.
         *
         * Health information is carried in telemetry,
         * allowing the downstream system to fail safely.
         */

        Serial.println(
            "Sensor system startup: DEGRADED"
        );
    }


    // --------------------------------------------------------
    // LORA
    // --------------------------------------------------------

    lora_ready =
        initializeLoRa();


    if (
        !lora_ready
    )
    {
        Serial.println(
            "LoRa startup: DEGRADED"
        );


        Serial.println(
            "Node will continue running and retry automatically."
        );


        last_lora_retry_ms =
            millis();
    }


    // --------------------------------------------------------
    // START TRANSMISSION TIMER
    // --------------------------------------------------------

    last_transmission_ms =
        millis();


    Serial.println();
    Serial.println(
        "GoldTrace node startup complete."
    );

    Serial.println(
        "Entering monitoring mode..."
    );

    Serial.println();
}


// ============================================================
// ARDUINO MAIN LOOP
// ============================================================

void loop()
{
    /*
     * Keep feeding incoming GPS NMEA characters to the
     * parser between measurement cycles.
     */

    pollGps(
        10
    );


    // --------------------------------------------------------
    // RECOVER LORA IF NECESSARY
    // --------------------------------------------------------

    retryLoRaIfRequired();


    // --------------------------------------------------------
    // PERIODIC SENSOR TRANSMISSION
    // --------------------------------------------------------

    unsigned long now =
        millis();


    if (
        now -
        last_transmission_ms >=
        TRANSMIT_INTERVAL_MS
    )
    {
        /*
         * Advance using the current time instead of
         * repeatedly adding the interval.
         *
         * This prevents a long sensor operation from causing
         * many immediate catch-up transmissions.
         */

        last_transmission_ms =
            now;


        performTransmissionCycle();
    }


    /*
     * Small cooperative delay.
     */

    delay(
        10
    );
}
