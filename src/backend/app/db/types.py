from enum import Enum


class TicketStatus(str, Enum):
    """Статусы тикета."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Приоритеты тикета."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
