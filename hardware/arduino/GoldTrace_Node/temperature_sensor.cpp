#include <Arduino.h>

#include <OneWire.h>
#include <DallasTemperature.h>

#include <math.h>

#include "config.h"
#include "temperature_sensor.h"


// ============================================================
// DS18B20 OBJECTS
// ============================================================

static OneWire temperature_one_wire(
    PIN_ONEWIRE
);


static DallasTemperature temperature_bus(
    &temperature_one_wire
);


static bool temperature_ready =
    false;


static constexpr uint8_t
TEMPERATURE_RESOLUTION_BITS =
    11;


// ============================================================
// VALIDATION
// ============================================================

static bool isValidTemperature(
    float temperature_c
)
{
    if (
        !isfinite(
            temperature_c
        )
    )
    {
        return false;
    }


    /*
     * DallasTemperature uses DEVICE_DISCONNECTED_C,
     * normally -127 C, when communication fails.
     */

    if (
        temperature_c ==
        DEVICE_DISCONNECTED_C
    )
    {
        return false;
    }


    /*
     * 85 C is commonly seen as the DS18B20
     * power-on/default scratchpad value if a
     * conversion has not completed properly.
     */

    if (
        fabsf(
            temperature_c -
            85.0f
        ) <
        0.01f
    )
    {
        return false;
    }


    /*
     * Physical DS18B20 operating range.
     */

    if (
        temperature_c < -55.0f ||
        temperature_c > 125.0f
    )
    {
        return false;
    }


    return true;
}


// ============================================================
// INITIALIZATION
// ============================================================

bool initializeTemperatureSensor()
{
    Serial.println(
        "Initializing DS18B20 water temperature sensor..."
    );


    temperature_bus.begin();


    int device_count =
        temperature_bus.getDeviceCount();


    Serial.print(
        "DS18B20 devices detected: "
    );


    Serial.println(
        device_count
    );


    if (
        device_count <= 0
    )
    {
        Serial.println(
            "DS18B20: NOT DETECTED"
        );


        temperature_ready =
            false;


        return false;
    }


    /*
     * 11-bit resolution:
     *
     * Resolution: 0.125 C
     * Conversion time is shorter than 12-bit mode,
     * which is useful for the field sensor node.
     */

    temperature_bus.setResolution(
        TEMPERATURE_RESOLUTION_BITS
    );


    /*
     * Use blocking conversion for now.
     *
     * This keeps individual sensor testing simple.
     * We can switch to asynchronous conversion later
     * when optimizing the complete node loop.
     */

    temperature_bus.setWaitForConversion(
        true
    );


    temperature_ready =
        true;


    Serial.println(
        "DS18B20: READY"
    );


    Serial.print(
        "Resolution: "
    );


    Serial.print(
        TEMPERATURE_RESOLUTION_BITS
    );


    Serial.println(
        "-bit"
    );


    return true;
}


// ============================================================
// TEMPERATURE READING
// ============================================================

TemperatureReading readTemperatureSensor()
{
    TemperatureReading reading = {
        false,
        false,
        0.0f,
        0.0f,
        TEMPERATURE_RESOLUTION_BITS
    };


    if (
        !temperature_ready
    )
    {
        return reading;
    }


    /*
     * Request a fresh temperature conversion.
     */

    temperature_bus.requestTemperatures();


    float temperature_c =
        temperature_bus.getTempCByIndex(
            0
        );


    if (
        !isValidTemperature(
            temperature_c
        )
    )
    {
        Serial.print(
            "DS18B20 invalid/disconnected reading: "
        );


        Serial.println(
            temperature_c
        );


        return reading;
    }


    float temperature_f =
        (
            temperature_c *
            9.0f /
            5.0f
        ) +
        32.0f;


    reading.healthy =
        true;


    reading.connected =
        true;


    reading.celsius =
        temperature_c;


    reading.fahrenheit =
        temperature_f;


    return reading;
}
