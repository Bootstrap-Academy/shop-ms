"""hearts

Revision ID: 72f9d22b9b71
Create Date: 2023-08-15 17:22:27.007020
"""

from alembic import op

import sqlalchemy as sa

from api.database.database import UTCDateTime


# revision identifiers, used by Alembic.
revision = "72f9d22b9b71"
down_revision = "2449a78c236e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_hearts",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("hearts", sa.Integer(), nullable=True),
        sa.Column("last_auto_refill", UTCDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_hearts")
