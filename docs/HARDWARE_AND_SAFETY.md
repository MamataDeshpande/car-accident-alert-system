# Hardware interfaces and safety notes

**This is a lab-only teaching project, not a real accident detection or emergency notification device.**

Original report parts included Arduino/ATmega328P, ADXL335 accelerometer, a GPS receiver, a GSM module and 16x2 LCD. The fresh code suggests:

| Interface | Arduino pins | Description |
|---|---|---|
| ADXL335 axes | A1/A2/A3 | Analog X, Y, Z; check module voltage |
| GPS receiver UART | D10/D11 | SoftwareSerial RX/TX; verify module logic levels |
| GSM modem UART | D2/D3 | SoftwareSerial RX/TX; verify safe supply |
| LCD | D4–D9 | RS, enable, data D4–D7 |
| Manual cancel | D12 to ground | INPUT_PULLUP |
| Status LED | D13 | Test indicator |

GSM modules such as SIM900 can draw significant current during transmission. Use a separately regulated supply suited to the specific breakout and common ground. Never power a modem directly from an Arduino I/O pin.

A basic state machine monitors simulated acceleration changes, starts a 10-second cancellation countdown after a persistent deviation, prints a **mock** alert, then enters cooldown. No threshold is validated for detecting real crashes.

**Critical limitations:** sensor installation angle, potholes, braking, missing GPS reception, serial receiver switching, cellular coverage, power interruptions, duplicate alerts, lost SMS, and hardware faults have not been validated. The optional SMS code does not confirm delivery and must only be used with a consenting test phone. No road deployment.

Use `ENABLE_REAL_SMS 0` in `config.h` unless you have explicitly authorized a controlled lab setup. Never configure emergency service numbers.
