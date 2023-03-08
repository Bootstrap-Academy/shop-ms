"""add invoice numbers to paypal orders

Revision ID: e139c8893c87
Create Date: 2023-03-08 18:11:00.902690
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e139c8893c87"
down_revision = "a36b218872ff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("shop_paypal_orders", sa.Column("invoice_no", sa.BigInteger(), nullable=True))
    op.create_unique_constraint(None, "shop_paypal_orders", ["invoice_no"])


def downgrade() -> None:
    op.drop_column("shop_paypal_orders", "invoice_no")
