import uuid

import pytest
from sqlalchemy import text

from app.api.tickets.service import ServiceDesk

pytestmark = pytest.mark.asyncio


async def test_create_ticket_persists_to_db(
    db_session: object,
) -> None:
    service_desk = ServiceDesk(db_session)
    ticket = await service_desk.create_ticket(description="hello")

    result = await db_session.execute(
        text("SELECT id, created_at, description FROM tickets WHERE id = :id"),
        {"id": ticket.id},
    )
    row = result.mappings().first()
    assert row is not None
    assert row["id"] == ticket.id
    assert row["created_at"].tzinfo is not None
    assert row["description"] == "hello"

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id"),
        {"id": ticket.id},
    )
    await db_session.commit()
