import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.api.tickets.service import ServiceDesk
from app.main import app
from app.db.session import get_session


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
    ticket = await service.create_ticket()

    response = await client.get(f"/tickets/{ticket.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(ticket.id)

    await db_session.execute(
        text("DELETE FROM tickets WHERE id = :id"),
        {"id": uuid.UUID(data["id"])},
    )
    await db_session.commit()
