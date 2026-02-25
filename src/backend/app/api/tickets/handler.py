from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tickets.schemas import Ticket
from app.api.tickets.service import ServiceDesk
from app.db.session import get_session

tickets_router = APIRouter(tags=["tickets"])


@tickets_router.post("/ticket", response_model=Ticket)
async def create_ticket(session: AsyncSession = Depends(get_session)) -> Ticket:
    service_desk = ServiceDesk(session)
    return await service_desk.create_ticket()


@tickets_router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Ticket:
    service_desk = ServiceDesk(session)
    ticket = await service_desk.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket
