from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from sqlalchemy.orm import Mapped

from api.database import Base, db
from api.models import Coins


class StripeCheckout(Base):
    __tablename__ = "shop_stripe_checkout"

    id: Mapped[str] = Column(String(128), primary_key=True, unique=True)
    user_id: Mapped[str] = Column(String(36))
    created_at: Mapped[datetime] = Column(DateTime)
    coins: Mapped[int] = Column(BigInteger)
    pending: Mapped[bool] = Column(Boolean, default=True)

    @classmethod
    async def create(cls, checkout_id: str, user_id: str, coins: int) -> StripeCheckout:
        order = cls(id=checkout_id, user_id=user_id, coins=coins, created_at=datetime.utcnow())
        await db.add(order)
        return order

    @classmethod
    async def get(cls, checkout_id: str) -> StripeCheckout | None:
        return await db.get(cls, id=checkout_id)

    async def capture(self) -> int | None:
        self.pending = False
        return await Coins.add(self.user_id, self.coins)
