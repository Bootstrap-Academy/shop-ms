from typing import Any

from fastapi import APIRouter

from api import models
from api.auth import get_user, require_verified_email
from api.exceptions.auth import verified_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.schemas.hearts import Hearts
from api.settings import settings
from api.utils.cache import clear_cache


router = APIRouter()


@router.get("/hearts/{user_id}", dependencies=[require_verified_email], responses=verified_responses(Hearts))
async def get_hearts(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    row = await models.Hearts.get(user_id)
    return row.serialize


@router.put(
    "/hearts/{user_id}",
    dependencies=[require_verified_email],
    responses=verified_responses(Hearts, NotEnoughCoinsError),
)
async def refill_hearts(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    row = await models.Hearts.get(user_id)
    if row.hearts < settings.hearts_max:
        if (await models.Coins.get(user_id)).coins < settings.hearts_refill_price:
            raise NotEnoughCoinsError
        await models.Transaction.create(user_id, -settings.hearts_refill_price, "Refill hearts", False)
        await models.Coins.add(user_id, -settings.hearts_refill_price, False)
        await clear_cache("coins")
        row.refill()

    return row.serialize
