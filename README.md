# Car Accident Alert System

**B.Tech. Electronics and Telecommunication Project (2017–2018)**  
**Government College of Engineering, Karad**

**Project members:** Mamata Shodhan Deshpande and Gouri Prakash Wayachal.

## Introduction

The Car Accident Alert System was developed to detect sudden changes in vehicle position and send the accident location through an SMS. It uses an Arduino (ATmega328P) with an accelerometer, GPS receiver, GSM modem, and 16×2 LCD.

The purpose is to inform a predefined contact about a possible accident and provide the vehicle's coordinates using a Google Maps link.

## Components

| Component | Description |
|---|---|
| Arduino / ATmega328P | Reads sensor signals and controls the overall system |
| ADXL335 accelerometer | Detects sudden changes on X, Y and Z axes |
| SIM28ML GPS module | Provides the location coordinates |
| SIM900A GSM module | Sends an SMS with accident location |
| 16×2 LCD | Displays status, latitude, longitude and speed |

## Methodology

The accelerometer readings are calibrated when the system starts. During monitoring, the Arduino compares current X, Y and Z values with the initial readings. When the difference exceeds the preset limits, the system reads GPS information and sends a message to the predefined number using GSM.

The alert message contains latitude, longitude, speed in knots, and a Google Maps link.

The report's code uses the **$GPRMC** sentence to extract GPS information. The text of the methodology also discusses GPS data in **$GPGGA** format. Both descriptions have been preserved as part of the original report rather than replaced with a new GPS library.

## Source Code

[Arduino program from Chapter 4.4](arduino/CarAccidentAlert/CarAccidentAlert.ino)

The source code was transcribed from the report, preserving the original variables, threshold constants, GSM AT commands and GPS parsing approach. Line wrapping caused by the printed PDF was normalized for a code file. The SMS number remains the report's original `XXXXXXXXXX` placeholder.

This is the original **2017–2018 prototype design**, not a modern implementation or a certified accident detection system. The code has not been retested on current Arduino hardware or newer libraries.

## Results

The report describes a **Proteus simulation** using virtual GPS and GSM terminals, as well as a hardware prototype where Arduino received position-sensor signals, displayed information on the LCD and sent an SMS with the location. The report also describes a ten-second LCD countdown in hardware; this countdown is **not present in the printed Chapter 4.4 code**.

## Conclusion and Future Work

The project investigated an embedded method to locate a vehicle after an accident and send an alert through GPS and GSM. Future work suggested in the report includes a sound sensor, alcohol detection, a camera and nearby hospital/traffic-route information.

*The repository documents an academic prototype. It should not be relied upon for crash detection or emergency communication in a real vehicle.*
