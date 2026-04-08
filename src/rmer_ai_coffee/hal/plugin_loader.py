"""HAL plugin loader with discovery, load, unload and simple registry.

Discovery rule: file '*_plugin.py' or package dir with '__init__.py'.

This loader assigns a stable module name under the prefix
'rmer_ai_coffee_plugins.<name>' when importing file-based plugins so that
unload can clean up sys.modules reliably.
"""
from __future__ import annotations

from importlib import import_module
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import List, Optional


class PluginLoadError(RuntimeError):
    pass


class PluginLoader:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._loaded: dict[str, ModuleType] = {}

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
                # Use a consistent module name in the spec so loaders work correctly
                mod_name = f"rmer_ai_coffee_plugins.{name}"
                spec = importlib.util.spec_from_file_location(mod_name, str(p))
                if spec is None or spec.loader is None:
                    raise PluginLoadError(f"Cannot create module spec for {p}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module
                spec.loader.exec_module(module)  # type: ignore[arg-type]
            self._loaded[name] = module
            return module
        except Exception as exc:
            raise PluginLoadError(f"Failed to load plugin {name}: {exc}") from exc

    def unload(self, name: str) -> None:
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
