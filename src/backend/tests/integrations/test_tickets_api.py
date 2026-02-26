import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.api.tickets.service import ServiceDesk
from app.db.session import get_session
from app.db.types import TicketPriority, TicketStatus
from app.main import app

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client(db_session: object):
    async def _get_session_override():
        yield db_session

    app.dependency_overrides[get_session] = _get_session_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def test_get_ticket_by_id(client: AsyncClient, db_session: object) -> None:
    service = ServiceDesk(db_session)
    ticket = await service.create_ticket(
        title="hello",
        description="desc",
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
    )

    response = await client.get(f"/tickets/{ticket.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket.id
    assert data["description"] == "desc"
    assert data["title"] == "hello"
    assert data["status"] == TicketStatus.NEW.value
    assert data["priority"] == TicketPriority.MEDIUM.value

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id"),
        {"id": data["id"]},
    )
    await db_session.commit()


async def test_update_ticket_description(client: AsyncClient, db_session: object) -> None:
    service = ServiceDesk(db_session)
    ticket = await service.create_ticket(
        title="old",
        description="old desc",
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
    )

    response = await client.put(
        f"/tickets/{ticket.id}",
        json={
            "description": "new desc",
            "status": TicketStatus.DONE.value,
            "priority": TicketPriority.HIGH.value,
            "title": "new title",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket.id
    assert data["description"] == "new desc"
    assert data["status"] == TicketStatus.DONE.value
    assert data["priority"] == TicketPriority.HIGH.value
    assert data["title"] == "new title"

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id"),
        {"id": data["id"]},
    )
    await db_session.commit()


async def test_list_tickets(client: AsyncClient, db_session: object) -> None:
    service = ServiceDesk(db_session)
    ticket_one = await service.create_ticket(
        title="one",
        description="one desc",
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
    )
    ticket_two = await service.create_ticket(
        title="two",
        description="two desc",
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
    )

    response = await client.get("/tickets")

    assert response.status_code == 200
    data = response.json()
    ids = [item["id"] for item in data]
    assert ticket_one.id in ids
    assert ticket_two.id in ids

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id1 OR id = :id2"),
        {"id1": ticket_one.id, "id2": ticket_two.id},
    )
    await db_session.commit()
