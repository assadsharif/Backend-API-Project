"""
Stock Signal API - Cache Service

In-memory TTL cache using cachetools for storing signal and indicator results.
LRU eviction when capacity is reached. 15-minute TTL by default.
"""

from typing import Any

from cachetools import TTLCache


class CacheService:
    """Thread-safe in-memory TTL cache for API responses."""

    def __init__(self, maxsize: int = 500, ttl: int = 900) -> None:
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._hits: int = 0
        self._misses: int = 0

    def get(self, key: str) -> Any | None:
        """Retrieve a value from cache. Returns None on miss."""
        value = self._cache.get(key)
        if value is not None:
            self._hits += 1
        else:
            self._misses += 1
        return value

    def set(self, key: str, value: Any) -> None:
        """Store a value in cache."""
        self._cache[key] = value

    def has(self, key: str) -> bool:
        """Check if a key exists in cache (without affecting hit/miss stats)."""
        return key in self._cache

    def invalidate(self, key: str) -> bool:
        """Remove a key from cache. Returns True if key was present."""
        try:
            del self._cache[key]
            return True
        except KeyError:
            return False

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            "size": len(self._cache),
            "maxsize": self._cache.maxsize,
            "ttl": int(self._cache.ttl),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4),
        }
