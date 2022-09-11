"""add coins table

Revision ID: 1b89576b3cf4
Create Date: 2022-09-11 13:43:23.863436
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1b89576b3cf4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_coins",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("coins", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("user_id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_coins")
