from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user
from api.exceptions.auth import internal_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.schemas.coins import Balance
from api.utils.cache import clear_cache, redis_cached


router = APIRouter()


@router.get("/coins/{user_id}", responses=internal_responses(Balance))
@redis_cached("coins", "user_id")
async def get_balance(user_id: str = get_user()) -> Any:
    """Return the balance of a user."""

    return Balance(coins=await models.Coins.get(user_id))


@router.post("/coins/{user_id}", responses=internal_responses(Balance, NotEnoughCoinsError))
async def add_coins(
    coins: int = Body(embed=True, description="The amount of coins to add to the user's account"),
    user_id: str = get_user(),
) -> Any:
    """
    Add coins to a user's balance.

    Specify a negative amount to remove coins.
    """

    if await models.Coins.get(user_id) + coins < 0:
        raise NotEnoughCoinsError

    await clear_cache("coins")

    return Balance(coins=await models.Coins.add(user_id, coins))
