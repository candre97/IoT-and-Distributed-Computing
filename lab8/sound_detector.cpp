/* mbed Microcontroller Library
 * Copyright (c) 2018 ARM Limited
 * SPDX-License-Identifier: Apache-2.0
 */

#include "mbed.h"
#include "platform/mbed_thread.h"
#include "stats_report.h"
#include <AnalogIn.h>
#include <AnalogOut.h>

AnalogOut v_src(GPIO0);
AnalogIn therm(GPIO2);

#define SLEEP_TIME                  50 // (msec)
#define PRINT_AFTER_N_LOOPS         20

// main() runs in its own thread in the OS
int main()
{
    SystemReport sys_state( SLEEP_TIME * PRINT_AFTER_N_LOOPS /* Loop delay time in ms */);
    v_src = 1.0; /* Going to use a digital output as V_src */
    float max = 0; 
    while (true) {
        thread_sleep_for(SLEEP_TIME);
        v_src = 1.0;
        float raw_analog_val = 0; 
        
        for(int i = 0; i < 10; i++) {
            raw_analog_val += therm.read();
        }
        raw_analog_val /= 10;
        printf("Raw Analog Percentage 10 read AVG %f\n", raw_analog_val); 
        if (raw_analog_val > max) {
            max = raw_analog_val;
            printf("NEW MAX: %f\n", max);
            thread_sleep_for(3000); 
        }
    }
}
