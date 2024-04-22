from asyncpg import Connection
from random import Random
from testcontainers_demo.postgres_functions import insert_random_key_value_pair, get_value, get_count
import pyperclip
import pytest

@pytest.mark.parametrize("seed", range(50))
async def test_postgres(seed, test_database: Connection):
    rng = Random(seed)
    # confirm that we start with an empty database
    count = await get_count(test_database)
    assert count == 0
    # insert a new key/value
    k, v = await insert_random_key_value_pair(rng, test_database)
    # confirm that we get it back
    retrieved = await get_value(k, test_database)
    assert v == retrieved
    # confirm we have one thing in the datavase
    count = await get_count(test_database)
    assert count == 1
