"""rebuild tickets table

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "ad466f629331"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Пересоздает таблицу тикетов с новой схемой."""
    op.drop_table("tickets")
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "status",
            sa.Enum(
                "new",
                "in_progress",
                "done",
                "closed",
                name="ticket_status",
            ),
            nullable=False,
            server_default="new",
        ),
        sa.Column(
            "priority",
            sa.Enum(
                "low",
                "medium",
                "high",
                "critical",
                name="ticket_priority",
            ),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.alter_column("tickets", "description", server_default=None)


def downgrade() -> None:
    """Откатывает пересоздание таблицы тикетов."""
    op.drop_table("tickets")
    op.create_table(
        "tickets",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
            server_default="",
        ),
    )
    op.alter_column("tickets", "description", server_default=None)
