from ..config import load_config
from ..hal.registry import HALRegistry


def bootstrap_from_config(path: str | None = None) -> HALRegistry:
    cfg = load_config(path)
    hal = HALRegistry()
    drivers = cfg.get("drivers", {})
    for logical_name, driver_name in drivers.items():
        # dynamic import strategy: try students of rmer_ai_coffee.hal.<driver_name>
        mod_name = f"rmer_ai_coffee.hal.{driver_name}"
        try:
            mod = __import__(mod_name, fromlist=["*"])
            factory = getattr(mod, "get_factory", None)
            if callable(factory):
                hal.register_factory(logical_name, factory)
                continue
        except Exception:
            pass
        # Fallback to direct mapping for built-in mock
        if driver_name == "mock":
            from ..hal.mock import MockPump, MockHeater, MockValve, MockTempSensor

            mapping = {
                "pump": lambda: MockPump(),
                "heater": lambda: MockHeater(),
                "valve": lambda: MockValve(),
                "temp_sensor": lambda: MockTempSensor(),
            }
            if logical_name in mapping:
                hal.register_factory(logical_name, mapping[logical_name])
    return hal
