from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tickets.schemas import Ticket
from app.db.models import Ticket as TicketModel
from app.db.types import TicketPriority, TicketStatus


class ServiceDesk:
    """Сервисный слой работы с тикетами."""
    def __init__(self, session: AsyncSession) -> None:
        """Создает сервис с сессией БД."""
        self._session = session

    async def create_ticket(
        self,
        title: str,
        description: str = "",
        status: TicketStatus = TicketStatus.NEW,
        priority: TicketPriority = TicketPriority.MEDIUM,
    ) -> Ticket:
        """Создает тикет с описанием."""
        ticket = TicketModel(
            title=title,
            description=description,
            status=status,
            priority=priority,
        )
        self._session.add(ticket)
        await self._session.commit()
        await self._session.refresh(ticket)
        return Ticket.model_validate(ticket)

    async def get_ticket(self, ticket_id: int) -> Ticket | None:
        """Возвращает тикет по идентификатору."""
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket is None:
            return None
        return Ticket.model_validate(ticket)

    async def delete_ticket(self, ticket_id: int) -> bool:
        """Удаляет тикет по идентификатору."""
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket is None:
            return False
        await self._session.delete(ticket)
        await self._session.commit()
        return True

    async def update_ticket(
        self,
        ticket_id: int,
        title: str | None = None,
        description: str | None = None,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
    ) -> Ticket | None:
        """Обновляет описание тикета."""
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket is None:
            return None
        if title is not None:
            ticket.title = title
        if description is not None:
            ticket.description = description
        if status is not None:
            ticket.status = status
        if priority is not None:
            ticket.priority = priority
        ticket.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(ticket)
        return Ticket.model_validate(ticket)

    async def list_tickets(self) -> list[Ticket]:
        """Возвращает список тикетов."""
        result = await self._session.execute(
            select(TicketModel).order_by(TicketModel.created_at.desc())
        )
        tickets = result.scalars().all()
        return [Ticket.model_validate(ticket) for ticket in tickets]
