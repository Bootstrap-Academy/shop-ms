from pydantic import BaseModel


class PremiumPlan(BaseModel):
    price: int
    months: int


class PremiumStatus(BaseModel):
    premium: bool
    since: float | None
    until: float | None
