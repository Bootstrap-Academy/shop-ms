from pydantic import BaseModel


class Hearts(BaseModel):
    hearts: int
    last_auto_refill: int
    next_auto_refill: int
