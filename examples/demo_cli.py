from __future__ import annotations

import json

from local_first_ai_service.cache import TTLCache
from local_first_ai_service.metrics import MetricsCollector
from local_first_ai_service.models import Request
from local_first_ai_service.service import LocalFirstService


class DeterministicClock:
    def __init__(self, start: float = 0.0) -> None:
        self._current = start

    def __call__(self) -> float:
        return self._current


def _print_response(label: str, request: Request, response: dict[str, object]) -> None:
    print(f"scenario: {label}")
    print(f"deadline_ms: {request.deadline_ms}")
    print(f"route: {response['route']}")
    print(f"degraded: {str(response['degraded']).lower()}")
    print(f"cache_hit: {str(response['cache_hit']).lower()}")
    print(f"latency_ms: {response['latency_ms']:.2f}")
    print(f"result: {response['result']}")
    print("-")


def main() -> None:
    clock = DeterministicClock()
    metrics = MetricsCollector()
    cache = TTLCache[str](ttl_s=2.0, time_fn=clock)
    service = LocalFirstService(cache=cache, metrics=metrics, time_fn=clock)

    scenarios: list[tuple[str, Request]] = [
        ("local: cold", Request(payload="hello", deadline_ms=250, simulate_latency_ms=3)),
        (
            "local: cache hit",
            Request(payload="hello", deadline_ms=250, simulate_latency_ms=1),
        ),
        (
            "fallback: network ok",
            Request(payload="cloud:remote", deadline_ms=250, simulate_latency_ms=4),
        ),
        (
            "degraded: offline",
            Request(
                payload="cloud:remote",
                network_available=False,
                deadline_ms=250,
                simulate_latency_ms=2,
            ),
        ),
        (
            "degraded: deadline",
            Request(payload="slow", deadline_ms=5, simulate_latency_ms=10),
        ),
    ]

    for label, request in scenarios:
        response = service.handle(request)
        payload = response.to_dict()
        _print_response(label, request, payload)

    print("metrics:")
    print(json.dumps(metrics.snapshot(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
