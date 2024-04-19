
from redis import Redis
from testcontainers_demo.string_utils import generate_random_string
from random import Random

async def insert_random_key_value_pair(rng: Random, redis_conn : Redis):
    """Insert a random key-value pair into Redis."""
    key = generate_random_string(rng, 20)
    value = generate_random_string(rng, 20)
    redis_conn.set(key, value)
    print(f"Inserted key: {key}, value: {value}")
    return key, value

async def get_value(key, redis_conn: Redis):
    """Retrieve a value from Redis using the specified key."""
    value = redis_conn.get(key)
    if value:
        print(f"Retrieved value: {value} for key: {key}")
        return value
    else:
        print(f"No value found for key: {key}")
        return "Key not found"
    