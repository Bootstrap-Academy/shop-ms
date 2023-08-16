from pydantic import BaseModel, Field


class HeartsConfig(BaseModel):
    hearts_max: int = Field(description="The maximum number of heart halves a user can have.")
    hearts_refill_price: int = Field(description="The number of morphcoins to pay for manually refilling hearts.")


class Hearts(BaseModel):
    hearts: int = Field(description="The number of heart halves the user has.")
    last_auto_refill: int = Field(description="Timestamp of the last free refill.")
    next_auto_refill: int = Field(description="Timestamp of the next free refill.")
