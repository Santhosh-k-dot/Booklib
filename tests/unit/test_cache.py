import pytest
import asyncio
from fastapi_cache import FastAPICache
from app.cache import init_cache

# -------------------------
# CACHE INITIALIZATION
# -------------------------

def test_cache_initialization_memory_backend():
    init_cache(testing=True)

    assert FastAPICache.get_backend() is not None
    assert FastAPICache.get_prefix() == "test-cache"


# -------------------------
# CACHE HIT & MISS
# -------------------------

@pytest.mark.asyncio
async def test_cache_miss_then_hit():
    init_cache(testing=True)
    backend = FastAPICache.get_backend()

    key = "test-key"

    # Cache MISS
    value = await backend.get(key)
    assert value is None

    # Cache SET
    await backend.set(key, "cached-value", expire=10)

    # Cache HIT
    value = await backend.get(key)
    assert value == "cached-value"


# -------------------------
# CACHE EXPIRY
# -------------------------

@pytest.mark.asyncio
async def test_cache_expiry():
    init_cache(testing=True)
    backend = FastAPICache.get_backend()

    key = "expire-key"

    await backend.set(key, "temp-value", expire=1)

    await asyncio.sleep(2)  # wait for expiry

    value = await backend.get(key)
    assert value is None