from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Ticket(BaseModel):
    """Схема тикета."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    description: str


class TicketDeleted(BaseModel):
    """Ответ при удалении тикета."""
    id: UUID
    message: str


class TicketCreate(BaseModel):
    """Входные данные для создания тикета."""
    description: str = Field(default="")


class TicketUpdate(BaseModel):
    """Входные данные для обновления тикета."""
    description: str
