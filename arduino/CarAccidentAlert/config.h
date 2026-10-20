#pragma once
// EDUCATIONAL PROTOTYPE ONLY. Not a certified crash/alert system.
// All thresholds and delays are illustrative, not validated.
#define ENABLE_REAL_SMS 0
#define SMS_RECIPIENT_CONFIGURED 0
#define SMS_RECIPIENT_NUMBER "+0000000000"
#if ENABLE_REAL_SMS && !SMS_RECIPIENT_CONFIGURED
#error "Explicitly configure and verify your own test phone number before enabling SMS."
#endif
#define ACCEL_ADC_DELTA 90
#define REQUIRED_CONSECUTIVE_SAMPLES 3
#define SENSOR_PERIOD_MS 50UL
#define CANCEL_WINDOW_MS 10000UL
#define COOLDOWN_MS 15000UL
#define GPS_MAX_AGE_MS 30000UL
