from typing import AsyncGenerator
from asyncpg import Connection
import pytest
from redis import Redis
from testcontainers.redis import RedisContainer
from testcontainers.postgres import PostgresContainer
from testcontainers_demo.postgres_functions import create_database, drop_database, get_db_connection
from testcontainers_demo.string_utils import generate_random_string
import asyncio
import asyncpg
from random import Random

@pytest.fixture(scope="session")
def event_loop(request):
    """
    Creates a custom event loop fixture that is session-scoped, unlike the default
    function-scoped 'event_loop' fixture provided by pytest-asyncio.

    In asynchronous testing with pytest and asyncio, tests run inside an event loop.
    The pytest-asyncio plugin provides an 'event_loop' fixture that is function-scoped,
    meaning a new event loop is created and destroyed for every test function. This
    setup works well for most cases but becomes problematic when you have session-scoped
    fixtures (resources you want to initialize once and share across all tests in a session)
    that also need to perform asynchronous operations.

    The mismatch in scopes (session vs. function) can lead to errors since the session-scoped
    resources may try to use a closed or a new event loop that's different from the one they
    were initialized with. This custom session-scoped 'event_loop' fixture ensures that all
    async tests within a session use the same event loop. It allows session-scoped resources
    to be shared across tests smoothly, without scope-related issues.

    Parameters:
    - request: The fixture request object, a special parameter provided by pytest
      which gives access to the requesting test context.

    How it works:
    - The fixture defines an event loop policy that determines how the new event loop is created.
    - It then creates a new event loop that will be used for all tests in the session.
    - The 'yield' statement makes this event loop available to the tests. Once the tests are done,
      the loop is closed to ensure proper cleanup.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_redis() -> AsyncGenerator[Redis, None]:
    """
    Provide a function scoped redis container for testing.

    This function creates a throwaway Redis container per test.
    """

    with RedisContainer(
        image="redis:6.0-bullseye"
    ) as redis_container:
        
        redis = Redis(
            host=redis_container.get_container_host_ip(),
            port=redis_container.get_exposed_port(redis_container.port_to_expose),
            decode_responses=True)
        yield redis


@pytest.fixture(scope="session")
async def test_pg_container() -> AsyncGenerator[PostgresContainer, None]:
    """
    Establish a session scoped postgres PostgresContainer.  This postgres container
    is reused for all tests in the session, and is an input to the function scoped
    'test_database' method.  Keeping postgres scoped at the session level speeds up
    the runtime of tests.  Individual tests will create a new database inside
    of this container
    """
    postgres_image = "postgis/postgis:14-3.3"

    with PostgresContainer(
        image=postgres_image,
        port=5432,
        user="postgres",
        password="postgres",
    ) as pg_container:

       yield pg_container


@pytest.fixture(scope="function")
async def test_database(test_pg_container: PostgresContainer) -> AsyncGenerator[Connection, None]:
    """
    Provides a function scoped database connection for testing.  This function
    creates a database inside the session scoped postgres container for testing
    """

    db_name = f"test_db_{generate_random_string(Random(), length=8)}"  # Ensure unique DB name for each test
    # db_name = "test_db"

    host = test_pg_container.get_container_host_ip()
    port = test_pg_container.get_exposed_port(test_pg_container.port_to_expose)
    user = "postgres"
    password = "postgres"

    await create_database(host, port, user, password, db_name)

    # Establish a connection to the new database to pass to the test
    conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name
    )
    try:
        yield conn
        await conn.close()
        # drop the database
        await drop_database(host, port, user, password, db_name)
    finally:
        await conn.close()