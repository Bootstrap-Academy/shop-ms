from pydantic import BaseModel, Field


class BuyCoins(BaseModel):
    coins: int = Field(ge=500, le=1_000_000, description="The amount of coins to buy")


class Balance(BaseModel):
    coins: int = Field(description="The amount of coins the user has")
    withheld_coins: int = Field(
        description="The amount of coins the user has but are withheld "
        "until they provide the required information about them"
    )
