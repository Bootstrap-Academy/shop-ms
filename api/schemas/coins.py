from pydantic import BaseModel, Field


class BuyCoins(BaseModel):
    coins: int = Field(gt=0, description="The amount of coins to buy")
