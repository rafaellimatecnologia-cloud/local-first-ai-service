from __future__ import annotations

from collections.abc import Callable

from .cache import TTLCache
from .metrics import MetricsCollector
from .models import Request, Response, Route


class LocalFirstService:
    def __init__(
        self,
        cache: TTLCache[str],
        metrics: MetricsCollector,
        time_fn: Callable[[], float],
    ) -> None:
        self._cache = cache
        self._metrics = metrics
        self._time_fn = time_fn

    def handle(self, request: Request) -> Response:
        start = self._time_fn()
        if request.deadline_ms <= 0:
            return self._degraded_response(start, request, cache_hit=False)
        if request.simulate_latency_ms >= request.deadline_ms:
            return self._degraded_response(start, request, cache_hit=False)

        if request.payload.startswith("cloud:"):
            if not request.network_available:
                return self._degraded_response(start, request, cache_hit=False)
            response = self._fallback_handler(request, start)
            self._metrics.record(response.latency_ms)
            return response

        cache_key = f"local::{request.payload}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            response = Response(
                route=Route.LOCAL,
                result=cached,
                degraded=False,
                cache_hit=True,
                latency_ms=self._latency_ms(start, request),
            )
            self._metrics.record(response.latency_ms)
            return response

        result = self._local_handler(request)
        self._cache.set(cache_key, result)
        response = Response(
            route=Route.LOCAL,
            result=result,
            degraded=False,
            cache_hit=False,
            latency_ms=self._latency_ms(start, request),
        )
        self._metrics.record(response.latency_ms)
        return response

    def _local_handler(self, request: Request) -> str:
        payload = request.payload.strip()
        return f"local:{payload.upper()}:{len(payload)}"

    def _fallback_handler(self, request: Request, start: float) -> Response:
        payload = request.payload.removeprefix("cloud:").strip()
        result = f"fallback:{payload[::-1]}:{len(payload)}"
        return Response(
            route=Route.FALLBACK,
            result=result,
            degraded=False,
            cache_hit=False,
            latency_ms=self._latency_ms(start, request),
        )

    def _degraded_response(self, start: float, request: Request, cache_hit: bool) -> Response:
        response = Response(
            route=Route.DEGRADED,
            result="degraded:unavailable",
            degraded=True,
            cache_hit=cache_hit,
            latency_ms=self._latency_ms(start, request),
        )
        self._metrics.record(response.latency_ms)
        return response

    def _latency_ms(self, start: float, request: Request) -> float:
        elapsed_ms = (self._time_fn() - start) * 1000
        return max(0.0, elapsed_ms + float(request.simulate_latency_ms))
