# SBC Testing & Deployment Plan

Version: 2026-04-08
Author: Hermes Agent
Repository: r-mercer-dev-pit/ai-coffee-machine-os

Purpose
-------
This plan describes the end-to-end work required to take the current project skeleton to a state where it can be tested and validated on a single-board computer (SBC). It covers feature requirements, development tasks, testing strategy (unit, integration, hardware-in-the-loop), delivery (systemd/docker), security considerations, and acceptance criteria.

Scope & Assumptions
-------------------
- Target SBCs: Raspberry Pi family (Raspberry Pi OS / Debian), Odroid, similar ARM single-board Linux devices.
- Hardware specifics (pump/heater/valves/sensors) are NOT yet available. Development will follow a mock-first strategy and a clearly-defined HAL so drivers can be added later.
- Primary language: Python 3.11 for high-level logic. Low-level drivers may be written in Rust with Python bindings (maturin) where performance/safety is required.
- Network connectivity: MQTT and REST (FastAPI) interfaces supported.

High-level goals
----------------
1. Define and stabilize the HAL and plugin model so core logic runs identically with mocks and with real drivers.
2. Implement an asyncio-based service runner and a minimal brew sequence verified via tests.
3. Provide local deployment options: systemd unit for SBCs and docker-compose for development/testing.
4. Provide a test matrix (unit, integration, HIL) and CI automation to run on GitHub Actions.
5. Provide a Rust driver scaffold with instructions to build Python bindings for SBCs.
6. Provide documentation and checklists to provision an SBC, deploy, test, and rollback.

Design principles
-----------------
- Mock-first: every hardware interface must have a mock implementation and unit tests that exercise logic without hardware.
- TDD: implement features via tests first (unit -> integration -> HIL).
- Small, frequent commits on feature branches; PRs for review and CI validation before merge to main.
- Least privilege for credentials; no secrets in repo. Recommend Vault/gopass for production secrets.
- Observable: include logging, health endpoints, and simple telemetry (status, errors).

Deliverables
------------
- HAL API spec (Python ABCs) and mock drivers (already present)
- HAL plugin loader and config-driven registration
- BrewController with a tested simple brew flow (mocked)
- FastAPI REST endpoints and optional minimal web UI for status and commands
- Systemd unit template and install script for SBCs
- Dockerfile + docker-compose for local testing
- Rust driver scaffold (drivers/rust_driver_template) with build & binding instructions (maturin)
- Integration tests and a HIL test harness to run on an SBC (uses mock vs live toggles)
- CI pipeline updates: run unit tests, ruff lint, build wheel, and optionally run a QEMU-based ARM test step (optional)
- Docs: ARCHITECTURE.md, HACKING.md, SBC_PROVISIONING.md, TESTING.md

Milestones & Tasks (detailed)
-----------------------------
Milestone 0 — Project hygiene (done)
- Verify repo skeleton, devcontainer, CI present. (Done)

Milestone 1 — HAL plugin loader & config (TDD)
- Task 1.1: Add config file loader
  - File: src/rmer_ai_coffee/config.py
  - Behavior: load YAML/ENV config, profile-aware HERMES_HOME support
- Task 1.2: Implement plugin registry
  - File: src/rmer_ai_coffee/hal/registry.py
  - Tests: tests/test_hal_registry.py
- Task 1.3: Add runtime loader that reads config and registers drivers (mock by default)
  - File: src/rmer_ai_coffee/core/bootstrap.py

Milestone 2 — Service orchestration & gracefulness
- Task 2.1: Harden ServiceRunner with start/stop lifecycle, health checks, and signal handlers
  - File: src/rmer_ai_coffee/core/app.py (expand)
  - Tests: tests/test_service_runner.py
- Task 2.2: Add health and readiness endpoints to REST API
  - File: src/rmer_ai_coffee/connectivity/rest_api.py

Milestone 3 — Brew flows and state machine
- Task 3.1: Formalize brew sequences as composable steps
  - File: src/rmer_ai_coffee/services/sequence.py
  - Tests: tests/test_brew_sequences.py (TDD for timing/ordering)
- Task 3.2: Add scheduler and safe-shutdown behavior

Milestone 4 — Packaging & SBC deployment artifacts
- Task 4.1: Add Dockerfile and docker-compose for local dev
  - Files: Dockerfile, docker/docker-compose.yml
- Task 4.2: Add systemd unit template and install script
  - Files: scripts/systemd/ai-coffee-machine.service, scripts/install_on_sbc.sh
- Task 4.3: Add cross-build or build instructions for wheels on ARM (manylinux/ABI notes)

Milestone 5 — Rust driver scaffold & bindings
- Task 5.1: Create drivers/rust_driver_template Cargo project
  - Files: drivers/rust_driver_template/Cargo.toml, src/lib.rs
- Task 5.2: Add maturin packaging example to build Python wheel and expose simple Pump API
  - Files: drivers/rust_driver_template/README.md, build instructions in docs
- Task 5.3: Add CI job (optional) to build wheels for linux-aarch64 using GitHub Actions matrix or cross toolchains

Milestone 6 — Integration & Hardware-in-the-loop (HIL) tests
- Task 6.1: Create HIL test harness that can be run on an SBC to exercise hardware drivers while optionally logging to a test collector.
  - Files: tests/hil/run_hil.py, scripts/hil_runner.sh
- Task 6.2: Define gating tests (smoke tests) for safe hardware operations e.g., only run pump for X seconds, check sensor feedback
- Task 6.3: Add safety interlocks: emergency-stop, watchdog timers, maximum durations

Milestone 7 — CI and release pipeline
- Task 7.1: Extend CI to run unit tests and linters across matrix (3.11, 3.10). Add ruff/black/isort checks.
- Task 7.2: Add semantic-release style tagging (manual) and GitHub Actions job to build and publish artifacts to GitHub Releases (draft) for manual download on SBC.

Milestone 8 — Documentation and onboarding
- Task 8.1: Write SBC_PROVISIONING.md (image flash, network config, systemd install, verifying services)
- Task 8.2: Write TESTING.md with instructions to run unit, integration and HIL tests
- Task 8.3: ARCHITECTURE.md capturing HAL contract and plugin lifecycle

Testing strategy
----------------
- Unit tests: TDD, pure-Python, use mocks for hardware. Run on CI for every PR.
- Integration tests: combine REST + service runner + mocked HAL (use pytest-asyncio). Run on CI and locally via docker-compose.
- Hardware-in-the-loop (HIL): tests that run on an SBC with a true driver. These are gated and executed manually or via a scheduled runner; they require operator confirmation and safety checks.
- Safety tests: check that any test that would actuate hardware requires an explicit env var like HIL_RUN=1 and will abort if not present.

Mock hardware integration
-------------------------
- Keep mock implementations in src/rmer_ai_coffee/hal/mock.py and expand to simulate sensor drift, partial failures, and timing jitter.
- Provide a "mock harness" script (scripts/run_with_mocks.sh) that starts the service runner with mock drivers and exposes the REST UI for QA.
- Tests should include randomized property-based tests for edge conditions (pytest + hypothesis optional).

Security & secrets
------------------
- Never store secrets in git. Use environment variables for local dev and recommend HashiCorp Vault or gopass in production.
- Document the minimal TLS and authentication requirements for MQTT and REST.
- Provide steps for provisioning device credentials on first boot (see SBC_PROVISIONING.md).

Acceptance criteria
-------------------
The project is ready for SBC testing when all of the following are true:
1. HAL interfaces are stable and covered by unit tests (>=80% coverage for core modules).
2. A simple brew flow can be triggered via REST and completes successfully against mock drivers (CI green).
3. Docker-compose allows reproducing the service on a developer machine.
4. Systemd unit installed on an SBC can start the service and the service responds to /status and /health endpoints.
5. Rust driver scaffold builds into a Python wheel on an SBC (or via cross-build) and a minimal smoke integration test can call the driver safely.
6. Documentation: ARCHITECTURE.md, SBC_PROVISIONING.md, and TESTING.md exist and are reviewed.

Execution plan & branch workflow
-------------------------------
- Use feature branches for every milestone: feat/hal-plugin-loader, feat/service-lifecycle, feat/rust-drivers, etc.
- PR checklist (required): tests, changelog entry (if featureful), docs updated, CI green, at least one reviewer.
- Merge strategy: squash commits into main after PR approval.

Safety & rollback
-----------------
- When running HIL tests, always have a hardware kill-switch and ensure scripts respect MAX_ACTUATION_SECONDS env var.
- Provide a simple rollback: stop systemd service, rollback package (pip uninstall / install previous wheel), bring up service.

Next immediate actions I can take (pick one)
-------------------------------------------
1. Create HAL registry and bootstrap (feat/hal-plugin-loader) and open a PR.
2. Add Dockerfile + docker-compose and scripts for local testing (feat/docker-local).
3. Scaffold Rust driver template and add build instructions (feat/rust-drivers).
4. Create DOCUMENTATION files (ARCHITECTURE.md, SBC_PROVISIONING.md, TESTING.md) and save them in docs/ (I will do this and open a PR).

Plan saved to: docs/plans/sbc-deployment-plan.md

If you want, I will now create a feature branch, commit this plan, and open a PR for review. Which immediate action should I take next?