from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user, require_verified_email, user_auth
from api.exceptions.auth import verified_responses
from api.exceptions.coins import NotEnoughCoinsError
from api.exceptions.premium import NoPremiumError
from api.models.premium import pay_for_premium
from api.schemas.premium import PremiumPlan, PremiumStatus
from api.schemas.user import User
from api.utils.docs import responses


router = APIRouter()


@router.get("/premium_plans", responses=responses(dict[str, PremiumPlan]))
async def get_plans() -> Any:
    """Return all available premium plans."""

    return {x.name: PremiumPlan(price=x.price, months=x.months) for x in models.premium.PremiumPlan}


@router.get("/premium/{user_id}", dependencies=[require_verified_email], responses=verified_responses(PremiumStatus))
async def get_premium_status(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    """Return the premium status of a given user."""

    row = await models.Premium.get_latest(user_id)
    if not row:
        return PremiumStatus(premium=False, since=None, until=None, autopay=None)
    autopay = await models.PremiumAutopay.get(user_id)
    return PremiumStatus(
        premium=True, since=row.start.timestamp(), until=row.end.timestamp(), autopay=autopay and autopay.plan.name
    )


@router.post(
    "/premium", dependencies=[require_verified_email], responses=verified_responses(PremiumStatus, NotEnoughCoinsError)
)
async def buy_premium(
    plan: models.premium.PremiumPlan = Body(), autopay: bool | None = Body(None), user: User = user_auth
) -> Any:
    """
    Select a premium plan, pay for it and increase the user's premium timespan by the corresponding number of months.

    Set `autopay` to `true` to automatically renew premium.
    """

    if not await pay_for_premium(user.id, plan):
        raise NotEnoughCoinsError

    row = await models.Premium.add(user.id, plan.timedelta)
    if autopay is not None:
        await models.PremiumAutopay.set(user.id, plan if autopay else None)
    return PremiumStatus(
        premium=True, since=row.start.timestamp(), until=row.end.timestamp(), autopay=plan.name if autopay else None
    )


@router.put(
    "/premium/autopay", dependencies=[require_verified_email], responses=verified_responses(bool, NoPremiumError)
)
async def update_autopay(
    plan: models.premium.PremiumPlan | None = Body(None, embed=True), user: User = user_auth
) -> Any:
    """Change the premium plan to renew automatically or disable autopay."""

    if not await models.Premium.get_latest(user.id):
        raise NoPremiumError

    await models.PremiumAutopay.set(user.id, plan)
    return True
