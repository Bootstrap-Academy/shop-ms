from __future__ import annotations

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import Mapped

from api.database import Base, db


class Coins(Base):
    __tablename__ = "shop_coins"

    user_id: Mapped[str] = Column(String(36), primary_key=True, unique=True)
    coins: Mapped[int] = Column(BigInteger)
    withheld_coins: Mapped[int] = Column(BigInteger)

    @staticmethod
    async def get(user_id: str) -> int:
        if row := await db.get(Coins, user_id=user_id):
            return row.coins
        return 0

    @staticmethod
    async def set(user_id: str, coins: int) -> None:
        if row := await db.get(Coins, user_id=user_id):
            row.coins = coins
        else:
            await db.add(Coins(user_id=user_id, coins=coins))

    @staticmethod
    async def add(user_id: str, amount: int, withhold: bool) -> int:
        if row := await db.get(Coins, user_id=user_id):
            if not withhold:
                row.coins += amount
            else:
                row.withheld_coins += amount
            return row.coins
        else:
            await db.add(Coins(user_id=user_id, coins=amount * (not withhold), withheld_coins=amount * withhold))
            return amount
