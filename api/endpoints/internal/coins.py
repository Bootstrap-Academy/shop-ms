from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user
from api.exceptions.auth import internal_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.schemas.coins import Balance


router = APIRouter()


@router.get("/coins/{user_id}", responses=internal_responses(Balance))
async def get_balance(user_id: str = get_user()) -> Any:
    """Return the balance of a user."""

    return Balance(coins=await models.Coins.get(user_id))


@router.delete("/coins/{user_id}", responses=internal_responses(Balance, NotEnoughCoinsError))
async def spend_coins(
    coins: int = Body(embed=True, ge=0, description="The amount of coins to remove from the user's account"),
    user_id: str = get_user(),
) -> Any:
    """Remove coins from a user's balance."""

    if coins > await models.Coins.get(user_id):
        raise NotEnoughCoinsError
    return Balance(coins=await models.Coins.remove(user_id, coins))
