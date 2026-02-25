from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tickets.schemas import Ticket
from app.api.tickets.service import ServiceDesk
from app.db.session import get_session

tickets_router = APIRouter(tags=["tickets"])


@tickets_router.post("/ticket", response_model=Ticket)
async def create_ticket(session: AsyncSession = Depends(get_session)) -> Ticket:
    service_desk = ServiceDesk(session)
    return await service_desk.create_ticket()
