import string
from asyncpg import Connection
import asyncpg
from testcontainers_demo.string_utils import generate_random_string
from random import Random
import asyncio


async def insert_random_key_value_pair(rng : Random, conn : Connection) -> string:
    """Insert a random key-value pair into the 'data' table."""
    key = generate_random_string(rng, 20)
    value = generate_random_string(rng, 20)
    await conn.execute('INSERT INTO data (key, value) VALUES ($1, $2)', key, value)
    return (key,value)

async def get_value(key: str, conn: Connection) -> str:
    """Retrieve a value from the 'data' table using the specified key."""
    row = await conn.fetchrow('SELECT value FROM data WHERE key = $1', key)
    if row:
        return row['value']
    else:
        return "Key not found"

async def get_count(conn: Connection) -> int:
    """Retrieve the count of rows in the 'data' table."""
    row = await conn.fetchrow('SELECT COUNT(*) AS count FROM data')
    count = row['count'] if row else 0
    return count

async def get_db_connection(
        host: str,
        port: int,
        usernamne: str,
        password: str,
        db_name: str) -> Connection:
    """
    Establish a postgres connection
    """

    connection = await asyncpg.connect(
        host=host,
        port=port,
        user=usernamne,
        password=password,
        database=db_name,
        ssl="prefer",
    )
    return connection


async def create_database(host: str, port: int, user: str, password: str, db_name: str):
    # Connect to the PostgreSQL server
    conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="template1",  # connect to the default database to create a new one
    )

    drop_sql = f"DROP DATABASE IF EXISTS {db_name}"
    create_sql = f"CREATE DATABASE {db_name} OWNER {user}"
    await conn.execute(drop_sql)
    await conn.execute(create_sql)

    
    # Reconnect to the new database to create a table
    await conn.close()

    new_conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name
    )

    # SQL to create the 'data' table
    create_table_sql = """
    CREATE TABLE data (
        key VARCHAR(20) PRIMARY KEY,
        value VARCHAR(20)
    )
    """
    await new_conn.execute(create_table_sql)
    await new_conn.close()



async def drop_database(host: str, port: int, user: str, password: str, db_name: str):
    # Connect to the PostgreSQL server
    conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="template1",  # connect to the default database to create a new one
    )

    drop_sql = f"DROP DATABASE IF EXISTS {db_name}"
    await conn.execute(drop_sql)
    # Reconnect to the new database to create a table
    await conn.close()
