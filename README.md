# local-first-ai-service

**Portfolio Note (Safe-to-Publish):** This repository is a public, generic demonstration and does not disclose proprietary architectures, algorithms, or patent-related material.

[![ci](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service/actions/workflows/ci.yml/badge.svg)](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.11%2B-blue)](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service)
[![license](https://img.shields.io/badge/license-mit-green)](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service/blob/main/LICENSE)
[![ruff](https://img.shields.io/badge/ruff-enabled-purple)](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service)
[![tests](https://img.shields.io/badge/tests-pytest-informational)](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service)
[![types](https://img.shields.io/badge/types-pyright-blue)](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service)
[![coverage](https://img.shields.io/badge/coverage-report-lightgrey)](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service)

A local-first service that deterministically routes by deadline, degrades safely under constraints, and emits audit-ready metrics without calling external APIs.

## Demo (3 seconds)

![Demo](docs/assets/demo.gif)

> Note: The demo GIF is uploaded manually outside this PR.

## Why this matters

- Keeps data, latency, and failure modes local by default.
- Makes routing decisions reproducible for audits and incident reviews.
- Degrades safely with clear, predictable outcomes under constraints.

## Architecture - Local-first decision flow

```mermaid
flowchart TD
    request[request] --> deadline{deadline met?}
    deadline -- no --> degraded[degraded response]
    deadline -- yes --> kind{payload type}
    kind -- local --> local[local handler]
    kind -- cloud --> network{network available?}
    network -- no --> degraded
    network -- yes --> fallback[fallback handler]
    local --> cache[cache + metrics]
    fallback --> cache
    degraded --> cache
```

## Behavior

- **Local:** deterministic in-process handler.
- **Fallback:** deterministic alternate route when network is available.
- **Degraded:** minimal response when constraints are violated.
- See: [Policy Model (SLO-aware routing)](docs/POLICY_MODEL.md)
## Observability

Metrics capture per-request latency and export JSON snapshots with p50/p95 to support audits and tests.

## What this demonstrates

- Deterministic routing and deadline enforcement.
- Local-first execution with explicit fallback rules.
- Graceful degradation when constraints fail.
- Cache-aware latency and audit metrics.
- Fully testable, offline-friendly behavior.

## Use cases

- Edge runtimes needing strict latency budgets.
- Deterministic routing for regulated workloads.
- Local-first agents with predictable failure modes.

## Quickstart

```bash
pip install -e .
pip install pytest ruff pyright
python examples/demo_cli.py
pytest
```

## License

MIT License. See [LICENSE](https://github.com/rafaellimatecnologia-cloud/local-first-ai-service/blob/main/LICENSE).
