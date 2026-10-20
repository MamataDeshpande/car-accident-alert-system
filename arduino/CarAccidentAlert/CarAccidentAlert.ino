/*
 * Original, independently authored educational reconstruction of an
 * undergraduate car-accident alert electronics project.
 * NOT a real-world emergency device. NEVER deploy in a road vehicle.
 * SMS DISABLED by default. Only use with your own consenting test recipient.
 */
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <LiquidCrystal.h>
#include <TinyGPS++.h>
#include "config.h"

SoftwareSerial gpsSerial(10,11);
SoftwareSerial gsmSerial(2,3);
LiquidCrystal lcd(4,5,6,7,8,9);
TinyGPSPlus gps;
const uint8_t ACCEL_X=A1, ACCEL_Y=A2, ACCEL_Z=A3;
const uint8_t CANCEL_BUTTON=12, STATUS_LED=13;
int referenceX=0, referenceY=0, referenceZ=0;
uint8_t shockStreak=0;
unsigned long lastSampleMs=0, triggeredAtMs=0, resetAtMs=0;
enum State : uint8_t { MONITORING, COUNTDOWN, DONE, CANCELLED };
State state=MONITORING;

void showStatus(const __FlashStringHelper *a, const __FlashStringHelper *b) {
  lcd.clear(); lcd.setCursor(0,0); lcd.print(a);
  lcd.setCursor(0,1); lcd.print(b);
}
void calibrateReference() {
  showStatus(F("Calibrating..."), F("Keep still"));
  long x=0,y=0,z=0;
  for(int i=0;i<30;i++) {x+=analogRead(ACCEL_X);y+=analogRead(ACCEL_Y);z+=analogRead(ACCEL_Z);delay(30);}
  referenceX=x/30; referenceY=y/30; referenceZ=z/30;
}
bool candidateShock() {
  int dx=abs(analogRead(ACCEL_X)-referenceX);
  int dy=abs(analogRead(ACCEL_Y)-referenceY);
  int dz=abs(analogRead(ACCEL_Z)-referenceZ);
  bool exceeded=dx>ACCEL_ADC_DELTA || dy>ACCEL_ADC_DELTA || dz>ACCEL_ADC_DELTA;
  if(exceeded) {if(shockStreak<REQUIRED_CONSECUTIVE_SAMPLES) ++shockStreak;}
  else shockStreak=0;
  return shockStreak>=REQUIRED_CONSECUTIVE_SAMPLES;
}
void emitLocation(Stream &out) {
  if(gps.location.isValid() && gps.location.age()<=GPS_MAX_AGE_MS) {
    out.print(F("Coordinates: "));out.print(gps.location.lat(),6);
    out.print(F(", "));out.println(gps.location.lng(),6);
    out.print(F("https://www.google.com/maps?q="));
    out.print(gps.location.lat(),6);out.print(',');
    out.println(gps.location.lng(),6);
  } else out.println(F("GPS unavailable (no fresh fix)."));
}
void writeMessage(Stream &out) {
  out.println(F("DEMO ONLY - possible incident (unverified)."));
  out.println(F("No emergency service contacted."));
  emitLocation(out);
}
void notifyMockOrTestSMS() {
#if ENABLE_REAL_SMS
  // LAB TEST ONLY. Confirmations and modem resilience not implemented.
  gsmSerial.listen();
  gsmSerial.println(F("AT"));delay(600);
  gsmSerial.println(F("AT+CMGF=1"));delay(600);
  gsmSerial.print(F("AT+CMGS=\""));
  gsmSerial.print(F(SMS_RECIPIENT_NUMBER));
  gsmSerial.println('"');delay(600);
  writeMessage(gsmSerial);
  gsmSerial.write((uint8_t)26);delay(2000);
  gpsSerial.listen();
  Serial.println(F("TEST SMS command sent; delivery NOT confirmed."));
#else
  Serial.println(F("[MOCK ONLY] No SMS was transmitted."));
  writeMessage(Serial);
#endif
}
void setup() {
  Serial.begin(9600);
  pinMode(CANCEL_BUTTON, INPUT_PULLUP);pinMode(STATUS_LED, OUTPUT);
  lcd.begin(16,2);
  gpsSerial.begin(9600);gsmSerial.begin(9600);
  gpsSerial.listen();
  calibrateReference();
  showStatus(F("Monitoring"), F("TEST MODE"));
  Serial.println(F("Educational prototype only: SMS disabled by default."));
}
void loop() {
  while(gpsSerial.available()>0) gps.encode(gpsSerial.read());
  unsigned long now=millis();
  if(state==MONITORING && now-lastSampleMs>=SENSOR_PERIOD_MS) {
    lastSampleMs=now;
    if(candidateShock()) {
      state=COUNTDOWN;triggeredAtMs=now;
      digitalWrite(STATUS_LED,HIGH);
      showStatus(F("Impact candidate"), F("Press D12 cancel"));
      Serial.println(F("Impact candidate (NOT confirmed crash)."));
    }
  }
  if(state==COUNTDOWN) {
    if(digitalRead(CANCEL_BUTTON)==LOW) {
      state=CANCELLED;resetAtMs=now;
      digitalWrite(STATUS_LED,LOW);
      showStatus(F("Alert cancelled"), F("TEST MODE"));
      Serial.println(F("Simulated alert cancelled."));
    } else if(now-triggeredAtMs>=CANCEL_WINDOW_MS) {
      state=DONE;resetAtMs=now;
      showStatus(F("Mock alert"), F("Serial output"));
      notifyMockOrTestSMS();
    }
  }
  if((state==DONE || state==CANCELLED) && now-resetAtMs>=COOLDOWN_MS) {
    state=MONITORING;shockStreak=0;
    digitalWrite(STATUS_LED,LOW);gpsSerial.listen();
    showStatus(F("Monitoring"), F("TEST MODE"));
  }
}
