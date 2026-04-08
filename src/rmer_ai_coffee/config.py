from __future__ import annotations
import os
import tomllib
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "drivers": {
        "pump": "mock",
        "heater": "mock",
        "valve": "mock",
        "temp_sensor": "mock",
    },
    "service": {"host": "0.0.0.0", "port": 8000},
}


def get_default_hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))


def load_config(path: str | None = None) -> Dict[str, Any]:
    """Load config from TOML file or return defaults.

    The loader looks for (in order):
    - explicit `path` argument
    - $HERMES_HOME/ai-coffee-machine.toml
    - ./ai-coffee-machine.toml
    - defaults
    """
    paths = []
    if path:
        paths.append(Path(path))
    hermes_home = get_default_hermes_home()
    paths.append(hermes_home / "ai-coffee-machine.toml")
    paths.append(Path.cwd() / "ai-coffee-machine.toml")

    for p in paths:
        try:
            if p.exists():
                with p.open("rb") as fh:
                    data = tomllib.load(fh)
                return data
        except Exception:
            # ignore parse errors and continue to defaults
            pass

    # Fallback to environment-driven simple config
    cfg = DEFAULT_CONFIG.copy()
    # allow overriding driver names via env vars like DRIVER_PUMP=real_gpio
    drivers = cfg.setdefault("drivers", {})
    for k in list(drivers.keys()):
        env_key = f"DRIVER_{k.upper()}"
        if env_key in os.environ:
            drivers[k] = os.environ[env_key]
    return cfg
