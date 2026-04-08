from fastapi import FastAPI
from ..core.app import ServiceRunner
from ..hal.base import HardwareRegistry
from ..services.brew_controller import BrewController

app = FastAPI()
# Use bootstrap to load configured drivers (mock by default)
from ..core.bootstrap import bootstrap_from_config

runner = ServiceRunner()

@app.on_event("startup")
async def startup_event():
    hal = bootstrap_from_config()
    runner.hal = hal
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
