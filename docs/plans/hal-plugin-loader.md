# HAL Plugin Loader — Design Overview (RFC)

Summary
- Provide a simple, testable in-process plugin loader for HAL drivers.
- Discovery: scan configured paths for  files and package dirs.
- Load: import file-based plugins via importlib with a stable module name prefix
  () to allow reliable unload.
- Unload: remove module objects and sys.modules entries.
- Registry: small in-memory registry records plugin metadata (name, version,
  entrypoint, description). Useful for listing and management APIs.

Security considerations
- In-process imports execute arbitrary code — for untrusted plugins prefer a
  subprocess sandbox with an RPC contract.
- Validate plugin metadata before registering.

Next steps
- Add a subprocess-based loader for isolation (Option B).
- Define a minimal plugin API contract (init, shutdown, metadata) and test it.
- Add CI job that runs plugin tests in a clean environment.
