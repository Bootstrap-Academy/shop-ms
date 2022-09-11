from pydantic import BaseModel, Field


class BuyCoins(BaseModel):
    coins: int = Field(gt=0, description="The amount of coins to buy")


class Balance(BaseModel):
    coins: int = Field(description="The amount of coins the user has")
