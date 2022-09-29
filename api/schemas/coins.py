from pydantic import AnyHttpUrl, BaseModel, Field


class BuyCoins(BaseModel):
    coins: int = Field(ge=500, le=1_000_000, description="The amount of coins to buy")


class StripeBuyCoins(BuyCoins):
    success_url: AnyHttpUrl = Field(description="The URL to redirect to on success")
    cancel_url: AnyHttpUrl = Field(description="The URL to redirect to on cancel")


class Balance(BaseModel):
    coins: int = Field(description="The amount of coins the user has")
