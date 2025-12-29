from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class _Entry(Generic[T]):
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    def __init__(self, ttl_s: float, time_fn: Callable[[], float]) -> None:
        self._ttl_s = ttl_s
        self._time_fn = time_fn
        self._data: dict[str, _Entry[T]] = {}

    def get(self, key: str) -> T | None:
        entry = self._data.get(key)
        if entry is None:
            return None
        if self._time_fn() >= entry.expires_at:
            self._data.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: T) -> None:
        self._data[key] = _Entry(value=value, expires_at=self._time_fn() + self._ttl_s)

    def clear(self) -> None:
        self._data.clear()
