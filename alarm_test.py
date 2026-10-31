import unittest
from alarm_utils import check_alarms


class TestMotorAlarms(unittest.TestCase):

    def test_normal_operation(self):
        alarms = check_alarms(1.5, 30.0, 1450.0)
        self.assertEqual(alarms, [])

    def test_high_current(self):
        alarms = check_alarms(2.8, 30.0, 1450.0)
        self.assertEqual(alarms, ["HIGH_CURRENT"])

    def test_high_temperature(self):
        alarms = check_alarms(1.5, 42.0, 1450.0)
        self.assertEqual(alarms, ["HIGH_TEMPERATURE"])

    def test_low_speed(self):
        alarms = check_alarms(1.5, 30.0, 1200.0)
        self.assertEqual(alarms, ["LOW_SPEED"])


if __name__ == "__main__":
    unittest.main()
