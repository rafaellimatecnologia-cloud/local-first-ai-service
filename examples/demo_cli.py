from __future__ import annotations

import json
import time

from local_first_ai_service.cache import TTLCache
from local_first_ai_service.metrics import MetricsCollector
from local_first_ai_service.models import Request
from local_first_ai_service.service import LocalFirstService


def main() -> None:
    metrics = MetricsCollector()
    cache = TTLCache[str](ttl_s=2.0, time_fn=time.monotonic)
    service = LocalFirstService(cache=cache, metrics=metrics, time_fn=time.monotonic)

    scenarios = [
        Request(payload="hello"),
        Request(payload="hello"),
        Request(payload="cloud:remote", network_available=True),
        Request(payload="cloud:remote", network_available=False),
        Request(payload="slow", deadline_ms=1, simulate_latency_ms=5),
    ]

    for request in scenarios:
        response = service.handle(request)
        print(json.dumps(response.to_dict(), indent=2, sort_keys=True))

    print("metrics:")
    print(metrics.snapshot_json())


if __name__ == "__main__":
    main()
