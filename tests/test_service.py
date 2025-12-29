from __future__ import annotations

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


def build_service(clock: FakeClock, ttl_s: float = 5.0) -> LocalFirstService:
    cache = TTLCache[str](ttl_s=ttl_s, time_fn=clock.time)
    metrics = MetricsCollector()
    return LocalFirstService(cache=cache, metrics=metrics, time_fn=clock.time)


def test_local_route_is_deterministic() -> None:
    clock = FakeClock()
    service = build_service(clock)

    request = Request(payload="hello")
    first = service.handle(request)
    second = service.handle(request)

    assert first.route is Route.LOCAL
    assert first.result == "local:HELLO:5"
    assert second.result == first.result
    assert second.cache_hit is True


def test_fallback_route_when_requested() -> None:
    clock = FakeClock()
    service = build_service(clock)

    request = Request(payload="cloud:hello", network_available=True)
    response = service.handle(request)

    assert response.route is Route.FALLBACK
    assert response.result == "fallback:olleh:5"
    assert response.cache_hit is False


def test_degraded_when_network_unavailable_for_fallback() -> None:
    clock = FakeClock()
    service = build_service(clock)

    request = Request(payload="cloud:hello", network_available=False)
    response = service.handle(request)

    assert response.route is Route.DEGRADED
    assert response.degraded is True


def test_degraded_when_deadline_exceeded() -> None:
    clock = FakeClock()
    service = build_service(clock)

    response = service.handle(Request(payload="hello", deadline_ms=0))

    assert response.route is Route.DEGRADED
    assert response.degraded is True


def test_cache_ttl_expires_entries() -> None:
    clock = FakeClock()
    service = build_service(clock, ttl_s=1.0)

    request = Request(payload="cache")
    first = service.handle(request)
    assert first.cache_hit is False

    clock.advance(0.5)
    second = service.handle(request)
    assert second.cache_hit is True

    clock.advance(1.0)
    third = service.handle(request)
    assert third.cache_hit is False
