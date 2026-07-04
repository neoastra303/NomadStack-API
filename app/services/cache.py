import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()


class RedisCache:
    def __init__(self):
        self.client: aioredis.Redis | None = None

    async def init(self):
        if settings.REDIS_URL:
            self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Any | None:
        if not self.client:
            return None
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = 300):
        if not self.client:
            return
        await self.client.set(key, json.dumps(value), ex=ttl)


cache = RedisCache()
