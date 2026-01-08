# Contributing

Thanks for your interest in improving this project.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Tests

```bash
pytest -q
```

## Lint & format

```bash
ruff check .
ruff format --check .
```

## Type checking

```bash
pyright
```

## Pre-commit (optional)

```bash
pre-commit install
pre-commit run --all-files
```

## Pull requests

- Keep changes focused and documented.
- Ensure tests, lint, format, and type checks pass.
- Do not introduce external service dependencies.
