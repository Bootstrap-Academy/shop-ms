from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user
from api.exceptions.auth import internal_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.schemas.coins import Balance
from api.services.auth import get_userinfo
from api.utils.cache import clear_cache, redis_cached


router = APIRouter()


@router.get("/coins/{user_id}", responses=internal_responses(Balance))
@redis_cached("coins", "user_id")
async def get_balance(user_id: str = get_user()) -> Any:
    """Return the balance of a user."""

    return (await models.Coins.get(user_id)).serialize


@router.post("/coins/{user_id}", responses=internal_responses(Balance, NotEnoughCoinsError))
async def add_coins(
    coins: int = Body(embed=True, description="The amount of coins to add to the user's account"),
    description: str = Body(description="Description of the transaction"),
    credit_note: bool | None = Body(None, description="Whether to include this transaction in a credit note"),
    user_id: str = get_user(),
) -> Any:
    """
    Add coins to a user's balance.

    Specify a negative amount to remove coins.
    """

    if (await models.Coins.get(user_id)).coins + coins < 0:
        raise NotEnoughCoinsError

    withhold = coins >= 0 and (not (info := await get_userinfo(user_id)) or not info.can_receive_coins)

    await clear_cache("coins")

    if credit_note is None:
        credit_note = coins > 0

    await models.Transaction.create(user_id, coins, description, credit_note)
    return (await models.Coins.add(user_id, coins, withhold)).serialize


@router.put("/coins/{user_id}/withheld", responses=internal_responses(bool))
async def release_withheld_coins(user_id: str = get_user()) -> Any:
    """Release withheld coins."""

    await models.Coins.release(user_id)

    return True
