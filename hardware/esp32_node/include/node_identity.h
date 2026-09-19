#pragma once


/*
 * ============================================================
 * GOLDTRACE NODE IDENTITY
 * ============================================================
 *
 * Change ONLY this value when flashing the physical ESP32.
 *
 * 1 = NODE_A / UPSTREAM
 * 2 = NODE_B / DOWNSTREAM
 *
 * Flash first ESP32 with:
 *
 *     GOLDTRACE_NODE_NUMBER 1
 *
 * Flash second ESP32 with:
 *
 *     GOLDTRACE_NODE_NUMBER 2
 */

#define GOLDTRACE_NODE_NUMBER 1


/*
 * PlatformIO may provide NODE_ID through a build flag.
 *
 * Arduino IDE normally does not, so the selection above
 * becomes the node identity.
 */

#ifndef NODE_ID

    #if GOLDTRACE_NODE_NUMBER == 1

        #define NODE_ID "NODE_A"

    #elif GOLDTRACE_NODE_NUMBER == 2

        #define NODE_ID "NODE_B"

    #else

        #error "GOLDTRACE_NODE_NUMBER must be 1 or 2"

    #endif

#endif
