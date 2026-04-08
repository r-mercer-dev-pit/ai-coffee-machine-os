from fastapi import FastAPI
from ..core.app import ServiceRunner
from ..hal.base import HardwareRegistry
from ..services.brew_controller import BrewController

app = FastAPI()
runner = ServiceRunner()

@app.on_event("startup")
async def startup_event():
    # register mock components for now
    from ..hal.mock import MockPump, MockHeater, MockValve, MockTempSensor
    runner.hal.register("pump", MockPump())
    runner.hal.register("heater", MockHeater())
    runner.hal.register("valve", MockValve())
    runner.hal.register("temp_sensor", MockTempSensor())
    await runner.start()

@app.on_event("shutdown")
async def shutdown_event():
    await runner.stop()

@app.get("/status")
async def status():
    return {"status": "ok"}

@app.post("/brew")
async def brew():
    bc = BrewController(runner.hal)
    res = await bc.simple_brew()
    return res
