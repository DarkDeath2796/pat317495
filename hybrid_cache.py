# hybrid_cache.py
"""
Persistent cache: Redis if available, in-memory LRU fallback.
Improved with key prefixing and error resilience.
"""

import json
import os
import logging
import redis
from cachetools import LRUCache


CACHE_PREFIX = "pajajap:"
DEFAULT_TTL = 60 * 60 * 24 * 7  # 7 days


class HybridCache:
    def __init__(self, redis_url=None, maxsize=1000):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_available = False
        self.redis_client = None
        self.lru = LRUCache(maxsize=maxsize)

        try:
            self.redis_client = redis.Redis.from_url(
                self.redis_url, decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self.redis_client.ping()
            self.redis_available = True
            logging.info("Redis connected: %s", self.redis_url)
        except Exception as e:
            logging.info("Redis unavailable (%s), using in-memory LRU", e)

    def _rkey(self, key: str) -> str:
        return f"{CACHE_PREFIX}{key}"

    def get(self, key: str):
        # Try Redis first
        if self.redis_available:
            try:
                val = self.redis_client.get(self._rkey(key))
                if val is not None:
                    parsed = json.loads(val)
                    # Also populate LRU for fast subsequent access
                    self.lru[key] = parsed
                    return parsed
            except Exception as e:
                logging.warning("Redis get error: %s", e)

        return self.lru.get(key)

    def set(self, key: str, value):
        # Always set in LRU
        self.lru[key] = value

        # Try Redis
        if self.redis_available:
            try:
                self.redis_client.set(
                    self._rkey(key),
                    json.dumps(value),
                    ex=DEFAULT_TTL,
                )
            except Exception as e:
                logging.warning("Redis set error: %s", e)

    def __contains__(self, key: str) -> bool:
        if key in self.lru:
            return True
        if self.redis_available:
            try:
                return bool(self.redis_client.exists(self._rkey(key)))
            except Exception:
                pass
        return False

    def items(self):
        """Yield all cached items (for admin endpoint)."""
        seen = set()

        # LRU items
        for k, v in self.lru.items():
            seen.add(k)
            yield k, v

        # Redis items not already in LRU
        if self.redis_available:
            try:
                for rkey in self.redis_client.scan_iter(f"{CACHE_PREFIX}*"):
                    key = rkey[len(CACHE_PREFIX):]
                    if key not in seen:
                        val = self.redis_client.get(rkey)
                        if val:
                            yield key, json.loads(val)
            except Exception as e:
                logging.warning("Redis scan error: %s", e)

    def clear(self):
        """Clear all caches."""
        self.lru.clear()
        if self.redis_available:
            try:
                for rkey in self.redis_client.scan_iter(f"{CACHE_PREFIX}*"):
                    self.redis_client.delete(rkey)
            except Exception:
                pass

    @property
    def stats(self) -> dict:
        info = {"lru_size": len(self.lru), "redis_available": self.redis_available}
        if self.redis_available:
            try:
                info["redis_keys"] = sum(
                    1 for _ in self.redis_client.scan_iter(f"{CACHE_PREFIX}*")
                )
            except Exception:
                info["redis_keys"] = "error"
        return info