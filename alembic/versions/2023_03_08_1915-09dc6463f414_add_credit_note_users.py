"""add credit_note_users

Revision ID: 09dc6463f414
Create Date: 2023-03-08 19:15:15.007661
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "09dc6463f414"
down_revision = "e139c8893c87"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_credit_note_users",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("public_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("public_id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("shop_credit_note_users")
