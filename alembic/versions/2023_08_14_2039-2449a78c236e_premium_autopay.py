"""premium_autopay

Revision ID: 2449a78c236e
Create Date: 2023-08-14 20:39:06.286203
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2449a78c236e"
down_revision = "21445e05c6bb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_premium_autopay",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("plan", sa.Enum("MONTHLY", "YEARLY", name="premiumplan"), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_premium_autopay")
