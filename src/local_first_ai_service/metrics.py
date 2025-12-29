from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class MetricsCollector:
    latencies_ms: list[float] = field(default_factory=list)

    def record(self, latency_ms: float) -> None:
        self.latencies_ms.append(max(0.0, latency_ms))

    def snapshot(self) -> dict[str, float | int]:
        if not self.latencies_ms:
            return {"count": 0, "p50_ms": 0.0, "p95_ms": 0.0}
        sorted_latencies = sorted(self.latencies_ms)
        return {
            "count": len(sorted_latencies),
            "p50_ms": _percentile(sorted_latencies, 50),
            "p95_ms": _percentile(sorted_latencies, 95),
        }

    def snapshot_json(self) -> str:
        return json.dumps(self.snapshot(), indent=2, sort_keys=True)


def _percentile(values: Iterable[float], percentile: int) -> float:
    data = list(values)
    if not data:
        return 0.0
    index = int(round((percentile / 100) * (len(data) - 1)))
    index = max(0, min(index, len(data) - 1))
    return float(data[index])
