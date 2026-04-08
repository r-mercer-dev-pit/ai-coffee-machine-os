from typing import Callable, Any
from .base import HardwareRegistry

class HALRegistry(HardwareRegistry):
    def __init__(self):
        super().__init__()

    def register_factory(self, name: str, factory: Callable[[], Any]):
        # Register a lazy factory; instantiate on get
        self.components[name] = factory

    def get(self, name: str):
        v = self.components.get(name)
        if callable(v):
            inst = v()
            self.components[name] = inst
            return inst
        return v
