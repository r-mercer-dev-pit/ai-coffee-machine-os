from rmer_ai_coffee.hal.registry import HALRegistry


def test_register_factory_and_get():
    hal = HALRegistry()
    hal.register_factory("pump", lambda: "pump_instance")
    assert hal.get("pump") == "pump_instance"
    # second get returns same instance
    assert hal.get("pump") == "pump_instance"
