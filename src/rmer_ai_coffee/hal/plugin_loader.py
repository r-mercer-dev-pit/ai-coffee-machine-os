"""HAL plugin loader with discovery, load, unload and simple registry integration.

This loader will attempt to register plugin metadata with an in-memory
PluginRegistry when a loaded module exposes PLUGIN_META (dict) or
PLUGIN_NAME (string) plus optional version/description.
"""
from __future__ import annotations

from importlib import import_module
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import List, Optional

from .registry import PluginRegistry, PluginMeta


class PluginLoadError(RuntimeError):
    pass


class PluginLoader:
    def __init__(self, config: Optional[dict] = None, registry: Optional[PluginRegistry] = None):
        self.config = config or {}
        self._loaded: dict[str, ModuleType] = {}
        # registry to track plugin metadata
        self.registry = registry or PluginRegistry()
        # mapping plugin_name -> registered_name in registry
        self._registered_names: dict[str, str] = {}

    def discover(self, paths: List[str]) -> List[str]:
        found: List[str] = []
        for p in paths:
            base = Path(p)
            if not base.exists():
                continue
            for child in sorted(base.iterdir()):
                if child.is_file() and child.name.endswith("_plugin.py"):
                    found.append(child.stem)
                if child.is_dir() and (child / "__init__.py").exists():
                    found.append(child.name)
        return found

    def _find_file_for(self, name: str, paths: List[str]) -> Optional[Path]:
        target_file = f"{name}.py" if name.endswith("_plugin") else f"{name}_plugin.py"
        for p in paths:
            base = Path(p)
            f = base / target_file
            if f.exists() and f.is_file():
                return f
            pkg = base / name
            if pkg.exists() and (pkg / "__init__.py").exists():
                return pkg
        return None

    def _maybe_register(self, plugin_name: str, module: ModuleType) -> None:
        """Attempt to extract metadata from module and register it."""
        meta_dict = None
        if hasattr(module, "PLUGIN_META") and isinstance(getattr(module, "PLUGIN_META"), dict):
            meta_dict = getattr(module, "PLUGIN_META")
        elif hasattr(module, "PLUGIN_NAME"):
            meta_dict = {"name": getattr(module, "PLUGIN_NAME")}
            # optional fields
            if hasattr(module, "PLUGIN_VERSION"):
                meta_dict["version"] = getattr(module, "PLUGIN_VERSION")
            elif hasattr(module, "__version__"):
                meta_dict["version"] = getattr(module, "__version__")
            if hasattr(module, "PLUGIN_DESCRIPTION"):
                meta_dict["description"] = getattr(module, "PLUGIN_DESCRIPTION")
            if hasattr(module, "PLUGIN_ENTRYPOINT"):
                meta_dict["entrypoint"] = getattr(module, "PLUGIN_ENTRYPOINT")

        if not meta_dict:
            return

        # Build PluginMeta; if name missing, PluginRegistry.register will raise
        name_to_register = meta_dict.get("name") or plugin_name
        meta = PluginMeta(
            name=name_to_register,
            version=str(meta_dict.get("version")) if meta_dict.get("version") is not None else "0.0.0",
            entrypoint=meta_dict.get("entrypoint"),
            description=meta_dict.get("description"),
        )
        try:
            self.registry.register(meta)
            self._registered_names[plugin_name] = name_to_register
        except Exception as exc:
            raise PluginLoadError(f"Failed to register plugin metadata for {plugin_name}: {exc}") from exc

    def load(self, name: str, paths: Optional[List[str]] = None) -> ModuleType:
        if name in self._loaded:
            return self._loaded[name]
        search_paths = paths or [str(Path.cwd())]
        p = self._find_file_for(name, search_paths)
        if p is None:
            raise PluginLoadError(f"Plugin {name} not found in paths={search_paths}")
        try:
            if p.is_dir():
                parent = str(p.parent)
                if parent not in sys.path:
                    sys.path.insert(0, parent)
                module = import_module(p.name)
            else:
                mod_name = f"rmer_ai_coffee_plugins.{name}"
                spec = importlib.util.spec_from_file_location(mod_name, str(p))
                if spec is None or spec.loader is None:
                    raise PluginLoadError(f"Cannot create module spec for {p}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module
                spec.loader.exec_module(module)  # type: ignore[arg-type]
            self._loaded[name] = module
            # try to register metadata if present
            self._maybe_register(name, module)
            return module
        except Exception as exc:
            raise PluginLoadError(f"Failed to load plugin {name}: {exc}") from exc

    def unload(self, name: str) -> None:
        # unregister if previously registered
        reg_name = self._registered_names.pop(name, None)
        if reg_name is not None:
            try:
                self.registry.unregister(reg_name)
            except Exception:
                pass
        mod = self._loaded.pop(name, None)
        if mod is None:
            return
        to_remove = [k for k, v in list(sys.modules.items()) if v is mod or k.startswith(f"rmer_ai_coffee_plugins.{name}")]
        for k in to_remove:
            try:
                del sys.modules[k]
            except KeyError:
                pass

    def get_loaded(self) -> dict[str, ModuleType]:
        return dict(self._loaded)


__all__ = ["PluginLoader", "PluginLoadError"]
