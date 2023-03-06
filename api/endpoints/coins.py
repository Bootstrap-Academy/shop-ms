from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Body

from api import models
from api.auth import admin_auth, get_user, require_verified_email, user_auth
from api.exceptions.auth import PermissionDeniedError, admin_responses, verified_responses
from api.exceptions.coins import (
    CouldNotCaptureOrderError,
    CouldNotCreateOrderError,
    OrderNotFoundError,
    UserInfoMissingError,
)
from api.schemas.coins import Balance, BuyCoins
from api.schemas.user import User
from api.services import paypal
from api.services.auth import get_userinfo
from api.settings import settings
from api.utils.cache import clear_cache, redis_cached
from api.utils.docs import responses
from api.utils.email import BOUGHT_COINS
from api.utils.invoices import generate_invoice_pdf


router = APIRouter()


@router.get("/coins/paypal", responses=responses(str))
async def paypal_get_client_id() -> Any:
    """Return the paypal client id."""

    return settings.paypal_client_id


@router.post(
    "/coins/paypal/orders",
    dependencies=[require_verified_email],
    responses=verified_responses(str, CouldNotCreateOrderError, UserInfoMissingError),
)
async def paypal_buy_coins(data: BuyCoins, user: User = user_auth) -> Any:
    """
    Create a new order to buy coins via PayPal.

    Returns the order id.

    *Requirements:* **VERIFIED**
    """

    if not (info := await get_userinfo(user.id)) or not info.can_buy_coins:
        raise UserInfoMissingError

    order = await paypal.create_order(data.coins)
    if not order:
        raise CouldNotCreateOrderError

    await models.PaypalOrder.create(order, user.id, data.coins)

    return order


@router.post(
    "/coins/paypal/orders/{order_id}/capture",
    dependencies=[require_verified_email],
    responses=verified_responses(Balance, OrderNotFoundError, CouldNotCaptureOrderError, UserInfoMissingError),
)
async def paypal_capture_order(order_id: str, user: User = user_auth) -> Any:
    """
    Capture a PayPal order.

    *Requirements:* **VERIFIED**
    """

    if not (order := await models.PaypalOrder.get(order_id, user.id)) or not order.pending:
        raise OrderNotFoundError

    if not (info := await get_userinfo(user.id)) or not info.can_buy_coins:
        raise UserInfoMissingError

    if not await paypal.capture_order(order_id):
        raise CouldNotCaptureOrderError

    coins = await order.capture()

    if email := info.email:
        # TODO invoice number
        mwst = Decimal("0.19")
        rec = [
            f"{info.first_name} {info.last_name}" if info.first_name or info.last_name else f"{info.display_name}",
            info.street,
            f"{info.zip_code} {info.city}",
            info.country,
        ]
        invoice = await generate_invoice_pdf(
            "1337",
            "Rechnung",
            "EUR",
            mwst,
            4,
            2,
            [("MorphCoins", Decimal("0.01") / (mwst + 1), order.coins)],
            [r for r in rec if r and r.strip()],
        )
        await BOUGHT_COINS.send(
            email, coins=order.coins, eur=order.coins / 100, attachments=[("rechnung.pdf", invoice)]
        )
    await clear_cache("coins")

    return coins.serialize


@router.get("/coins/{user_id}", responses=verified_responses(Balance, PermissionDeniedError))
@redis_cached("coins", "user_id")
async def get_balance(user_id: str = get_user(require_self_or_admin=True)) -> Any:
    """
    Return the balance of a user.

    *Requirements:* **SELF** or **ADMIN**
    """

    return (await models.Coins.get(user_id)).serialize


@router.put("/coins/{user_id}", dependencies=[admin_auth], responses=admin_responses(bool))
async def set_coins(coins: int = Body(embed=True, ge=0), user_id: str = get_user(check_existence=True)) -> Any:
    """
    Set the balance of a user.

    *Requirements:* **ADMIN**
    """

    await models.Coins.set(user_id, coins)

    await clear_cache("coins")

    return True
