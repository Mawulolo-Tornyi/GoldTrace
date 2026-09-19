#pragma once

#include "node_identity.h"


// ============================================================
// GOLDTRACE FIRMWARE
// ============================================================

#define GOLDTRACE_PROTOCOL_VERSION 1


// ============================================================
// I2C BUS
// ============================================================
//
// ADS1115 and other I2C devices share this bus.
//

#define PIN_I2C_SDA 4
#define PIN_I2C_SCL 5


// ============================================================
// INMP441 I2S MICROPHONE
// ============================================================

#define PIN_I2S_BCLK 6
#define PIN_I2S_WS   7
#define PIN_I2S_DIN  15

#define AUDIO_SAMPLE_RATE 16000
#define AUDIO_SAMPLES 512


// ============================================================
// DS18B20 WATER TEMPERATURE
// ============================================================

#define PIN_ONEWIRE 16


// ============================================================
// GPS UART
// ============================================================
//
// GPS TX -> ESP32 RX pin 17
// GPS RX -> ESP32 TX pin 18
//

#define PIN_GPS_RX 17
#define PIN_GPS_TX 18

#define GPS_BAUD 9600


// ============================================================
// RFM95 / SX1276 LORA
// ============================================================

#define PIN_LORA_DIO0 8
#define PIN_LORA_RST  9
#define PIN_LORA_CS   10

#define PIN_LORA_MOSI 11
#define PIN_LORA_SCK  12
#define PIN_LORA_MISO 13

#define PIN_LORA_DIO1 14


/*
 * DEVELOPMENT RADIO CONFIGURATION
 *
 * Do not treat this frequency as final field authorization.
 *
 * Before deployment we will confirm:
 *
 * - the exact RFM95/SX1276 module version
 * - antenna frequency
 * - permitted operating band
 * - permitted transmission power
 */

#define LORA_FREQUENCY_MHZ 868.0

#define LORA_BANDWIDTH_KHZ 125.0

#define LORA_SPREADING_FACTOR 9

#define LORA_CODING_RATE 7

#define LORA_SYNC_WORD 0x12

#define LORA_TX_POWER_DBM 13


// ============================================================
// TELEMETRY
// ============================================================

#define TRANSMIT_INTERVAL_MS 5000

#define MAX_WIRE_PACKET_BYTES 240


// ============================================================
// TURBIDITY CALIBRATION
// ============================================================
//
// THESE VALUES ARE TEMPORARY.
//
// On the hardware/testing day we will calibrate the actual
// turbidity probe using clean water and known muddy samples.
//

#define TURBIDITY_CLEAR_VOLTAGE 2.50f

#define TURBIDITY_NTU_PER_VOLT 400.0f


// ============================================================
// BATTERY MONITOR
// ============================================================
//
// Leave disabled until the actual battery and resistor
// divider have been selected.
//

#define ENABLE_BATTERY_MONITOR 0


/*
 * Example development value only.
 *
 * Actual value must be calculated from:
 *
 *   divider ratio =
 *       (R1 + R2) / R2
 */

#define BATTERY_DIVIDER_RATIO 2.0f


/*
 * These values currently represent a single-cell
 * lithium-type development assumption.
 *
 * They MUST be changed if the final GoldTrace power
 * system uses another battery arrangement.
 */

#define BATTERY_EMPTY_V 3.20f

#define BATTERY_FULL_V 4.20f
