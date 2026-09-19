#pragma once


/*
 * ============================================================
 * GOLDTRACE LORA SHARED SECRET
 * ============================================================
 *
 * Both ESP32 nodes and the Raspberry Pi gateway must use
 * the SAME secret.
 *
 * On the hardware day:
 *
 * 1. Copy this file as secrets.h
 * 2. Replace the example value
 * 3. Use the same secret on the Raspberry Pi
 *
 * Never upload the real secret to GitHub.
 */

#define LORA_SHARED_KEY \
"CHANGE_THIS_TO_A_RANDOM_SECRET"
