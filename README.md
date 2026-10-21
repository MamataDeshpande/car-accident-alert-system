# Car Accident Alert System

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

The projects code uses the **$GPRMC** sentence to extract GPS information. The text of the methodology also discusses GPS data in **$GPGGA** format. 

## Source Code

[Arduino program from Chapter 4.4](arduino/CarAccidentAlert/CarAccidentAlert.ino)


This is the original **prototype design**, not a modern implementation or a certified accident detection system. The code has not been retested on current Arduino hardware or newer libraries.

## Project Diagrams

<img width="464" height="318" alt="image" src="https://github.com/user-attachments/assets/2eb46e34-ab5b-466f-865f-c63a4bd7fc33" />

<img width="566" height="324" alt="image" src="https://github.com/user-attachments/assets/16bc94ef-cd7f-4975-91d6-4f20987ff490" />

<img width="477" height="393" alt="image" src="https://github.com/user-attachments/assets/e3b3514a-3669-4375-94ff-0631c81e4163" />



## Results

The report describes a **Proteus simulation** using virtual GPS and GSM terminals, as well as a hardware prototype where Arduino received position-sensor signals, displayed information on the LCD and sent an SMS with the location. The report also describes a ten-second LCD countdown in hardware.

<img width="184" height="249" alt="image" src="https://github.com/user-attachments/assets/28a1f1df-cef8-45a6-94db-dc59cfa1f0b4" />

<img width="230" height="306" alt="image" src="https://github.com/user-attachments/assets/db5353d5-73f4-4985-8766-de1143394e25" />



## Conclusion and Future Work

The project investigated an embedded method to locate a vehicle after an accident and send an alert through GPS and GSM. Future work suggested in the report includes a sound sensor, alcohol detection, a camera and nearby hospital/traffic-route information.


