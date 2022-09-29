"""add stripe_checkouts table

Revision ID: f61dc9b636a1
Create Date: 2022-09-29 20:29:57.073231
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f61dc9b636a1"
down_revision = "6c7bef4022fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_stripe_checkout",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("coins", sa.BigInteger(), nullable=True),
        sa.Column("pending", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_stripe_checkout")
