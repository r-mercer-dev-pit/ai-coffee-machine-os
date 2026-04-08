from .base import PumpInterface, HeaterInterface, ValveInterface, TemperatureSensorInterface

class MockPump(PumpInterface):
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

class MockHeater(HeaterInterface):
    def __init__(self):
        self.temp = 20.0

    def set_temperature(self, temp_c: float):
        self.temp = temp_c

class MockValve(ValveInterface):
    def __init__(self):
        self.opened = False

    def open(self):
        self.opened = True

    def close(self):
        self.opened = False

class MockTempSensor(TemperatureSensorInterface):
    def read_celsius(self) -> float:
        return 25.0
