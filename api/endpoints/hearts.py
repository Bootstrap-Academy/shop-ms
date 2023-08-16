from typing import Any

from fastapi import APIRouter

from api import models
from api.auth import get_user, require_verified_email, user_auth
from api.exceptions.auth import verified_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.schemas.hearts import Hearts, HeartsConfig
from api.schemas.user import User
from api.settings import settings
from api.utils.cache import clear_cache
from api.utils.docs import responses


router = APIRouter()


@router.get("/hearts/config", responses=responses(HeartsConfig))
async def get_hearts_config() -> Any:
    """Return the public hearts config."""

    return HeartsConfig(hearts_max=settings.hearts_max, hearts_refill_price=settings.hearts_refill_price)


@router.get("/hearts/{user_id}", dependencies=[require_verified_email], responses=verified_responses(Hearts))
async def get_hearts(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    """Return the hearts status of a given user."""

    row = await models.Hearts.get(user_id)
    return row.serialize


@router.put("/hearts", dependencies=[require_verified_email], responses=verified_responses(Hearts, NotEnoughCoinsError))
async def refill_hearts(user: User = user_auth) -> Any:
    """Manually refill hearts to maximum. Does nothing if the user already has this number of hearts."""

    row = await models.Hearts.get(user.id)
    if row.hearts < settings.hearts_max:
        if (await models.Coins.get(user.id)).coins < settings.hearts_refill_price:
            raise NotEnoughCoinsError
        await models.Transaction.create(user.id, -settings.hearts_refill_price, "Refill hearts", False)
        await models.Coins.add(user.id, -settings.hearts_refill_price, False)
        await clear_cache("coins")
        row.refill()

    return row.serialize
