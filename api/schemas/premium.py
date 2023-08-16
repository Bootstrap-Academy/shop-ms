from pydantic import BaseModel, Field


class PremiumPlan(BaseModel):
    price: int = Field(description="The number of morphcoins to pay for this plan.")
    months: int = Field(description="The number of months of premium this plan contains.")


class PremiumStatus(BaseModel):
    premium: bool = Field(description="Whether premium is active for this user.")
    since: float | None = Field(description="Start timestamp of the current (contiguous) premium membership.")
    until: float | None = Field("End timestamp of the current premium membership.")
    autopay: str | None = Field("Premium plan used for automatic renewals.")
