from pydantic import BaseModel, Extra

from api.services.internal import InternalService
from api.utils.cache import redis_cached


class UserInfo(BaseModel):
    name: str
    display_name: str
    email: str | None
    business: bool | None
    first_name: str | None
    last_name: str | None
    street: str | None
    zip_code: str | None
    city: str | None
    country: str | None
    vat_id: str | None
    can_buy_coins: bool
    can_receive_coins: bool

    class Config:
        extra = Extra.ignore


@redis_cached("user", "user_id")
async def get_userinfo(user_id: str) -> UserInfo | None:
    async with InternalService.AUTH.client as client:
        response = await client.get(f"/users/{user_id}")
        if response.status_code != 200:
            return None

        return UserInfo(**response.json())


async def exists_user(user_id: str) -> bool:
    return await get_userinfo(user_id) is not None
