"""Simple in-process plugin registry for metadata and discovery helpers.

This is a lightweight helper used by the HAL plugin loader to track loaded
plugin metadata (name, version, entrypoint, description). It is intentionally
small and testable — production systems may replace this with a persisted
registry or service discovery.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional, List


@dataclass
class PluginMeta:
    name: str
    version: str = "0.0.0"
    entrypoint: Optional[str] = None
    description: Optional[str] = None


class PluginRegistry:
    def __init__(self):
        self._store: Dict[str, PluginMeta] = {}

    def register(self, meta: PluginMeta) -> None:
        if not meta.name:
            raise ValueError("plugin meta must include a name")
        self._store[meta.name] = meta

    def unregister(self, name: str) -> None:
        self._store.pop(name, None)

    def get(self, name: str) -> Optional[PluginMeta]:
        return self._store.get(name)

    def list(self) -> List[PluginMeta]:
        return list(self._store.values())

    def as_dict(self) -> Dict[str, dict]:
        return {k: asdict(v) for k, v in self._store.items()}


__all__ = ["PluginMeta", "PluginRegistry"]
