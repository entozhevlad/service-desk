import pytest
from sqlalchemy import text

from app.api.tickets.service import ServiceDesk
from app.db.types import TicketPriority, TicketStatus

pytestmark = pytest.mark.asyncio


async def test_create_ticket_persists_to_db(
    db_session: object,
) -> None:
    service_desk = ServiceDesk(db_session)
    ticket = await service_desk.create_ticket(
        title="hello",
        description="desc",
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
    )

    result = await db_session.execute(
        text(
            "SELECT id, title, description, status, priority, created_at, updated_at "
            "FROM tickets WHERE id = :id"
        ),
        {"id": ticket.id},
    )
    row = result.mappings().first()
    assert row is not None
    assert row["id"] == ticket.id
    assert row["created_at"].tzinfo is not None
    assert row["updated_at"].tzinfo is not None
    assert row["title"] == "hello"
    assert row["description"] == "desc"
    assert row["status"] == TicketStatus.NEW.value
    assert row["priority"] == TicketPriority.MEDIUM.value

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id"),
        {"id": ticket.id},
    )
    await db_session.commit()
