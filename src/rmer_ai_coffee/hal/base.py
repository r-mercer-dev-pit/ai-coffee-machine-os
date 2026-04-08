from abc import ABC, abstractmethod

class PumpInterface(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

class HeaterInterface(ABC):
    @abstractmethod
    def set_temperature(self, temp_c: float):
        pass

class ValveInterface(ABC):
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

class TemperatureSensorInterface(ABC):
    @abstractmethod
    def read_celsius(self) -> float:
        pass

class HardwareRegistry:
    def __init__(self):
        self.components = {}

    async def initialize_all(self):
        # Initialize registered components if they have async init
        for name, comp in self.components.items():
            init = getattr(comp, "initialize", None)
            if callable(init):
                res = init()
                if hasattr(res, "__await__"):
                    await res

    async def shutdown_all(self):
        for name, comp in self.components.items():
            close = getattr(comp, "close", None)
            if callable(close):
                res = close()
                if hasattr(res, "__await__"):
                    await res

    def register(self, name: str, component):
        self.components[name] = component

    def get(self, name: str):
        return self.components.get(name)
