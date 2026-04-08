"""HAL plugin loader with optional on-disk discovery and PLUGIN_META registration.

This loader supports two load paths:
  - import by module name (importlib.import_module)
  - load from files under provided paths (file.py, file_plugin.py, or package)

When a loaded module exposes PLUGIN_META (a dict with at least the 'name' key)
that metadata is registered into an internal PluginRegistry instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module, util
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional

from .registry import PluginRegistry, PluginMeta


class PluginLoadError(Exception):
    """Raised when a plugin cannot be loaded or its metadata is invalid."""


@dataclass
class LoadedPlugin:
    name: str
    module: ModuleType
    path: str


class PluginLoader:
    """Discover and load plugin modules from filesystem paths.

    Behavior:
      - discover(paths) -> list of plugin candidate names
      - load(name, paths=None) -> loads by import name or from files under provided paths
      - when a module exposes PLUGIN_META (a dict with at least 'name'), the loader
        registers that metadata in an internal PluginRegistry instance.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.plugins: Dict[str, LoadedPlugin] = {}
        self.registry = PluginRegistry()

    def discover(self, paths: List[str]) -> List[str]:
        found: List[str] = []
        for p in paths:
            base = Path(p)
            if not base.exists():
                continue
            for child in base.iterdir():
                if child.is_file() and child.name.endswith("_plugin.py"):
                    found.append(child.stem)
                elif child.is_dir() and (child / "__init__.py").exists():
                    found.append(child.name)
        return found

    def _maybe_register_meta(self, module: ModuleType) -> None:
        meta = getattr(module, "PLUGIN_META", None)
        if meta is None:
            return
        if not isinstance(meta, dict) or "name" not in meta:
            raise PluginLoadError("PLUGIN_META missing required 'name' key")
        pm = PluginMeta(
            name=str(meta["name"]),
            version=str(meta.get("version", "")),
            entrypoint=str(meta.get("entrypoint", "")),
            description=str(meta.get("description", "")),
        )
        self.registry.register(pm)

    def load(self, name: str, paths: Optional[List[str]] = None) -> LoadedPlugin:
        """Load plugin by module name or by searching provided filesystem paths.

        Returns LoadedPlugin on success or raises PluginLoadError.
        """
        if name in self.plugins:
            return self.plugins[name]

        # Try normal import first
        try:
            module = import_module(name)
            lp = LoadedPlugin(name=name, module=module, path=getattr(module, "__file__", ""))
            self.plugins[name] = lp
            try:
                self._maybe_register_meta(module)
            except PluginLoadError:
                # metadata invalid -> surface as error
                raise
            except Exception:
                # ignore non-fatal metadata parsing issues
                pass
            return lp
        except Exception:
            # fallthrough to filesystem-based loading
            if not paths:
                raise PluginLoadError(f"Could not import plugin '{name}' and no paths provided")

        last_exc: Optional[Exception] = None
        for p in paths:
            base = Path(p)
            if not base.exists():
                continue
            file_plugin = base / f"{name}_plugin.py"
            file_candidate = base / f"{name}.py"
            pkg_candidate = base / name
            try:
                spec: Optional[ModuleSpec] = None
                if file_plugin.exists():
                    spec = util.spec_from_file_location(name, str(file_plugin))
                elif file_candidate.exists():
                    spec = util.spec_from_file_location(name, str(file_candidate))
                elif (pkg_candidate / "__init__.py").exists():
                    spec = util.spec_from_file_location(name, str(pkg_candidate / "__init__.py"))

                if spec is None:
                    continue
                module = util.module_from_spec(spec)
                loader = spec.loader
                if loader is None:
                    raise PluginLoadError(f"No loader available for plugin spec {name}")
                loader.exec_module(module)  # type: ignore[attr-defined]
                lp = LoadedPlugin(name=name, module=module, path=getattr(module, "__file__", ""))
                self.plugins[name] = lp
                # register metadata if present (will raise PluginLoadError on bad meta)
                self._maybe_register_meta(module)
                return lp
            except Exception as e:
                last_exc = e
                continue

        raise PluginLoadError(f"Failed to load plugin '{name}': {last_exc}")

    def unload(self, name: str) -> None:
        lp = self.plugins.pop(name, None)
        if lp and lp.module:
            meta = getattr(lp.module, "PLUGIN_META", None)
            if isinstance(meta, dict) and "name" in meta:
                try:
                    self.registry.unregister(meta["name"])
                except Exception:
                    # best-effort unregister
                    pass


# Expose symbols explicitly to avoid partial-name import issues
import sys
_mod = sys.modules.get(__name__)
if _mod is not None:
    try:
        if 'PluginLoadError' in locals():
            setattr(_mod, 'PluginLoadError', locals()['PluginLoadError'])
        if 'LoadedPlugin' in locals():
            setattr(_mod, 'LoadedPlugin', locals()['LoadedPlugin'])
        if 'PluginLoader' in locals():
            setattr(_mod, 'PluginLoader', locals()['PluginLoader'])
    except Exception:
        pass

__all__ = ["PluginLoader", "PluginLoadError", "LoadedPlugin"]
