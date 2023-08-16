from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from api.database import Base, db
from api.database.database import UTCDateTime
from api.schemas.hearts import Hearts as HeartsSchema
from api.settings import settings
from api.utils.utc import utcnow


class Hearts(Base):
    __tablename__ = "shop_hearts"

    user_id: Mapped[str] = Column(String(36), primary_key=True)
    hearts: Mapped[int] = Column(Integer)
    last_auto_refill: Mapped[datetime] = Column(UTCDateTime)

    @property
    def next_auto_refill(self) -> datetime:
        return _next_refill(self.last_auto_refill)

    @property
    def serialize(self) -> HeartsSchema:
        return HeartsSchema(
            hearts=self.hearts,
            last_auto_refill=int(self.last_auto_refill.timestamp()),
            next_auto_refill=int(self.next_auto_refill.timestamp()),
        )

    @classmethod
    async def get(cls, user_id: str) -> Hearts:
        now = utcnow()
        if not (row := await db.get(cls, user_id=user_id)):
            row = cls(user_id=user_id, hearts=settings.hearts_max, last_auto_refill=now)
            await db.add(row)
        elif now >= row.next_auto_refill:
            row.refill()
            row.last_auto_refill = now
        return row

    def add(self, hearts: int) -> bool:
        if self.hearts + hearts < 0:
            return False
        self.hearts = min(self.hearts + hearts, settings.hearts_max)
        return True

    def refill(self) -> None:
        self.hearts = settings.hearts_max


def _next_refill(last: datetime) -> datetime:
    out = datetime.combine(last.date(), settings.hearts_refill_time)
    if out <= last:
        out += timedelta(days=1)
    return out
