from typing import Any

from fastapi import APIRouter

from api import models
from api.auth import get_user
from api.exceptions.auth import internal_responses
from api.schemas.premium import PremiumStatus


router = APIRouter()


@router.get("/premium/{user_id}", responses=internal_responses(PremiumStatus))
async def get_premium(user_id: str = get_user()) -> Any:
    row = await models.Premium.get_latest(user_id)
    if not row:
        return PremiumStatus(premium=False, since=None, until=None)
    return PremiumStatus(premium=True, since=row.start.timestamp(), until=row.end.timestamp())
