from datetime import timedelta
from typing import Any, Literal

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user, require_verified_email
from api.exceptions.auth import verified_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.schemas.premium import PremiumPlan, PremiumStatus
from api.settings import settings
from api.utils.cache import clear_cache
from api.utils.docs import responses


router = APIRouter()


@router.get("/premium_plans", responses=responses(dict[str, PremiumPlan]))
async def get_plans() -> Any:
    return {
        "MONTHLY": PremiumPlan(price=settings.premium_monthly_price, months=1),
        "YEARLY": PremiumPlan(price=settings.premium_yearly_price, months=12),
    }


@router.get("/premium/{user_id}", dependencies=[require_verified_email], responses=verified_responses(PremiumStatus))
async def get_premium_status(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    row = await models.Premium.get_latest(user_id)
    if not row:
        return PremiumStatus(premium=False, since=None, until=None)
    return PremiumStatus(premium=True, since=row.start.timestamp(), until=row.end.timestamp())


@router.post(
    "/premium/{user_id}",
    dependencies=[require_verified_email],
    responses=verified_responses(PremiumStatus, NotEnoughCoinsError),
)
async def buy_premium(
    plan: Literal["MONTHLY", "YEARLY"] = Body(embed=True), user_id: str = get_user(require_self_or_admin=True)
) -> Any:
    if plan == "MONTHLY":
        price = settings.premium_monthly_price
        months = 1
    else:
        price = settings.premium_yearly_price
        months = 12

    if (await models.Coins.get(user_id)).coins < price:
        raise NotEnoughCoinsError
    await models.Transaction.create(user_id, -price, "Premium", False)
    await models.Coins.add(user_id, -price, False)
    await clear_cache("coins")

    row = await models.Premium.add(user_id, timedelta(days=365.25 / 12 * months))
    return PremiumStatus(premium=True, since=row.start.timestamp(), until=row.end.timestamp())
