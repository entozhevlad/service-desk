import pytest
from sqlalchemy import text

pytestmark = pytest.mark.asyncio


async def test_db_can_execute_simple_query(db_session: object) -> None:
    result = await db_session.execute(text("SELECT 1 AS value"))
    row = result.mappings().first()
    assert row is not None
    assert row["value"] == 1
