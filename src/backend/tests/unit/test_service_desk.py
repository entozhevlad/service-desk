import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from app.api.tickets.service import ServiceDesk
from app.db.models import Ticket as TicketModel

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_session() -> Mock:
    session = Mock()
    session.add = Mock()
    session.commit = AsyncMock()
    async def _refresh(ticket: TicketModel) -> None:
        if ticket.id is None:
            ticket.id = uuid.uuid4()
        if ticket.created_at is None:
            ticket.created_at = datetime.now(timezone.utc)

    session.refresh = AsyncMock(side_effect=_refresh)
    return session


@pytest.fixture
def service_desk(mock_session: Mock) -> ServiceDesk:
    return ServiceDesk(mock_session)


async def test_create_ticket_returns_id_and_timestamp(
    service_desk: ServiceDesk,
    mock_session: Mock,
) -> None:
    result = await service_desk.create_ticket()

    assert isinstance(result.id, uuid.UUID)
    assert isinstance(result.created_at, datetime)
    assert result.created_at.tzinfo is not None

    mock_session.add.assert_called_once()
    added_ticket = mock_session.add.call_args.args[0]
    assert isinstance(added_ticket, TicketModel)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(added_ticket)


async def test_get_ticket_returns_none_when_missing(mock_session: Mock) -> None:
    result = Mock()
    result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=result)
    service = ServiceDesk(mock_session)

    ticket = await service.get_ticket(uuid.uuid4())

    assert ticket is None


async def test_get_ticket_returns_ticket(mock_session: Mock) -> None:
    ticket_model = TicketModel()
    ticket_model.id = uuid.uuid4()
    ticket_model.created_at = datetime.now(timezone.utc)
    ticket_model.description = "test"

    result = Mock()
    result.scalar_one_or_none.return_value = ticket_model
    mock_session.execute = AsyncMock(return_value=result)
    service = ServiceDesk(mock_session)

    ticket = await service.get_ticket(ticket_model.id)

    assert ticket is not None
    assert ticket.id == ticket_model.id
    assert ticket.created_at == ticket_model.created_at
    assert ticket.description == ticket_model.description


async def test_create_ticket_default_description(mock_session: Mock) -> None:
    service = ServiceDesk(mock_session)
    result = await service.create_ticket()

    mock_session.add.assert_called_once()
    added_ticket = mock_session.add.call_args.args[0]
    assert isinstance(added_ticket, TicketModel)
    assert added_ticket.description == ""


async def test_update_ticket_updates_description(mock_session: Mock) -> None:
    ticket_model = TicketModel()
    ticket_model.id = uuid.uuid4()
    ticket_model.created_at = datetime.now(timezone.utc)
    ticket_model.description = "old"

    result = Mock()
    result.scalar_one_or_none.return_value = ticket_model
    mock_session.execute = AsyncMock(return_value=result)

    service = ServiceDesk(mock_session)
    updated = await service.update_ticket(ticket_model.id, "new")

    assert updated is not None
    assert updated.description == "new"
    assert ticket_model.description == "new"
    mock_session.commit.assert_awaited_once()


async def test_list_tickets_returns_models(mock_session: Mock) -> None:
    ticket_one = TicketModel()
    ticket_one.id = uuid.uuid4()
    ticket_one.created_at = datetime.now(timezone.utc)
    ticket_one.description = "first"

    ticket_two = TicketModel()
    ticket_two.id = uuid.uuid4()
    ticket_two.created_at = datetime.now(timezone.utc)
    ticket_two.description = "second"

    result = Mock()
    result.scalars.return_value.all.return_value = [ticket_one, ticket_two]
    mock_session.execute = AsyncMock(return_value=result)

    service = ServiceDesk(mock_session)
    tickets = await service.list_tickets()

    assert [ticket.id for ticket in tickets] == [ticket_one.id, ticket_two.id]
