from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import Column, String, desc
from sqlalchemy.orm import Mapped

from api.database import Base, db
from api.database.database import UTCDateTime, select
from api.utils.utc import utcnow


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
        # TODO auto renew
        return await db.first(
            select(cls).filter_by(user_id=user_id).where(cls.end > utcnow()).order_by(desc(cls.end)).limit(1)
        )

    @classmethod
    async def add(cls, user_id: str, delta: timedelta) -> Premium:
        if latest := await cls.get_latest(user_id):
            latest.end += delta
            return latest
        else:
            return await cls.create(user_id, delta)
