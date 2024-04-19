# Testcontainers Demo
This is a project providing testcontainers examples for postgresql and redis testing

## Quickstart

### Setup
```
python -m venv venv
source venv/bin/activate
pip install -e .[testing]
```

note, that in zsh, you need to use `pip install -e '.[testing]'`

### Run Tests
```
pytest -n auto
```

## Explanation
Testcontainers provides a clean way to create throwaway containers for testing.  This project has examples of postgres and redis using pytest 7.4.4.  There are some changes needed to support pytest 8+ that I have not worked out.

### Redis Tests
The redis tests use a new redis container for each test.  This is controlled in the conftest.py test_redis() function:

```python
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
```

This returns a redis connection for every function.  In the test_redis_functions, we have 100 copies of a test that inserts keys and asserts on counts.  If you change the scope of `test_redis` to `session`, you will see that the tests start to fail.  This is because the redis connection is being shared across the entire session, and by design, the test is leaving garbage in the cache.  Switching back to `function` it all works.

### Postgresql Tests
Postgres takes longer to setup, so we approach it slightly differently.  Instead of a new container per test, we'll create a new database per test, but we'll share the container across the session.  This is controlled using the  `test_pg_container` and `test_database` functions in conftest.py

```python


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
```

Similar to the Redis tests, the postgres tests add and count rows in the database.  In this case, each function is getting a new database, but the container is living longer.  You can see this when you run the tests by monitoring your docker desktop.  You'll see lots of redis containers coming and going, but the postgres containers will be more long lived.