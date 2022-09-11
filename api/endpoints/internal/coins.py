from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user
from api.exceptions.auth import internal_responses
from api.exceptions.coins import NotEnoughCoinsError


router = APIRouter()


@router.get("/coins/{user_id}", responses=internal_responses(int))
async def get_balance(user_id: str = get_user()) -> Any:
    return await models.Coins.get(user_id)


@router.delete("/coins/{user_id}", responses=internal_responses(int, NotEnoughCoinsError))
async def spend_coins(coins: int = Body(embed=True, ge=0), user_id: str = get_user()) -> Any:
    if coins > await models.Coins.get(user_id):
        raise NotEnoughCoinsError
    return await models.Coins.remove(user_id, coins)
