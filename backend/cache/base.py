"""Thread-safe TTLCache wrapper."""

from __future__ import annotations

import threading
from typing import Generic, TypeVar

from cachetools import TTLCache

T = TypeVar("T")


class ThreadSafeCache(Generic[T]):
    """Thread-safe TTL cache with size tracking.

    Wraps cachetools.TTLCache with a threading.RLock for safe concurrent
    access from multiple request handlers.
    """

    def __init__(self, maxsize: int, ttl: int) -> None:
        self._cache: TTLCache[str, T] = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = threading.RLock()

    def get(self, key: str) -> T | None:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: T) -> None:
        with self._lock:
            self._cache[key] = value

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    @property
    def maxsize(self) -> int:
        with self._lock:
            return self._cache.maxsize

    @property
    def ttl(self) -> int:
        with self._lock:
            return self._cache.ttl

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
