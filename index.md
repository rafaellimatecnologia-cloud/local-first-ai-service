# local-first-ai-service

A minimal, offline-friendly local-first routing service that deterministically enforces deadlines and degrades safely with audit-ready metrics.

## Guarantees

- No external network calls at runtime.
- Deterministic routing with explicit fallback/degraded outcomes.
- Local, reproducible metrics for audits and tests.

## Quickstart

```bash
pip install -e ".[dev]"
python examples/demo_cli.py
pytest -q
```

## Docs

- [README](README.md)
