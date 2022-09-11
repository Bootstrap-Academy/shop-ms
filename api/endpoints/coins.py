from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import admin_auth, get_user, require_verified_email, user_auth
from api.exceptions.auth import PermissionDeniedError, admin_responses, verified_responses
from api.schemas.coins import Balance, BuyCoins
from api.schemas.user import User


router = APIRouter()


@router.get(
    "/coins/{user_id}",
    dependencies=[require_verified_email],
    responses=verified_responses(Balance, PermissionDeniedError),
)
async def get_balance(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    """
    Return the balance of a user.

    *Requirements:* **VERIFIED** and (**SELF** or **ADMIN**)
    """

    return Balance(coins=await models.Coins.get(user_id))


@router.post("/coins", dependencies=[require_verified_email], responses=verified_responses(Balance))
async def buy_coins(data: BuyCoins, user: User = user_auth) -> Any:
    """
    Buy coins (**todo**)

    *Requirements:* **VERIFIED**
    """

    return Balance(coins=await models.Coins.add(user.id, data.coins))


@router.put("/coins/{user_id}", dependencies=[admin_auth], responses=admin_responses(bool))
async def set_coins(coins: int = Body(embed=True, ge=0), user_id: str = get_user(check_existence=True)) -> Any:
    """
    Set the balance of a user.

    *Requirements:* **ADMIN**
    """

    await models.Coins.set(user_id, coins)
    return True
