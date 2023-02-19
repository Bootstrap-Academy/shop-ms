from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, String
from sqlalchemy.orm import Mapped

from api.database import Base, db
from api.database.database import UTCDateTime
from api.models import Coins
from api.utils.utc import utcnow


class PaypalOrder(Base):
    __tablename__ = "shop_paypal_orders"

    id: Mapped[str] = Column(String(32), primary_key=True, unique=True)
    user_id: Mapped[str] = Column(String(36))
    created_at: Mapped[datetime] = Column(UTCDateTime)
    coins: Mapped[int] = Column(BigInteger)
    pending: Mapped[bool] = Column(Boolean, default=True)

    @classmethod
    async def create(cls, order_id: str, user_id: str, coins: int) -> PaypalOrder:
        order = cls(id=order_id, user_id=user_id, coins=coins, created_at=utcnow())
        await db.add(order)
        return order

    @classmethod
    async def get(cls, order_id: str, user_id: str) -> PaypalOrder | None:
        return await db.get(cls, id=order_id, user_id=user_id)

    async def capture(self) -> int | None:
        self.pending = False
        return await Coins.add(self.user_id, self.coins, False)
