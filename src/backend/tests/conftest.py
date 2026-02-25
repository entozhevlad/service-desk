import os
import sys
from pathlib import Path
from typing import AsyncIterator

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.db.session import get_engine, get_session_factory


def _has_db_config() -> bool:
    if os.getenv("DATABASE_URL"):
        return True
    return all(
        os.getenv(name)
        for name in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
    )


@pytest.fixture(scope="session")
def db_configured() -> bool:
    return _has_db_config()


@pytest.fixture
async def db_session(db_configured: bool) -> AsyncIterator[object]:
    if not db_configured:
        pytest.skip("Database config not provided")

    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            yield session
    finally:
        await get_engine().dispose()
