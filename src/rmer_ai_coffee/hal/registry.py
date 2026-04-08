from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .base import HardwareRegistry


@dataclass
class PluginMeta:
    name: str
    version: str
    entrypoint: str
    description: str = ""


class PluginRegistry(HardwareRegistry):
    """Registry storing PluginMeta objects keyed by plugin name."""

    def __init__(self):
        super().__init__()

    def register(self, meta: PluginMeta) -> None:
        self.components[meta.name] = meta

    def unregister(self, name: str) -> None:
        self.components.pop(name, None)

    def get(self, name: str):
        return self.components.get(name)

    def list(self) -> List[PluginMeta]:
        return list(self.components.values())

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.components.items()}

# Backwards-compat alias used by other tests
HALRegistry = PluginRegistry
