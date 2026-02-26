from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.types import TicketPriority, TicketStatus


class Ticket(BaseModel):
    """Схема тикета."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TicketDeleted(BaseModel):
    """Ответ при удалении тикета."""
    id: int
    message: str


class TicketCreate(BaseModel):
    """Входные данные для создания тикета."""
    title: str
    description: str = Field(default="")
    status: TicketStatus = Field(default=TicketStatus.NEW)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)


class TicketUpdate(BaseModel):
    """Входные данные для обновления тикета."""
    title: str | None = None
    description: str | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
