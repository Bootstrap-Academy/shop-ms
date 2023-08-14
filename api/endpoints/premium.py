from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user, require_verified_email
from api.exceptions.auth import verified_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.exceptions.premium import NoPremiumError
from api.models.premium import pay_for_premium
from api.schemas.premium import PremiumPlan, PremiumStatus
from api.utils.docs import responses


router = APIRouter()


@router.get("/premium_plans", responses=responses(dict[str, PremiumPlan]))
async def get_plans() -> Any:
    return {x.name: PremiumPlan(price=x.price, months=x.months) for x in models.premium.PremiumPlan}


@router.get("/premium/{user_id}", dependencies=[require_verified_email], responses=verified_responses(PremiumStatus))
async def get_premium_status(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    row = await models.Premium.get_latest(user_id)
    if not row:
        return PremiumStatus(premium=False, since=None, until=None, autopay=None)
    autopay = await models.PremiumAutopay.get(user_id)
    return PremiumStatus(
        premium=True, since=row.start.timestamp(), until=row.end.timestamp(), autopay=autopay and autopay.plan.name
    )


@router.post(
    "/premium/{user_id}",
    dependencies=[require_verified_email],
    responses=verified_responses(PremiumStatus, NotEnoughCoinsError),
)
async def buy_premium(
    plan: models.premium.PremiumPlan = Body(),
    autopay: bool = Body(),
    user_id: str = get_user(require_self_or_admin=True),
) -> Any:
    if not await pay_for_premium(user_id, plan):
        raise NotEnoughCoinsError

    row = await models.Premium.add(user_id, plan.timedelta)
    await models.PremiumAutopay.set(user_id, plan if autopay else None)
    return PremiumStatus(
        premium=True, since=row.start.timestamp(), until=row.end.timestamp(), autopay=plan.name if autopay else None
    )


@router.put(
    "/premium/{user_id}/autopay",
    dependencies=[require_verified_email],
    responses=verified_responses(bool, NoPremiumError),
)
async def update_autopay(
    plan: models.premium.PremiumPlan | None = Body(None, embed=True),
    user_id: str = get_user(require_self_or_admin=True),
) -> Any:
    if not await models.Premium.get_latest(user_id):
        raise NoPremiumError

    await models.PremiumAutopay.set(user_id, plan)
    return True
