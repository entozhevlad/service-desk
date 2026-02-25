from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tickets.schemas import Ticket
from app.db.models import Ticket as TicketModel


class ServiceDesk:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_ticket(self) -> Ticket:
        ticket = TicketModel()
        self._session.add(ticket)
        await self._session.commit()
        await self._session.refresh(ticket)
        return Ticket.model_validate(ticket)
