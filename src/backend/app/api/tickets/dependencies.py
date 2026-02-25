from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tickets.service import ServiceDesk
from app.db.session import get_session


def get_service_desk(
    session: AsyncSession = Depends(get_session),
) -> ServiceDesk:
    """Создает сервисный слой для тикетов."""
    return ServiceDesk(session)
