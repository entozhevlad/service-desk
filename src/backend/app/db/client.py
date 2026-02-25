import os
from typing import AsyncIterator, Optional

import asyncpg


def _build_dsn() -> Optional[str]:
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        return dsn

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")

    if user and password and database:
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    return None


def has_database_url() -> bool:
    return _build_dsn() is not None


class Database:
    def __init__(self) -> None:
        self._pool: Optional[asyncpg.Pool] = None
        self._dsn: Optional[str] = None

    async def connect(self) -> asyncpg.Pool:
        if self._pool is not None:
            return self._pool

        dsn = _build_dsn()
        if not dsn:
            raise RuntimeError("DATABASE_URL (or POSTGRES_* vars) is not set")

        self._dsn = dsn
        self._pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
        return self._pool

    async def disconnect(self) -> None:
        if self._pool is None:
            return
        await self._pool.close()
        self._pool = None

    async def fetchval(self, query: str, *args) -> object:
        pool = await self.connect()
        async with pool.acquire() as connection:
            return await connection.fetchval(query, *args)


async def get_connection() -> AsyncIterator[asyncpg.Connection]:
    pool = await db.connect()
    async with pool.acquire() as connection:
        yield connection


# Singleton-style client for app usage
db = Database()
