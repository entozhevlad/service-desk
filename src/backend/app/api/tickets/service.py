from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tickets.schemas import Ticket
from app.db.models import Ticket as TicketModel


class ServiceDesk:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_ticket(self, description: str = "") -> Ticket:
        ticket = TicketModel(description=description)
        self._session.add(ticket)
        await self._session.commit()
        await self._session.refresh(ticket)
        return Ticket.model_validate(ticket)

    async def get_ticket(self, ticket_id: UUID) -> Ticket | None:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket is None:
            return None
        return Ticket.model_validate(ticket)

    async def delete_ticket(self, ticket_id: UUID) -> bool:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket is None:
            return False
        await self._session.delete(ticket)
        await self._session.commit()
        return True

    async def update_ticket(self, ticket_id: UUID, description: str) -> Ticket | None:
        result = await self._session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket is None:
            return None
        ticket.description = description
        await self._session.commit()
        await self._session.refresh(ticket)
        return Ticket.model_validate(ticket)

    async def list_tickets(self) -> list[Ticket]:
        result = await self._session.execute(
            select(TicketModel).order_by(TicketModel.created_at.desc())
        )
        tickets = result.scalars().all()
        return [Ticket.model_validate(ticket) for ticket in tickets]
