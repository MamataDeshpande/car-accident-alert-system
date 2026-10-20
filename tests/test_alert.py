"""Unit tests for mock-only vehicle incident monitoring."""
import tempfile
import unittest
from pathlib import Path
from simulator.alert import (
    AccelerationSample, AlertController, AlertState, GPSFix, ImpactDetector,
    alert_message, nmea_to_decimal, parse_rmc, run_demo
)


class ImpactTests(unittest.TestCase):
    def test_no_false_candidate_in_normal_trace(self):
        detector = ImpactDetector()
        self.assertFalse(any(detector.observe(AccelerationSample(t,.03,0,1)) for t in range(7)))

    def test_requires_three_consecutive_samples(self):
        detector = ImpactDetector()
        self.assertFalse(detector.observe(AccelerationSample(0,3,0,1)))
        self.assertFalse(detector.observe(AccelerationSample(1,3,0,1)))
        self.assertTrue(detector.observe(AccelerationSample(2,3,0,1)))

    def test_invalid_sensor_data_resets_streak(self):
        detector = ImpactDetector()
        detector.observe(AccelerationSample(0,3,0,1))
        self.assertFalse(detector.observe(AccelerationSample(1,float("nan"),0,1)))
        self.assertFalse(detector.observe(AccelerationSample(2,3,0,1)))


class GPSTests(unittest.TestCase):
    def test_nmea_coordinate_conversion(self):
        self.assertAlmostEqual(nmea_to_decimal("4807.038","N",latitude=True),48.1173)
        self.assertAlmostEqual(nmea_to_decimal("01131.000","W",latitude=False),-11.5166666667)

    def test_parse_valid_rmc(self):
        fix=parse_rmc("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A")
        self.assertAlmostEqual(fix.latitude,48.1173)
        self.assertAlmostEqual(fix.longitude,11.5166666667)
        self.assertAlmostEqual(fix.speed_kmh,22.4*1.852)

    def test_bad_checksum_rejected(self):
        with self.assertRaises(ValueError):
            parse_rmc("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*00")

    def test_no_fix_rejected(self):
        payload="GPRMC,123519,V,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W"
        checksum=0
        for c in payload:
            checksum^=ord(c)
        with self.assertRaises(ValueError):
            parse_rmc(f"${payload}*{checksum:02X}")

    def test_missing_fix_keeps_message_explicit(self):
        self.assertIn("GPS unavailable",alert_message(None))


class StateMachineTests(unittest.TestCase):
    def test_alert_only_after_countdown(self):
        controller=AlertController(10)
        self.assertEqual(controller.update(2,impact=True),AlertState.COUNTDOWN)
        self.assertEqual(controller.update(11),AlertState.COUNTDOWN)
        self.assertEqual(controller.update(12,gps_fix=GPSFix(0,0)),AlertState.MOCK_ALERT)
        self.assertIn("DEMO ONLY",controller.message)

    def test_cancel_blocks_alert(self):
        controller=AlertController(10)
        controller.update(1,impact=True)
        self.assertEqual(controller.update(3,cancel=True),AlertState.CANCELLED)
        self.assertEqual(controller.update(40),AlertState.CANCELLED)
        self.assertIsNone(controller.message)

    def test_demo_creates_trace(self):
        with tempfile.TemporaryDirectory() as folder:
            destination=Path(folder)/"trace.csv"
            result=run_demo(output_csv=destination)
            self.assertTrue(destination.exists())
            self.assertEqual(result["state"],AlertState.MOCK_ALERT.value)
            self.assertEqual(result["samples"],25)

    def test_demo_cancellation(self):
        result=run_demo(cancel=True)
        self.assertEqual(result["state"],AlertState.CANCELLED.value)
        self.assertIsNone(result["message"])


if __name__=="__main__":
    unittest.main()
