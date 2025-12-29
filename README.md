# local-first-ai-service

## Portfolio Note (Safe-to-Publish)
This repository is a public, generic demonstration of a local-first service with graceful degradation.
It is intentionally IP-safe and does not disclose any proprietary architectures, algorithms, or patent-related material.

A minimal, publishable example of a local-first execution service with graceful
fallback and degradation behavior. The service never calls external APIs and
uses only deterministic, in-process handlers.

## Architecture

```
Request
  |
  v
+------------------+
| LocalFirstService|
+------------------+
  |        |     \
  |        |      \
  |        |       v
  |        |    [Degraded]
  |        v
  |     [Fallback]
  v
[Local]
  |
  v
[Cache + Metrics]
```

## Quickstart

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python examples/demo_cli.py
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python examples/demo_cli.py
```

## Behavior

- **LOCAL**: deterministic in-process handler.
- **FALLBACK**: simulated cloud handler (`payload` prefixed with `cloud:`).
- **DEGRADED**: minimal response when constraints are not met.

Constraints enforced by the service:

- If `network_available` is `False`, the fallback route is never used.
- If `deadline_ms` is exceeded (or zero), the service responds immediately with
  a degraded response.

## Observability

Metrics capture per-request latency and export JSON snapshots (p50/p95). The
`demo_cli` script prints the current snapshot after running scenarios.

## Skills Demonstrated
- Local-first execution with graceful degradation under constraints
- Deterministic fallback rules (no external APIs)
- Cache (TTL) behavior and basic performance metrics (p50/p95)
- Production hygiene: tests + CI + clear operational docs

## Tests

```bash
pytest
```

## Limitations

- No external network calls.
- In-memory cache only.
- Simulated latency is provided via request metadata for demos and tests.
