"""add transaction table

Revision ID: a36b218872ff
Create Date: 2023-03-07 16:35:05.840298
"""

from alembic import op

import sqlalchemy as sa

from api.database.database import UTCDateTime


# revision identifiers, used by Alembic.
revision = "a36b218872ff"
down_revision = "e64fcc015a17"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", UTCDateTime(), nullable=True),
        sa.Column("coins", sa.BigInteger(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("credit_note", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_transactions")
