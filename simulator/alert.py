"""Safe synthetic incident-monitoring demo; never sends SMS or emergency requests."""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass(frozen=True)
class AccelerationSample:
    time_s: float
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class GPSFix:
    latitude: float
    longitude: float
    speed_kmh: float = 0.0
    valid: bool = True


class AlertState(str, Enum):
    MONITORING = "MONITORING"
    COUNTDOWN = "COUNTDOWN"
    MOCK_ALERT = "MOCK_ALERT"
    CANCELLED = "CANCELLED"


class ImpactDetector:
    """Toy persistent-deviation detector, NOT validated crash detection."""
    def __init__(self, reference=(0, 0, 1), delta_threshold_g=1.7, consecutive_samples=3):
        if delta_threshold_g <= 0 or consecutive_samples < 1:
            raise ValueError("Invalid detection configuration")
        self.reference = reference
        self.delta_threshold_g = delta_threshold_g
        self.consecutive_samples = consecutive_samples
        self._streak = 0

    def observe(self, sample: AccelerationSample) -> bool:
        readings = (sample.x, sample.y, sample.z)
        if not all(math.isfinite(v) for v in readings):
            self._streak = 0
            return False
        magnitude = math.sqrt(sum((v-r)**2 for v, r in zip(readings, self.reference)))
        self._streak = self._streak + 1 if magnitude >= self.delta_threshold_g else 0
        return self._streak >= self.consecutive_samples


def nmea_to_decimal(field: str, hemisphere: str, *, latitude: bool) -> float:
    n = 2 if latitude else 3
    if len(field) < n+2 or (hemisphere not in ("N","S") if latitude else hemisphere not in ("E","W")):
        raise ValueError("Invalid NMEA coordinate")
    degrees = int(field[:n])
    minutes = float(field[n:])
    if not 0 <= minutes < 60:
        raise ValueError("Invalid NMEA minutes")
    value = degrees + minutes / 60.0
    if value > (90 if latitude else 180):
        raise ValueError("Coordinate out of range")
    return -value if hemisphere in ("S", "W") else value


def parse_rmc(sentence: str) -> GPSFix:
    if not sentence.startswith("$") or "*" not in sentence:
        raise ValueError("Expected checksummed NMEA sentence")
    payload, raw_checksum = sentence.strip()[1:].rsplit("*", 1)
    checksum = int(raw_checksum, 16)
    computed = 0
    for c in payload:
        computed ^= ord(c)
    if checksum != computed:
        raise ValueError("NMEA checksum mismatch")
    fields = payload.split(",")
    if len(fields) < 8 or fields[0] not in ("GPRMC", "GNRMC"):
        raise ValueError("Expected GPS RMC sentence")
    if fields[2] != "A":
        raise ValueError("GPS fix unavailable")
    return GPSFix(nmea_to_decimal(fields[3], fields[4], latitude=True),
                  nmea_to_decimal(fields[5], fields[6], latitude=False),
                  float(fields[7] or "0") * 1.852)


def alert_message(fix: GPSFix | None) -> str:
    prefix = "DEMO ONLY — simulated vehicle incident. NO emergency service notified."
    if not fix or not fix.valid:
        return f"{prefix} GPS unavailable; location cannot be provided."
    return (f"{prefix} Location: {fix.latitude:.6f}, {fix.longitude:.6f}; "
            f"https://www.google.com/maps?q={fix.latitude:.6f},{fix.longitude:.6f}")


class AlertController:
    def __init__(self, countdown_s=10.0):
        if countdown_s <= 0:
            raise ValueError("Countdown must be positive")
        self.countdown_s = countdown_s
        self.state = AlertState.MONITORING
        self.deadline_s = None
        self.message = None

    def update(self, now_s, *, impact=False, cancel=False, gps_fix=None):
        if self.state == AlertState.MONITORING and impact:
            self.state = AlertState.COUNTDOWN
            self.deadline_s = now_s + self.countdown_s
        if self.state == AlertState.COUNTDOWN:
            if cancel:
                self.state = AlertState.CANCELLED
            elif now_s >= self.deadline_s:
                self.message = alert_message(gps_fix)
                self.state = AlertState.MOCK_ALERT
        return self.state


def demo_samples():
    return [AccelerationSample(float(t), 2.9 if 8 <= t <= 11 else 0.04*math.sin(t/3),
                               0.02, 1.0) for t in range(25)]


def run_demo(*, cancel=False, output_csv: Path | None=None):
    detector = ImpactDetector()
    controller = AlertController(countdown_s=10)
    fix = GPSFix(0.0, 0.0)  # synthetic example; not a real incident location
    timeline = []
    for sample in demo_samples():
        triggered = detector.observe(sample)
        state = controller.update(sample.time_s, impact=triggered,
                                  cancel=cancel and sample.time_s == 15, gps_fix=fix)
        timeline.append({"time_s":sample.time_s, "x_g":round(sample.x,3),
                         "y_g":sample.y, "z_g":sample.z,
                         "impact_candidate":triggered, "state":state.value})
    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        with output_csv.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=timeline[0].keys())
            writer.writeheader()
            writer.writerows(timeline)
    return {"state":controller.state.value, "message":controller.message,
            "samples":len(timeline), "events":timeline}


def main():
    parser = argparse.ArgumentParser(description="Safe synthetic incident alert simulator")
    parser.add_argument("--cancel", action="store_true")
    parser.add_argument("--csv", default="outputs/demo_trace.csv")
    args = parser.parse_args()
    result = run_demo(cancel=args.cancel, output_csv=Path(args.csv))
    print(json.dumps({k:v for k,v in result.items() if k!="events"}, indent=2))


if __name__ == "__main__":
    main()
