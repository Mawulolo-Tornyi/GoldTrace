#include <Arduino.h>

#include <SPI.h>

#include <RadioLib.h>

#include "config.h"
#include "radio_transport.h"


// ============================================================
// RFM95 / SX1276 RADIO
// ============================================================

static SPIClass lora_spi(
    FSPI
);


static SX1276 radio =
    new Module(
        PIN_LORA_CS,
        PIN_LORA_DIO0,
        PIN_LORA_RST,
        PIN_LORA_DIO1,
        lora_spi
    );


static bool lora_ready =
    false;


static int16_t last_lora_status =
    RADIOLIB_ERR_NONE;


// ============================================================
// INITIALIZE RADIO
// ============================================================

bool initializeLoRa()
{
    Serial.println(
        "Initializing LoRa radio..."
    );


    /*
     * IMPORTANT:
     *
     * LORA_FREQUENCY_MHZ in config.h is currently a
     * development value.
     *
     * The final field value must match:
     *
     * 1. The physical LoRa module
     * 2. The antenna
     * 3. The permitted local radio configuration
     */


    lora_spi.begin(
        PIN_LORA_SCK,
        PIN_LORA_MISO,
        PIN_LORA_MOSI,
        PIN_LORA_CS
    );


    last_lora_status =
        radio.begin(
            LORA_FREQUENCY_MHZ,
            LORA_BANDWIDTH_KHZ,
            LORA_SPREADING_FACTOR,
            LORA_CODING_RATE,
            LORA_SYNC_WORD,
            LORA_TX_POWER_DBM,
            8,
            0
        );


    if (
        last_lora_status !=
        RADIOLIB_ERR_NONE
    )
    {
        Serial.print(
            "LoRa initialization failed. Code: "
        );


        Serial.println(
            last_lora_status
        );


        lora_ready =
            false;


        return false;
    }


    last_lora_status =
        radio.setCRC(
            true
        );


    if (
        last_lora_status !=
        RADIOLIB_ERR_NONE
    )
    {
        Serial.print(
            "LoRa CRC setup failed. Code: "
        );


        Serial.println(
            last_lora_status
        );


        lora_ready =
            false;


        return false;
    }


    lora_ready =
        true;


    Serial.println(
        "LoRa radio: READY"
    );


    Serial.print(
        "Frequency: "
    );


    Serial.print(
        LORA_FREQUENCY_MHZ,
        3
    );


    Serial.println(
        " MHz"
    );


    Serial.print(
        "Node ID: "
    );


    Serial.println(
        NODE_ID
    );


    return true;
}


// ============================================================
// TRANSMIT PACKET
// ============================================================

bool transmitLoRaPacket(
    const String &packet
)
{
    if (
        !lora_ready
    )
    {
        Serial.println(
            "LoRa transmission skipped: radio not ready."
        );


        return false;
    }


    if (
        packet.length() == 0
    )
    {
        Serial.println(
            "LoRa transmission skipped: empty packet."
        );


        return false;
    }


    if (
        packet.length() >
        MAX_WIRE_PACKET_BYTES
    )
    {
        Serial.println(
            "LoRa transmission skipped: packet too large."
        );


        return false;
    }


    last_lora_status =
        radio.transmit(
            packet
        );


    if (
        last_lora_status !=
        RADIOLIB_ERR_NONE
    )
    {
        Serial.print(
            "LoRa transmission failed. Code: "
        );


        Serial.println(
            last_lora_status
        );


        return false;
    }


    Serial.print(
        "LoRa packet transmitted: "
    );


    Serial.print(
        packet.length()
    );


    Serial.println(
        " bytes"
    );


    return true;
}


// ============================================================
// STATUS
// ============================================================

bool isLoRaReady()
{
    return lora_ready;
}


int16_t getLastLoRaStatus()
{
    return last_lora_status;
}
