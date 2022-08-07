from aioredis.utils import from_url as redis_from_url
from secrets import choice
from typing import List
from time import time

class Cache(object):
    def __init__(self, connection_url: str, cache_duration_seconds: float) -> None:
        self.client = redis_from_url(connection_url)
        self.droplets = None
        self.cache_expiry = 0.0
        self.cache_duration_seconds = cache_duration_seconds
        self.index = 0

    async def fetch_droplet(self) -> List[str]:
        current_time = time()
        if current_time > self.cache_expiry:
            self.droplets = await self.client.lrange("droplets", 0, -1)
            self.cache_expiry = current_time + self.cache_duration_seconds

        return choice(self.droplets)

    async def add_droplets(self, new_droplets: List[str]) -> None:
        self.cache_expiry = time() + self.cache_duration_seconds
        
        current = await self.client.lrange("droplets", 0, -1)
        new = list(set(current) | set(new_droplets))
        
        await self.client.delete("droplets")
        return await self.client.rpush("droplets", *new)

    async def remove_droplets(self, removed: List[str]) -> None:
        for remove in removed:
            await self.client.lrem("droplets", 0, remove)

    async def reset_droplets(self) -> None:
        return await self.client.delete("droplets")
