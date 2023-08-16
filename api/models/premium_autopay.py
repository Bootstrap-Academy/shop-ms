from __future__ import annotations

from sqlalchemy import Column, Enum, String, desc
from sqlalchemy.orm import Mapped

from api.database import Base, db, db_wrapper
from api.database.database import select
from api.models.premium import Premium, PremiumPlan
from api.utils.utc import utcnow


class PremiumAutopay(Base):
    __tablename__ = "shop_premium_autopay"

    user_id: Mapped[str] = Column(String(36), primary_key=True)
    plan: Mapped[PremiumPlan] = Column(Enum(PremiumPlan))

    @classmethod
    async def get(cls, user_id: str) -> PremiumAutopay | None:
        return await db.get(cls, user_id=user_id)

    @classmethod
    async def set(cls, user_id: str, plan: PremiumPlan | None) -> None:
        if row := await db.get(cls, user_id=user_id):
            if plan:
                row.plan = plan
            else:
                await db.delete(row)
        elif plan:
            await db.add(cls(user_id=user_id, plan=plan))


@db_wrapper
async def run_autopay() -> None:
    plans: dict[str, PremiumAutopay] = {row.user_id: row async for row in await db.stream(select(PremiumAutopay))}
    row: Premium
    async for row in await db.stream(select(Premium).where(Premium.end > utcnow())):
        plans.pop(row.user_id, None)
    async for row in await db.stream(select(Premium).where(Premium.user_id.in_([*plans])).order_by(desc(Premium.end))):
        if plan := plans.pop(row.user_id, None):
            await row.run_autopay(plan)
