from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import get_user
from api.exceptions.auth import internal_responses
from api.schemas.hearts import Hearts


router = APIRouter()


@router.get("/hearts/{user_id}", responses=internal_responses(Hearts))
async def get_hearts(user_id: str = get_user()) -> Any:
    row = await models.Hearts.get(user_id)
    return row.serialize


@router.post("/hearts/{user_id}", responses=internal_responses(bool))
async def add_hearts(hearts: int = Body(embed=True), user_id: str = get_user()) -> Any:
    row = await models.Hearts.get(user_id)
    return row.add(hearts)
