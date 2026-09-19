#include <Arduino.h>

#include <ArduinoJson.h>

#include <mbedtls/md.h>

#include "config.h"
#include "secrets.h"
#include "sensor_types.h"
#include "packet_builder.h"


// ============================================================
// HARDWARE HEALTH MASK
// ============================================================

static uint8_t buildHealthMask(
    const SensorSnapshot &snapshot
)
{
    uint8_t mask =
        0;


    /*
     * Bit layout:
     *
     * bit 0 = ADS1115 / analog sensors
     * bit 1 = microphone
     * bit 2 = vibration
     * bit 3 = temperature
     * bit 4 = GPS fix
     * bit 5 = battery monitor
     */


    if (
        snapshot.ads1115_healthy
    )
    {
        mask |=
            (1 << 0);
    }


    if (
        snapshot.audio.healthy
    )
    {
        mask |=
            (1 << 1);
    }


    if (
        snapshot.vibration.healthy
    )
    {
        mask |=
            (1 << 2);
    }


    if (
        snapshot.temperature_valid
    )
    {
        mask |=
            (1 << 3);
    }


    if (
        snapshot.gps_valid
    )
    {
        mask |=
            (1 << 4);
    }


    if (
        snapshot.battery_valid
    )
    {
        mask |=
            (1 << 5);
    }


    return mask;
}


// ============================================================
// HMAC SHA-256
// ============================================================

static String createPacketSignature(
    const String &payload
)
{
    unsigned char digest[
        32
    ];


    const mbedtls_md_info_t *md_info =
        mbedtls_md_info_from_type(
            MBEDTLS_MD_SHA256
        );


    if (
        md_info == nullptr
    )
    {
        return "";
    }


    int result =
        mbedtls_md_hmac(
            md_info,
            reinterpret_cast<const unsigned char *>(
                LORA_SHARED_KEY
            ),
            strlen(
                LORA_SHARED_KEY
            ),
            reinterpret_cast<const unsigned char *>(
                payload.c_str()
            ),
            payload.length(),
            digest
        );


    if (
        result != 0
    )
    {
        return "";
    }


    /*
     * We use the first 16 bytes of SHA-256.
     *
     * 16 bytes = 128-bit authentication tag.
     * Hex representation = 32 characters.
     */

    String signature;


    signature.reserve(
        32
    );


    static const char hex_chars[] =
        "0123456789abcdef";


    for (
        int index = 0;
        index < 16;
        index++
    )
    {
        unsigned char value =
            digest[
                index
            ];


        signature +=
            hex_chars[
                (
                    value >>
                    4
                )
                &
                0x0F
            ];


        signature +=
            hex_chars[
                value &
                0x0F
            ];
    }


    return signature;
}


// ============================================================
// BUILD GOLDTRACE SENSOR PAYLOAD
// ============================================================

String buildSensorPacket(
    const SensorSnapshot &snapshot,
    uint32_t boot_id,
    uint32_t sequence_number
)
{
    JsonDocument document;


    // --------------------------------------------------------
    // PACKET IDENTITY
    // --------------------------------------------------------

    document["v"] =
        GOLDTRACE_PROTOCOL_VERSION;


    document["id"] =
        NODE_ID;


    document["b"] =
        boot_id;


    document["seq"] =
        sequence_number;


    document["up"] =
        millis();


    // --------------------------------------------------------
    // TURBIDITY
    // --------------------------------------------------------

    document["tu"] =
        snapshot.turbidity_ntu;


    document["tv"] =
        snapshot.turbidity_voltage;


    // --------------------------------------------------------
    // VIBRATION
    // --------------------------------------------------------

    document["vr"] =
        snapshot.vibration.rms;


    document["vp"] =
        snapshot.vibration.peak;


    if (
        snapshot.vibration.healthy
    )
    {
        document["vsr"] =
            static_cast<uint32_t>(
                snapshot.vibration.sample_rate_hz +
                0.5f
            );
    }


    // --------------------------------------------------------
    // AUDIO
    // --------------------------------------------------------

    document["ar"] =
        snapshot.audio.rms;


    document["ap"] =
        snapshot.audio.peak;


    document["az"] =
        snapshot.audio.zero_crossing_rate;


    if (
        snapshot.audio.healthy
    )
    {
        document["asr"] =
            static_cast<uint32_t>(
                snapshot.audio.sample_rate_hz +
                0.5f
            );
    }


    // --------------------------------------------------------
    // HARDWARE HEALTH
    // --------------------------------------------------------

    document["sh"] =
        buildHealthMask(
            snapshot
        );


    // --------------------------------------------------------
    // OPTIONAL TEMPERATURE
    // --------------------------------------------------------

    if (
        snapshot.temperature_valid
    )
    {
        document["tc"] =
            snapshot.temperature_c;
    }


    // --------------------------------------------------------
    // OPTIONAL BATTERY
    // --------------------------------------------------------

    if (
        snapshot.battery_valid
    )
    {
        document["bv"] =
            snapshot.battery_voltage;


        document["bp"] =
            snapshot.battery_percent;
    }


    // --------------------------------------------------------
    // OPTIONAL GPS
    // --------------------------------------------------------

    if (
        snapshot.gps_valid
    )
    {
        document["lat"] =
            snapshot.latitude;


        document["lon"] =
            snapshot.longitude;


        document["sat"] =
            snapshot.gps_satellites;


        document["hd"] =
            snapshot.gps_hdop;
    }


    // --------------------------------------------------------
    // SERIALIZE
    // --------------------------------------------------------

    String payload;


    payload.reserve(
        220
    );


    serializeJson(
        document,
        payload
    );


    // --------------------------------------------------------
    // AUTHENTICATE
    // --------------------------------------------------------

    String signature =
        createPacketSignature(
            payload
        );


    if (
        signature.length() != 32
    )
    {
        Serial.println(
            "Packet signing failed."
        );


        return "";
    }


    String wire_packet;


    wire_packet.reserve(
        payload.length() +
        signature.length() +
        1
    );


    wire_packet +=
        payload;


    wire_packet +=
        "|";


    wire_packet +=
        signature;


    // --------------------------------------------------------
    // SIZE SAFETY
    // --------------------------------------------------------

    if (
        wire_packet.length() >
        MAX_WIRE_PACKET_BYTES
    )
    {
        Serial.print(
            "Packet too large: "
        );


        Serial.print(
            wire_packet.length()
        );


        Serial.println(
            " bytes"
        );


        return "";
    }


    return wire_packet;
}
