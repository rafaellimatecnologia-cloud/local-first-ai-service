from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Route(str, Enum):
    LOCAL = "LOCAL"
    FALLBACK = "FALLBACK"
    DEGRADED = "DEGRADED"


@dataclass(frozen=True)
class Request:
    payload: str
    network_available: bool = True
    deadline_ms: int = 1_000
    simulate_latency_ms: int = 0


@dataclass(frozen=True)
class Response:
    route: Route
    result: str
    degraded: bool
    cache_hit: bool
    latency_ms: float

    def to_dict(self) -> dict[str, object]:
        return {
            "route": self.route.value,
            "result": self.result,
            "degraded": self.degraded,
            "cache_hit": self.cache_hit,
            "latency_ms": self.latency_ms,
        }
