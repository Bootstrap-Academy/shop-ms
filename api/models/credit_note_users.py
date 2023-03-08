from __future__ import annotations

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.functions import max as max_

from api.database import Base, db
from api.database.database import select


class CreditNoteUser(Base):
    __tablename__ = "shop_credit_note_users"

    user_id: Mapped[str] = Column(String(36), primary_key=True)
    public_id: Mapped[int] = Column(BigInteger, unique=True)

    @classmethod
    async def _create(cls, user_id: str) -> CreditNoteUser:
        out = cls(user_id=user_id, public_id=await cls._next())
        await db.add(out)
        return out

    @classmethod
    async def get(cls, user_id: str) -> int:
        if row := await db.get(cls, user_id=user_id):
            return row.public_id
        return (await cls._create(user_id)).public_id

    @classmethod
    async def _next(cls) -> int:
        return (await db.first(select(max_(cls.public_id))) or 0) + 1
