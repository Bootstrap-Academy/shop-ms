from api.services.internal import InternalService
from api.utils.cache import redis_cached


@redis_cached("user", "user_id")
async def exists_user(user_id: str) -> bool:
    async with InternalService.AUTH.client as client:
        response = await client.get(f"/users/{user_id}")
        return response.status_code == 200
