import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.api.tickets.service import ServiceDesk
from app.db.session import get_session
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
    ticket = await service.create_ticket(description="hello")

    response = await client.get(f"/tickets/{ticket.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(ticket.id)
    assert data["description"] == "hello"

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id"),
        {"id": uuid.UUID(data["id"])},
    )
    await db_session.commit()


async def test_update_ticket_description(client: AsyncClient, db_session: object) -> None:
    service = ServiceDesk(db_session)
    ticket = await service.create_ticket(description="old")

    response = await client.put(
        f"/tickets/{ticket.id}",
        json={"description": "new"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(ticket.id)
    assert data["description"] == "new"

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id"),
        {"id": uuid.UUID(data["id"])},
    )
    await db_session.commit()


async def test_list_tickets(client: AsyncClient, db_session: object) -> None:
    service = ServiceDesk(db_session)
    ticket_one = await service.create_ticket(description="one")
    ticket_two = await service.create_ticket(description="two")

    response = await client.get("/tickets")

    assert response.status_code == 200
    data = response.json()
    ids = [item["id"] for item in data]
    assert str(ticket_one.id) in ids
    assert str(ticket_two.id) in ids

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id1 OR id = :id2"),
        {"id1": ticket_one.id, "id2": ticket_two.id},
    )
    await db_session.commit()
