import os
import uuid

import pytest

from app.db.client import db


pytestmark = pytest.mark.asyncio


def _has_db_config() -> bool:
    if os.getenv("DATABASE_URL"):
        return True
    return all(
        os.getenv(name)
        for name in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
    )


@pytest.mark.skipif(not _has_db_config(), reason="Database config not provided")
async def test_db_uses_ephemeral_schema() -> None:
    pool = await db.connect()
    schema_name = f"test_schema_{uuid.uuid4().hex[:8]}"

    async with pool.acquire() as connection:
        await connection.execute(f'CREATE SCHEMA "{schema_name}"')
        await connection.execute(f'SET search_path TO "{schema_name}"')
        await connection.execute(
            'CREATE TABLE items (id SERIAL PRIMARY KEY, name TEXT NOT NULL)'
        )
        await connection.execute(
            'INSERT INTO items (name) VALUES ($1), ($2)',
            "alpha",
            "beta",
        )
        value = await connection.fetchval(
            "SELECT name FROM items WHERE id = $1",
            1,
        )
        assert value == "alpha"

        await connection.execute(f'DROP SCHEMA "{schema_name}" CASCADE')

    await db.disconnect()
