from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Column, String, Text
from sqlalchemy.orm import Mapped

from api.database import Base, db
from api.database.database import UTCDateTime
from api.utils.utc import utcnow


class Transaction(Base):
    __tablename__ = "shop_transactions"

    id: Mapped[str] = Column(String(36), primary_key=True, unique=True)
    user_id: Mapped[str] = Column(String(36))
    created_at: Mapped[datetime] = Column(UTCDateTime)
    coins: Mapped[int] = Column(BigInteger)
    description: Mapped[str] = Column(Text)
    credit_note: Mapped[bool] = Column(Boolean)

    @classmethod
    async def create(cls, user_id: str, coins: int, description: str, credit_note: bool) -> Transaction:
        transaction = cls(
            id=str(uuid4()),
            user_id=user_id,
            coins=coins,
            description=description,
            created_at=utcnow(),
            credit_note=credit_note,
        )
        await db.add(transaction)
        return transaction
