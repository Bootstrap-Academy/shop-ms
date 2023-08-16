"""premium

Revision ID: 21445e05c6bb
Create Date: 2023-08-12 22:01:17.271081
"""

from alembic import op

import sqlalchemy as sa

from api.database.database import UTCDateTime


# revision identifiers, used by Alembic.
revision = "21445e05c6bb"
down_revision = "09dc6463f414"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_premium",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("start", UTCDateTime(), nullable=True),
        sa.Column("end", UTCDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_premium")
