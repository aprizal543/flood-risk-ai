"""Thread-safe cache hit/miss counters."""

from __future__ import annotations

import threading


class CacheMetrics:
    """Thread-safe hit/miss counters for a single cache instance."""

    def __init__(self) -> None:
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()

    def hit(self) -> None:
        with self._lock:
            self._hits += 1

    def miss(self) -> None:
        with self._lock:
            self._misses += 1

    @property
    def hits(self) -> int:
        with self._lock:
            return self._hits

    @property
    def misses(self) -> int:
        with self._lock:
            return self._misses

    @property
    def total(self) -> int:
        with self._lock:
            return self._hits + self._misses

    @property
    def hit_rate(self) -> float:
        with self._lock:
            total = self._hits + self._misses
            if total == 0:
                return 0.0
            return round(self._hits / total, 4)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total": self._hits + self._misses,
                "hit_rate": self.hit_rate,
            }
