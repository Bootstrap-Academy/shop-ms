from typing import Any

from fastapi import APIRouter

from api import models
from api.auth import get_user
from api.exceptions.auth import internal_responses


router = APIRouter()


@router.get("/premium/{user_id}", responses=internal_responses(bool))
async def get_premium(user_id: str = get_user()) -> Any:
    return await models.Premium.get_latest(user_id) is not None
