from __future__ import annotations

import enum
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Column, String, desc
from sqlalchemy.orm import Mapped

from api.database import Base, db
from api.database.database import UTCDateTime, select
from api.models.coins import Coins
from api.models.transactions import Transaction
from api.settings import settings
from api.utils.cache import clear_cache
from api.utils.utc import utcnow


if TYPE_CHECKING:
    from api.models.premium_autopay import PremiumAutopay


class PremiumPlan(enum.Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

    @property
    def months(self) -> int:
        if self == PremiumPlan.MONTHLY:
            return 1
        else:
            return 12

    @property
    def timedelta(self) -> timedelta:
        return timedelta(days=365.25 / 12 * self.months)

    @property
    def price(self) -> int:
        if self == PremiumPlan.MONTHLY:
            return settings.premium_monthly_price
        else:
            return settings.premium_yearly_price


class Premium(Base):
    __tablename__ = "shop_premium"

    id: Mapped[str] = Column(String(36), primary_key=True)
    user_id: Mapped[str] = Column(String(36))
    start: Mapped[datetime] = Column(UTCDateTime)
    end: Mapped[datetime] = Column(UTCDateTime)

    @classmethod
    async def create(cls, user_id: str, delta: timedelta) -> Premium:
        now = utcnow()
        row = cls(id=str(uuid4()), user_id=user_id, start=now, end=now + delta)
        await db.add(row)
        return row

    @classmethod
    async def get_latest(cls, user_id: str) -> Premium | None:
        from . import PremiumAutopay

        out: Premium | None = await db.first(select(cls).filter_by(user_id=user_id).order_by(desc(cls.end)).limit(1))
        if not out or out.end > utcnow():
            return out

        if (plan := await PremiumAutopay.get(user_id)) and await out.run_autopay(plan):
            return out

        return None

    @classmethod
    async def add(cls, user_id: str, delta: timedelta) -> Premium:
        if latest := await cls.get_latest(user_id):
            latest.end += delta
            return latest
        else:
            return await cls.create(user_id, delta)

    async def run_autopay(self, autopay: PremiumAutopay) -> Premium | None:
        plan = autopay.plan
        if not await pay_for_premium(self.user_id, plan):
            await db.delete(autopay)
            return None

        now = utcnow()
        if now >= self.end + timedelta(days=7):
            return await Premium.create(self.user_id, plan.timedelta)

        if now >= self.end + timedelta(hours=2):
            self.end = now + plan.timedelta
        else:
            self.end += plan.timedelta

        return self


async def pay_for_premium(user_id: str, plan: PremiumPlan) -> bool:
    if (await Coins.get(user_id)).coins < plan.price:
        return False

    await Transaction.create(user_id, -plan.price, f"Premium {plan.name.lower()}", False)
    await Coins.add(user_id, -plan.price, False)
    await clear_cache("coins")
    return True
