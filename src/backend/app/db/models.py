from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import TicketPriority, TicketStatus


class Ticket(Base):
    """ORM модель тикета."""
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
    )
    description: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        default="",
        server_default="",
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status"),
        nullable=False,
        default=TicketStatus.NEW,
        server_default=TicketStatus.NEW.value,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority, name="ticket_priority"),
        nullable=False,
        default=TicketPriority.MEDIUM,
        server_default=TicketPriority.MEDIUM.value,
    )
