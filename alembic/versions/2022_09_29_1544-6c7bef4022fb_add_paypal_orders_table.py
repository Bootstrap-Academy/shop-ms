"""add paypal_orders table

Revision ID: 6c7bef4022fb
Create Date: 2022-09-29 15:44:37.141700
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6c7bef4022fb"
down_revision = "1b89576b3cf4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_paypal_orders",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("coins", sa.BigInteger(), nullable=True),
        sa.Column("pending", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_paypal_orders")
