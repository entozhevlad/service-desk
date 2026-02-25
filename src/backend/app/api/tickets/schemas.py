from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Ticket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    description: str


class TicketDeleted(BaseModel):
    id: UUID
    message: str


class TicketCreate(BaseModel):
    description: str = Field(default="")


class TicketUpdate(BaseModel):
    description: str
