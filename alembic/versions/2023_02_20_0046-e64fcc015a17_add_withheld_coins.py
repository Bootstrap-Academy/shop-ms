"""add withheld coins

Revision ID: e64fcc015a17
Create Date: 2023-02-20 00:46:59.192811
"""

from alembic import op

import sqlalchemy as sa

from api import models


# revision identifiers, used by Alembic.
revision = "e64fcc015a17"
down_revision = "060dc00335fa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("shop_coins", sa.Column("withheld_coins", sa.BigInteger(), nullable=True))
    op.execute(sa.update(models.Coins).values(withheld_coins=0))


def downgrade() -> None:
    op.drop_column("shop_coins", "withheld_coins")
