import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.coder import JsonCoder


async def init_cache(testing: bool = False):
    if testing:
        FastAPICache.init(
            InMemoryBackend(),
            prefix="test-cache",
            coder=JsonCoder()
        )
    else:
        redis_client = redis.from_url(
            "redis://localhost:6379",
            # decode_responses=True
        )

        FastAPICache.init(
            RedisBackend(redis_client),
            prefix="library-cache",
            coder=JsonCoder()
        )