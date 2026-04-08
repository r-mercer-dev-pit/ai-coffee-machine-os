# AI Coffee Machine OS

AI-powered coffee machine operating system skeleton

This repository contains a modular, extensible software stack intended to run on single-board computers (Raspberry Pi, Odroid, etc.) to control an AI-powered coffee machine. It provides:

- A hardware abstraction layer (HAL) with mock drivers for development
- An asyncio-based service runner
- An FastAPI-based REST API skeleton
- Plugin-friendly driver layout; Rust bindings are prepared for low-level drivers
- CI, tests, and development container guidance

Getting started (development)

1. Clone the repo
2. Create and activate a Python 3.11 venv
   python -m venv .venv && source .venv/bin/activate
3. Install dependencies
   pip install -r requirements.txt
4. Run tests
   pytest -q

Contributing

- Use feature branches and open PRs
- Follow Conventional Commits

License: MIT
