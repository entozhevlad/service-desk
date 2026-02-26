from fastapi import APIRouter, Depends, HTTPException, status

from app.api.tickets.dependencies import get_service_desk
from app.api.tickets.schemas import (
    Ticket,
    TicketCreate,
    TicketDeleted,
    TicketUpdate,
)
from app.api.tickets.service import ServiceDesk

tickets_router = APIRouter(tags=["tickets"])


@tickets_router.post("/ticket", response_model=Ticket)
async def create_ticket(
    payload: TicketCreate,
    service_desk: ServiceDesk = Depends(get_service_desk),
) -> Ticket:
    """Создает тикет."""
    return await service_desk.create_ticket(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
    )


@tickets_router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    service_desk: ServiceDesk = Depends(get_service_desk),
) -> Ticket:
    """Возвращает тикет по идентификатору."""
    ticket = await service_desk.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket


@tickets_router.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    service_desk: ServiceDesk = Depends(get_service_desk),
) -> Ticket:
    """Обновляет тикет по идентификатору."""
    payload_data = payload.model_dump(exclude_unset=True)
    if not payload_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )
    ticket = await service_desk.update_ticket(
        ticket_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
    )
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket


@tickets_router.get("/tickets", response_model=list[Ticket])
async def list_tickets(
    service_desk: ServiceDesk = Depends(get_service_desk),
) -> list[Ticket]:
    """Возвращает список тикетов."""
    return await service_desk.list_tickets()


@tickets_router.delete("/tickets/{ticket_id}", response_model=TicketDeleted)
async def delete_ticket(
    ticket_id: int,
    service_desk: ServiceDesk = Depends(get_service_desk),
) -> TicketDeleted:
    """Удаляет тикет по идентификатору."""
    deleted = await service_desk.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return TicketDeleted(id=ticket_id, message="Ticket deleted")
