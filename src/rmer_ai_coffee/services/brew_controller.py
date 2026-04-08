import asyncio
from ..hal.base import HardwareRegistry

class BrewController:
    def __init__(self, hal: HardwareRegistry):
        self.hal = hal

    async def simple_brew(self):
        pump = self.hal.get("pump")
        heater = self.hal.get("heater")
        valve = self.hal.get("valve")
        sensor = self.hal.get("temp_sensor")

        # Example brew sequence (mocked)
        heater.set_temperature(92.0)
        await asyncio.sleep(0.2)
        pump.start()
        await asyncio.sleep(0.5)
        valve.open()
        await asyncio.sleep(0.2)
        valve.close()
        pump.stop()
        return {"status": "done", "temp": sensor.read_celsius()}
