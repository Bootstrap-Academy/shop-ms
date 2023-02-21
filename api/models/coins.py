from __future__ import annotations

from typing import Any

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import Mapped

from api.database import Base, db


class Coins(Base):
    __tablename__ = "shop_coins"

    user_id: Mapped[str] = Column(String(36), primary_key=True, unique=True)
    coins: Mapped[int] = Column(BigInteger)
    withheld_coins: Mapped[int] = Column(BigInteger)

    @property
    def serialize(self) -> dict[str, Any]:
        return {"coins": self.coins, "withheld_coins": self.withheld_coins}

    @staticmethod
    async def get(user_id: str) -> Coins:
        if row := await db.get(Coins, user_id=user_id):
            return row
        return await db.add(Coins(user_id=user_id, coins=0, withheld_coins=0))

    @staticmethod
    async def set(user_id: str, coins: int) -> None:
        if row := await db.get(Coins, user_id=user_id):
            row.coins = coins
        else:
            await db.add(Coins(user_id=user_id, coins=coins, withheld_coins=0))

    @staticmethod
    async def add(user_id: str, amount: int, withhold: bool) -> Coins:
        if row := await db.get(Coins, user_id=user_id):
            if not withhold:
                row.coins += amount
            else:
                row.withheld_coins += amount
            return row
        else:
            return await db.add(Coins(user_id=user_id, coins=amount * (not withhold), withheld_coins=amount * withhold))

    @staticmethod
    async def release(user_id: str) -> None:
        if row := await db.get(Coins, user_id=user_id):
            row.coins += row.withheld_coins
            row.withheld_coins = 0
