"""remove stripe table

Revision ID: 060dc00335fa
Create Date: 2022-10-19 20:16:55.517696
"""

from alembic import op

import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = "060dc00335fa"
down_revision = "f61dc9b636a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("id", table_name="shop_stripe_checkout")
    op.drop_table("shop_stripe_checkout")


def downgrade() -> None:
    op.create_table(
        "shop_stripe_checkout",
        sa.Column("id", mysql.VARCHAR(collation="utf8mb4_bin", length=128), nullable=False),
        sa.Column("user_id", mysql.VARCHAR(collation="utf8mb4_bin", length=36), nullable=True),
        sa.Column("created_at", mysql.DATETIME(), nullable=True),
        sa.Column("coins", mysql.BIGINT(display_width=20), autoincrement=False, nullable=True),
        sa.Column("pending", mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_bin",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index("id", "shop_stripe_checkout", ["id"], unique=False)
