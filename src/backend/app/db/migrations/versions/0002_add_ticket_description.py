"""add ticket description

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-25
"""

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
            server_default="",
        ),
    )
    op.alter_column("tickets", "description", server_default=None)


def downgrade() -> None:
    op.drop_column("tickets", "description")
