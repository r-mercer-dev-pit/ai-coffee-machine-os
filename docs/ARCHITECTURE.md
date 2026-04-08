AI Coffee Machine OS — Architecture

Overview
--------
This document describes the architecture, data flows, HAL contract, plugin lifecycle, and key design choices for ai-coffee-machine-os. It is a living document; update when interfaces change.

Goals
- Clear hardware abstraction so high-level logic is hardware‑agnostic
- Mock-first development and testability
- Safe-by-default hardware actuation with safety interlocks
- Small footprint to run on SBCs (Python 3.11) and optional Rust drivers for low-level access

High-level components
- Service runner (asyncio): orchestrates services, lifecycle, health, and graceful shutdown.
- HAL (Hardware Abstraction Layer): Python ABC interfaces and a plugin registry. Drivers implement interfaces and register via factory functions.
- Drivers: Mock drivers for development; hardware drivers (Python or Rust + maturin bindings) for SBC deployment.
- Services: BrewController and sequence execution (state machine), scheduler, telemetry/health.
- Connectivity: FastAPI REST endpoints (status, brew), MQTT client for pub/sub, optional WebSocket for UI.
- Packaging & Deployment: systemd unit for SBC, docker-compose for local dev, maturin-built wheels for Rust drivers.

HAL contract
------------
Each logical device (pump, heater, valve, temp_sensor, etc.) is represented by an abstract interface (ABC) under src/rmer_ai_coffee/hal/base.py.

Interface rules:
- Methods must be synchronous unless explicitly documented as async. The registry can call async initialize/shutdown if present.
- Implementations must be safe to call from multiple tasks (document concurrency expectations).
- Drivers expose a get_factory() function that returns a zero-argument factory for the component OR they can rely on config mapping to built-in mocks.

Plugin lifecycle
- Registration: bootstrap reads ai-coffee-machine.toml (or HERMES_HOME), maps logical names to driver names, imports driver modules and calls get_factory() when available.
- Instantiation: HALRegistry stores factory proxies and instantiates on first get() call (lazy instantiation).
- Init/Shutdown: ServiceRunner calls hal.initialize_all() during startup and hal.shutdown_all() during stop.

Driver naming and discovery
- Drivers live under rmer_ai_coffee.hal.<driver_name> (Python) or drivers/<driver_name> for Rust crates that expose Python bindings.
- A driver module should define `get_factory()` returning a callable producing the driver instance.

Safety and actuation policy
- Any operation that actuates hardware (pump.start(), heater.set_temperature(), valve.open()) must be guarded by safety checks in higher-level services.
- Default safety: MAX_ACTUATION_SECONDS, require HIL_RUN=1 environment variable to perform real hardware actuation in tests.

Testing and Mocks
- Mock drivers are under src/rmer_ai_coffee/hal/mock.py and simulate normal and failure modes.
- Tests should never actuate real hardware unless explicitly opting into HIL tests.

Observability
- Expose /status and /health endpoints via REST.
- Log structured JSON messages for key events (startup, shutdown, brew start/stop, exceptions).

Extensibility
- Drivers can be added without changing the core by adding a module exposing get_factory() and updating TOML config or ENV vars.

Notes
- Keep ABCs stable; changing an interface is breaking and must be coordinated with versioning and migration notes.
