from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tickets.schemas import (Ticket, TicketCreate, TicketDeleted,
                                     TicketUpdate)
from app.api.tickets.service import ServiceDesk
from app.db.session import get_session

tickets_router = APIRouter(tags=["tickets"])


@tickets_router.post("/ticket", response_model=Ticket)
async def create_ticket(
    payload: TicketCreate,
    session: AsyncSession = Depends(get_session),
) -> Ticket:
    service_desk = ServiceDesk(session)
    return await service_desk.create_ticket(description=payload.description)


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


@tickets_router.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: UUID,
    payload: TicketUpdate,
    session: AsyncSession = Depends(get_session),
) -> Ticket:
    service_desk = ServiceDesk(session)
    ticket = await service_desk.update_ticket(ticket_id, payload.description)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@tickets_router.get("/tickets", response_model=list[Ticket])
async def list_tickets(session: AsyncSession = Depends(get_session)) -> list[Ticket]:
    service_desk = ServiceDesk(session)
    return await service_desk.list_tickets()


@tickets_router.delete("/tickets/{ticket_id}", response_model=TicketDeleted)
async def delete_ticket(
    ticket_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> TicketDeleted:
    service_desk = ServiceDesk(session)
    deleted = await service_desk.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketDeleted(id=ticket_id, message="Ticket deleted")
