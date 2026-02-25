from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Ticket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class TicketDeleted(BaseModel):
    id: UUID
    message: str
