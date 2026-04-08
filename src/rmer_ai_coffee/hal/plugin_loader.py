"""Simple HAL plugin loader utilities."""
from pathlib import Path
from typing import List

class PluginLoader:
    """Discover plugin modules in provided filesystem paths.

    Discovery rule: any Python file matching '*_plugin.py' or any directory
    containing an '__init__.py' is considered a plugin candidate; returns
    names (stem for files, directory name for packages).
    """
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.plugins: dict[str, str] = {}

    def discover(self, paths: List[str]) -> List[str]:
        found: List[str] = []
        for p in paths:
            base = Path(p)
            if not base.exists():
                continue
            for child in base.iterdir():
                if child.is_file() and child.name.endswith('_plugin.py'):
                    found.append(child.stem)
                if child.is_dir() and (child / '__init__.py').exists():
                    found.append(child.name)
        return found

    def load(self, name: str):
        raise NotImplementedError

    def unload(self, name: str):
        self.plugins.pop(name, None)
