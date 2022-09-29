from typing import cast

from httpx import AsyncClient

from api.settings import settings


def get_client() -> AsyncClient:
    return AsyncClient(base_url=settings.paypal_base_url, auth=(settings.paypal_client_id, settings.paypal_secret))


async def create_order(coins: int) -> str | None:
    async with get_client() as client:
        response = await client.post(
            "/v2/checkout/orders",
            json={
                "intent": "CAPTURE",
                "purchase_units": [{"amount": {"currency_code": "EUR", "value": str(round(coins / 100, 2))}}],
            },
        )
        if response.status_code != 201:
            return None
        return cast(str, response.json().get("id"))


async def capture_order(order_id: str) -> bool:
    async with get_client() as client:
        response = await client.post(f"/v2/checkout/orders/{order_id}/capture", json={})
        if response.status_code != 201:
            return False

        return cast(str | None, response.json().get("status")) == "COMPLETED"
