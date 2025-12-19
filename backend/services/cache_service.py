"""
Redis cache service - handles caching of processed sculpture data and session metadata.
"""

import redis.asyncio as aioredis
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for sculpture data and metadata."""

    def __init__(self, redis_url: str):
        """
        Initialize cache service with Redis connection.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Establish connection to Redis."""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info(f"Connected to Redis at {self.redis_url}")

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def ping(self) -> bool:
        """
        Check if Redis is accessible.

        Returns:
            True if Redis responds to ping, False otherwise
        """
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    # Sculpture caching methods
    async def get_sculpture(self, year: int, round: int, session: str, driver: str) -> Optional[Dict[str, Any]]:
        """
        Get cached sculpture data.

        Args:
            year: F1 season year
            round: Race round number
            session: Session identifier
            driver: Driver abbreviation

        Returns:
            Sculpture data dictionary or None if not cached
        """
        key = f"f1:sculpture:{year}:{round}:{session}:{driver}"
        try:
            data = await self.redis.get(key)
            if data:
                logger.info(f"Cache HIT for sculpture: {key}")
                return json.loads(data)
            else:
                logger.info(f"Cache MISS for sculpture: {key}")
                return None
        except Exception as e:
            logger.error(f"Error getting sculpture from cache: {e}")
            return None

    async def set_sculpture(
        self,
        year: int,
        round: int,
        session: str,
        driver: str,
        data: Dict[str, Any],
        ttl: int = 86400
    ):
        """
        Cache sculpture data with TTL.

        Args:
            year: F1 season year
            round: Race round number
            session: Session identifier
            driver: Driver abbreviation
            data: Sculpture data to cache
            ttl: Time-to-live in seconds (default 24 hours)
        """
        key = f"f1:sculpture:{year}:{round}:{session}:{driver}"
        try:
            # Add timestamp
            data['cached_at'] = datetime.utcnow().isoformat()

            await self.redis.setex(key, ttl, json.dumps(data))
            logger.info(f"Cached sculpture: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error caching sculpture: {e}")

    async def delete_sculpture(self, year: int, round: int, session: str, driver: str):
        """Delete a cached sculpture."""
        key = f"f1:sculpture:{year}:{round}:{session}:{driver}"
        await self.redis.delete(key)
        logger.info(f"Deleted sculpture from cache: {key}")

    # Session metadata caching methods
    async def get_session_metadata(self, year: int, round: int, session: str) -> Optional[Dict[str, str]]:
        """
        Get cached session metadata.

        Args:
            year: F1 season year
            round: Race round number
            session: Session identifier

        Returns:
            Session metadata dictionary or None if not cached
        """
        key = f"f1:session:{year}:{round}:{session}:metadata"
        try:
            data = await self.redis.hgetall(key)
            if data:
                logger.info(f"Cache HIT for session metadata: {key}")
                return data
            else:
                logger.info(f"Cache MISS for session metadata: {key}")
                return None
        except Exception as e:
            logger.error(f"Error getting session metadata: {e}")
            return None

    async def set_session_metadata(
        self,
        year: int,
        round: int,
        session: str,
        event_name: str,
        session_date: str,
        ttl: int = 86400
    ):
        """
        Cache session metadata.

        Args:
            year: F1 season year
            round: Race round number
            session: Session identifier
            event_name: Name of the event
            session_date: Session date
            ttl: Time-to-live in seconds (default 24 hours)
        """
        key = f"f1:session:{year}:{round}:{session}:metadata"
        try:
            metadata = {
                "year": str(year),
                "round": str(round),
                "session": session,
                "event_name": event_name,
                "date": session_date,
                "loaded_at": datetime.utcnow().isoformat()
            }

            await self.redis.hset(key, mapping=metadata)
            await self.redis.expire(key, ttl)
            logger.info(f"Cached session metadata: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error caching session metadata: {e}")

    async def get_session_drivers(self, year: int, round: int, session: str) -> Optional[List[str]]:
        """Get cached list of drivers for a session."""
        key = f"f1:session:{year}:{round}:{session}:drivers"
        try:
            drivers = await self.redis.lrange(key, 0, -1)
            if drivers:
                logger.info(f"Cache HIT for session drivers: {key}")
                return drivers
            return None
        except Exception as e:
            logger.error(f"Error getting session drivers: {e}")
            return None

    async def set_session_drivers(
        self,
        year: int,
        round: int,
        session: str,
        drivers: List[str],
        ttl: int = 86400
    ):
        """Cache list of drivers for a session."""
        key = f"f1:session:{year}:{round}:{session}:drivers"
        try:
            await self.redis.delete(key)  # Clear existing list
            if drivers:
                await self.redis.rpush(key, *drivers)
                await self.redis.expire(key, ttl)
                logger.info(f"Cached session drivers: {key} ({len(drivers)} drivers, TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error caching session drivers: {e}")

    async def mark_session_loaded(self, year: int, round: int, session: str, ttl: int = 86400):
        """Mark that a session has been loaded (lightweight flag)."""
        key = f"f1:session:{year}:{round}:{session}:loaded"
        await self.redis.setex(key, ttl, "1")

    async def is_session_loaded(self, year: int, round: int, session: str) -> bool:
        """Check if a session has been loaded."""
        key = f"f1:session:{year}:{round}:{session}:loaded"
        return await self.redis.exists(key) > 0

    # Cache management
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = await self.redis.info("stats")
            keyspace = await self.redis.info("keyspace")

            # Count keys by pattern
            sculpture_keys = len(await self.redis.keys("f1:sculpture:*"))
            session_keys = len(await self.redis.keys("f1:session:*"))

            return {
                "total_keys": info.get("db0", {}).get("keys", 0),
                "sculpture_cache_count": sculpture_keys,
                "session_cache_count": session_keys,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    async def clear_all_sculptures(self):
        """Clear all cached sculptures (admin operation)."""
        keys = await self.redis.keys("f1:sculpture:*")
        if keys:
            await self.redis.delete(*keys)
            logger.warning(f"Cleared {len(keys)} sculptures from cache")

    async def clear_all_sessions(self):
        """Clear all cached session metadata (admin operation)."""
        keys = await self.redis.keys("f1:session:*")
        if keys:
            await self.redis.delete(*keys)
            logger.warning(f"Cleared {len(keys)} session metadata from cache")
