from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import admin_auth, get_user, require_verified_email, user_auth
from api.exceptions.auth import PermissionDeniedError, admin_responses, verified_responses
from api.schemas.coins import BuyCoins
from api.schemas.user import User


router = APIRouter()


@router.get(
    "/coins/{user_id}", dependencies=[require_verified_email], responses=verified_responses(int, PermissionDeniedError)
)
async def get_balance(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    return await models.Coins.get(user_id)


@router.post("/coins", dependencies=[require_verified_email], responses=verified_responses(int))
async def buy_coins(data: BuyCoins, user: User = user_auth) -> Any:
    return await models.Coins.add(user.id, data.coins)


@router.put("/coins/{user_id}", dependencies=[admin_auth], responses=admin_responses(bool))
async def set_coins(coins: int = Body(embed=True, ge=0), user_id: str = get_user(check_existence=True)) -> Any:
    await models.Coins.set(user_id, coins)
    return True
