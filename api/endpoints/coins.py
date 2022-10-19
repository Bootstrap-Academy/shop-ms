from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import admin_auth, get_user, require_verified_email, user_auth
from api.exceptions.auth import PermissionDeniedError, admin_responses, verified_responses
from api.exceptions.coins import CouldNotCaptureOrderError, CouldNotCreateOrderError, OrderNotFoundError
from api.schemas.coins import Balance, BuyCoins
from api.schemas.user import User
from api.services import paypal
from api.settings import settings
from api.utils.docs import responses


router = APIRouter()


@router.get("/coins/paypal", responses=responses(str))
async def paypal_get_client_id() -> Any:
    """Return the paypal client id."""

    return settings.paypal_client_id


@router.post(
    "/coins/paypal/orders",
    dependencies=[require_verified_email],
    responses=verified_responses(str, CouldNotCreateOrderError),
)
async def paypal_buy_coins(data: BuyCoins, user: User = user_auth) -> Any:
    """
    Create a new order to buy coins via PayPal.

    Returns the order id.

    *Requirements:* **VERIFIED**
    """

    order = await paypal.create_order(data.coins)
    if not order:
        raise CouldNotCreateOrderError

    await models.PaypalOrder.create(order, user.id, data.coins)

    return order

    # return Balance(coins=await models.Coins.add(user.id, data.coins))


@router.post(
    "/coins/paypal/orders/{order_id}/capture",
    dependencies=[require_verified_email],
    responses=verified_responses(Balance, OrderNotFoundError, CouldNotCaptureOrderError),
)
async def paypal_capture_order(order_id: str, user: User = user_auth) -> Any:
    """
    Capture a PayPal order.

    *Requirements:* **VERIFIED**
    """

    if not (order := await models.PaypalOrder.get(order_id, user.id)) or not order.pending:
        raise OrderNotFoundError

    if not await paypal.capture_order(order_id):
        raise CouldNotCaptureOrderError

    return Balance(coins=await order.capture())


@router.get("/coins/{user_id}", responses=verified_responses(Balance, PermissionDeniedError))
async def get_balance(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    """
    Return the balance of a user.

    *Requirements:* **SELF** or **ADMIN**
    """

    return Balance(coins=await models.Coins.get(user_id))


@router.put("/coins/{user_id}", dependencies=[admin_auth], responses=admin_responses(bool))
async def set_coins(coins: int = Body(embed=True, ge=0), user_id: str = get_user(check_existence=True)) -> Any:
    """
    Set the balance of a user.

    *Requirements:* **ADMIN**
    """

    await models.Coins.set(user_id, coins)
    return True
