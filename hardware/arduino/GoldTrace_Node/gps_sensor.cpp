#include <Arduino.h>

#include <TinyGPSPlus.h>

#include "config.h"
#include "gps_sensor.h"


// ============================================================
// GPS OBJECTS
// ============================================================

static TinyGPSPlus gps_parser;


static HardwareSerial gps_serial(
    1
);


static bool gps_ready =
    false;


// ============================================================
// INITIALIZATION
// ============================================================

bool initializeGPSSensor()
{
    Serial.println(
        "Initializing GPS module..."
    );


    gps_serial.begin(
        GPS_BAUD,
        SERIAL_8N1,
        PIN_GPS_RX,
        PIN_GPS_TX
    );


    delay(
        100
    );


    gps_ready =
        true;


    Serial.print(
        "GPS UART ready at "
    );


    Serial.print(
        GPS_BAUD
    );


    Serial.println(
        " baud"
    );


    return true;
}


// ============================================================
// FEED NMEA DATA INTO TinyGPS++
// ============================================================

void updateGPSSensor(
    unsigned long duration_ms
)
{
    if (
        !gps_ready
    )
    {
        return;
    }


    unsigned long started =
        millis();


    do
    {
        while (
            gps_serial.available() > 0
        )
        {
            char character =
                static_cast<char>(
                    gps_serial.read()
                );


            gps_parser.encode(
                character
            );
        }


        delay(
            1
        );

    } while (
        millis() -
        started <
        duration_ms
    );
}


// ============================================================
// READ CURRENT GPS STATE
// ============================================================

GPSReading readGPSSensor()
{
    GPSReading reading = {
        false,
        false,
        false,
        0.0,
        0.0,
        0.0f,
        0.0f,
        0.0f,
        0,
        0,
        0
    };


    if (
        !gps_ready
    )
    {
        return reading;
    }


    /*
     * Give the UART a short opportunity to receive
     * additional NMEA sentences before reading state.
     */

    updateGPSSensor(
        250
    );


    uint32_t chars =
        gps_parser.charsProcessed();


    reading.characters_processed =
        chars;


    /*
     * Receiving NMEA data means the serial connection
     * between GPS and ESP32 is functioning.
     */

    reading.receiving_data =
        chars > 10;


    /*
     * A GPS can be healthy while still having no fix,
     * particularly indoors.
     */

    reading.healthy =
        reading.receiving_data;


    if (
        gps_parser.satellites.isValid()
    )
    {
        reading.satellites =
            gps_parser.satellites.value();
    }


    if (
        gps_parser.hdop.isValid()
    )
    {
        reading.hdop =
            static_cast<float>(
                gps_parser.hdop.hdop()
            );
    }


    if (
        gps_parser.altitude.isValid()
    )
    {
        reading.altitude_m =
            static_cast<float>(
                gps_parser.altitude.meters()
            );
    }


    if (
        gps_parser.speed.isValid()
    )
    {
        reading.speed_kmh =
            static_cast<float>(
                gps_parser.speed.kmph()
            );
    }


    if (
        gps_parser.location.isValid()
    )
    {
        reading.fix_valid =
            true;


        reading.latitude =
            gps_parser.location.lat();


        reading.longitude =
            gps_parser.location.lng();


        reading.fix_age_ms =
            gps_parser.location.age();
    }


    return reading;
}
