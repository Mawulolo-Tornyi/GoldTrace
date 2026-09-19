#include <Arduino.h>

#include "sensors.h"

#include "turbidity_sensor.h"
#include "vibration_sensor.h"
#include "audio_sensor.h"
#include "temperature_sensor.h"
#include "gps_sensor.h"
#include "battery_sensor.h"


// ============================================================
// SENSOR INITIALIZATION STATE
// ============================================================

static bool turbidity_initialized =
    false;


static bool vibration_initialized =
    false;


static bool audio_initialized =
    false;


static bool temperature_initialized =
    false;


static bool gps_initialized =
    false;


static bool battery_initialized =
    false;


// ============================================================
// INITIALIZE COMPLETE GOLDTRACE SENSOR SUITE
// ============================================================

bool initializeSensors()
{
    Serial.println();
    Serial.println(
        "========================================"
    );

    Serial.println(
        "   GOLDTRACE SENSOR INITIALIZATION"
    );

    Serial.println(
        "========================================"
    );


    // --------------------------------------------------------
    // TURBIDITY
    // --------------------------------------------------------

    turbidity_initialized =
        initializeTurbiditySensor();


    // --------------------------------------------------------
    // GEOPHONE / VIBRATION
    // --------------------------------------------------------

    vibration_initialized =
        initializeVibrationSensor();


    // --------------------------------------------------------
    // INMP441 MICROPHONE
    // --------------------------------------------------------

    audio_initialized =
        initializeAudioSensor();


    // --------------------------------------------------------
    // DS18B20 WATER TEMPERATURE
    // --------------------------------------------------------

    temperature_initialized =
        initializeTemperatureSensor();


    // --------------------------------------------------------
    // GPS
    // --------------------------------------------------------

    gps_initialized =
        initializeGPSSensor();


    // --------------------------------------------------------
    // BATTERY
    // --------------------------------------------------------

    battery_initialized =
        initializeBatterySensor();


    Serial.println();
    Serial.println(
        "========== SENSOR INITIALIZATION SUMMARY =========="
    );


    Serial.print(
        "Turbidity: "
    );

    Serial.println(
        turbidity_initialized
            ? "READY"
            : "NOT READY"
    );


    Serial.print(
        "Vibration: "
    );

    Serial.println(
        vibration_initialized
            ? "READY"
            : "NOT READY"
    );


    Serial.print(
        "INMP441: "
    );

    Serial.println(
        audio_initialized
            ? "READY"
            : "NOT READY"
    );


    Serial.print(
        "DS18B20: "
    );

    Serial.println(
        temperature_initialized
            ? "READY"
            : "OPTIONAL / NOT READY"
    );


    Serial.print(
        "GPS UART: "
    );

    Serial.println(
        gps_initialized
            ? "READY"
            : "OPTIONAL / NOT READY"
    );


#if ENABLE_BATTERY_MONITOR

    Serial.print(
        "Battery monitor: "
    );

    Serial.println(
        battery_initialized
            ? "READY"
            : "NOT READY"
    );

#else

    Serial.println(
        "Battery monitor: DISABLED"
    );

#endif


    /*
     * GoldTrace's primary evidence sensors are:
     *
     *   turbidity
     *   vibration
     *   audio
     *
     * GPS and DS18B20 may be unavailable without
     * preventing the ESP32 from starting.
     */

    bool core_sensors_ready =
        turbidity_initialized &&
        vibration_initialized &&
        audio_initialized;


    Serial.println();


    if (
        core_sensors_ready
    )
    {
        Serial.println(
            "Core GoldTrace sensors: READY"
        );
    }
    else
    {
        Serial.println(
            "Core GoldTrace sensors: DEGRADED"
        );
    }


    return core_sensors_ready;
}


// ============================================================
// GPS BACKGROUND POLLING
// ============================================================

void pollGps(
    unsigned long duration_ms
)
{
    if (
        gps_initialized
    )
    {
        updateGPSSensor(
            duration_ms
        );
    }
}


// ============================================================
// READ COMPLETE SENSOR SNAPSHOT
// ============================================================

SensorSnapshot readSensorSnapshot()
{
    SensorSnapshot snapshot;


    // ========================================================
    // TURBIDITY
    // ========================================================

    TurbidityReading turbidity =
        readTurbiditySensor();


    if (
        turbidity.healthy
    )
    {
        snapshot.turbidity_ntu =
            turbidity.ntu;


        snapshot.turbidity_voltage =
            turbidity.voltage;
    }


    // ========================================================
    // VIBRATION
    // ========================================================

    VibrationReading vibration =
        readVibrationSensor();


    snapshot.vibration.healthy =
        vibration.healthy;


    if (
        vibration.healthy
    )
    {
        snapshot.vibration.rms =
            vibration.rms;


        snapshot.vibration.peak =
            vibration.peak;


        snapshot.vibration.sample_rate_hz =
            vibration.sample_rate_hz;
    }


    // ========================================================
    // AUDIO
    // ========================================================

    AudioReading audio =
        readAudioSensor();


    snapshot.audio.healthy =
        audio.healthy;


    if (
        audio.healthy
    )
    {
        snapshot.audio.rms =
            audio.rms;


        snapshot.audio.peak =
            audio.peak;


        snapshot.audio.zero_crossing_rate =
            audio.zero_crossing_rate;


        snapshot.audio.sample_rate_hz =
            audio.sample_rate_hz;
    }


    // ========================================================
    // TEMPERATURE
    // ========================================================

    TemperatureReading temperature =
        readTemperatureSensor();


    snapshot.temperature_valid =
        (
            temperature.healthy &&
            temperature.connected
        );


    if (
        snapshot.temperature_valid
    )
    {
        snapshot.temperature_c =
            temperature.celsius;
    }


    // ========================================================
    // GPS
    // ========================================================

    GPSReading gps =
        readGPSSensor();


    snapshot.gps_valid =
        gps.fix_valid;


    snapshot.gps_satellites =
        gps.satellites;


    snapshot.gps_hdop =
        gps.hdop;


    if (
        gps.fix_valid
    )
    {
        snapshot.latitude =
            gps.latitude;


        snapshot.longitude =
            gps.longitude;
    }


    // ========================================================
    // BATTERY
    // ========================================================

    BatteryReading battery =
        readBatterySensor();


    snapshot.battery_valid =
        (
            battery.enabled &&
            battery.healthy
        );


    if (
        snapshot.battery_valid
    )
    {
        snapshot.battery_percent =
            battery.percentage;


        snapshot.battery_voltage =
            battery.battery_voltage;
    }


    // ========================================================
    // ADS1115 HEALTH
    // ========================================================

    /*
     * Turbidity and geophone are the primary ADS1115
     * channels used by GoldTrace.
     */

    snapshot.ads1115_healthy =
        (
            turbidity.healthy &&
            vibration.healthy
        );


    return snapshot;
}
