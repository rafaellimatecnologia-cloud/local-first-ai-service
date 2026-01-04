from __future__ import annotations

from local_first_ai_service.metrics import MetricsCollector


def test_metrics_snapshot_percentiles() -> None:
    metrics = MetricsCollector()
    for value in [10, 20, 30, 40, 50]:
        metrics.record(value)

    snapshot = metrics.snapshot()

    assert snapshot["count"] == 5
    assert snapshot["p50_ms"] == 30.0
    assert snapshot["p95_ms"] == 50.0
