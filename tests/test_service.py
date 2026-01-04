from __future__ import annotations

from collections.abc import Callable

from local_first_ai_service.cache import TTLCache
from local_first_ai_service.metrics import MetricsCollector
from local_first_ai_service.models import Request, Route
from local_first_ai_service.service import LocalFirstService


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def time(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class StepClock:
    def __init__(self, steps: list[float]) -> None:
        self._steps = steps
        self._index = 0

    def time(self) -> float:
        if self._index < len(self._steps):
            value = self._steps[self._index]
            self._index += 1
            return value
        return self._steps[-1]


def build_service(time_fn: Callable[[], float], ttl_s: float = 5.0) -> LocalFirstService:
    cache = TTLCache[str](ttl_s=ttl_s, time_fn=time_fn)
    metrics = MetricsCollector()
    return LocalFirstService(cache=cache, metrics=metrics, time_fn=time_fn)


def test_local_route_is_deterministic() -> None:
    clock = FakeClock()
    service = build_service(clock.time)

    request = Request(payload="hello")
    first = service.handle(request)
    second = service.handle(request)

    assert first.route is Route.LOCAL
    assert first.result == "local:HELLO:5"
    assert second.result == first.result
    assert second.cache_hit is True


def test_fallback_route_when_requested() -> None:
    clock = FakeClock()
    service = build_service(clock.time)

    request = Request(payload="cloud:hello", network_available=True)
    response = service.handle(request)

    assert response.route is Route.FALLBACK
    assert response.result == "fallback:olleh:5"
    assert response.cache_hit is False


def test_degraded_when_network_unavailable_for_fallback() -> None:
    clock = FakeClock()
    service = build_service(clock.time)

    request = Request(payload="cloud:hello", network_available=False)
    response = service.handle(request)

    assert response.route is Route.DEGRADED
    assert response.degraded is True


def test_degraded_when_deadline_exceeded() -> None:
    clock = FakeClock()
    service = build_service(clock.time)

    response = service.handle(Request(payload="hello", deadline_ms=0))

    assert response.route is Route.DEGRADED
    assert response.degraded is True


def test_cache_ttl_expires_entries() -> None:
    clock = FakeClock()
    service = build_service(clock.time, ttl_s=1.0)

    request = Request(payload="cache")
    first = service.handle(request)
    assert first.cache_hit is False

    clock.advance(0.5)
    second = service.handle(request)
    assert second.cache_hit is True

    clock.advance(1.0)
    third = service.handle(request)
    assert third.cache_hit is False


def test_degraded_when_elapsed_time_exceeds_deadline() -> None:
    clock = StepClock([0.0, 0.0, 0.0, 0.2, 0.2])
    service = build_service(clock.time)

    request = Request(payload="hello", deadline_ms=50, simulate_latency_ms=10)
    response = service.handle(request)

    assert response.route is Route.DEGRADED
    assert response.degraded is True
