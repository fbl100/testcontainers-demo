from redis import Redis
from testcontainers_demo.redis_functions import insert_random_key_value_pair, get_value
from random import Random
import pyperclip
import pytest

@pytest.mark.parametrize("seed", range(50))
async def test_get_and_set_value(seed, test_redis: Redis):
    rng = Random(seed)
    # assert that we start with an empty cache
    # if the test_redis is using the 'session' scope
    # this will fail (since we leave garbage in the cache at the end of the test)
    assert len(test_redis.keys()) == 0
    # insert a random key/value pair
    k,v = await insert_random_key_value_pair(rng, test_redis)
    # confirm that it's actually there
    retrieved = await get_value(k, test_redis)
    assert v == retrieved
    # confirm that there is one item in the cache.
    # importantly, we'll leave the value there to confirm how testcontainer scopes work
    assert len(test_redis.keys()) == 1

