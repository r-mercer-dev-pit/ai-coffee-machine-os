import pytest
from rmer_ai_coffee.hal.mock import MockPump, MockHeater, MockValve, MockTempSensor

def test_mock_pump():
    p = MockPump()
    assert not p.running
    p.start()
    assert p.running
    p.stop()
    assert not p.running

def test_mock_heater():
    h = MockHeater()
    h.set_temperature(90.0)
    assert h.temp == 90.0

def test_temp_sensor():
    s = MockTempSensor()
    t = s.read_celsius()
    assert isinstance(t, float)
