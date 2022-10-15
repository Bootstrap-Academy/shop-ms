from typing import Any

from fastapi import APIRouter, Body, Header, Request

from api import models
from api.auth import admin_auth, get_user, require_verified_email, user_auth
from api.exceptions.auth import PermissionDeniedError, admin_responses, verified_responses
from api.exceptions.coins import CouldNotCaptureOrderError, CouldNotCreateOrderError, OrderNotFoundError
from api.schemas.coins import Balance, BuyCoins, StripeBuyCoins
from api.schemas.user import User
from api.services import paypal, stripe
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


@router.post(
    "/coins/stripe/checkout",
    dependencies=[require_verified_email],
    responses=verified_responses(str, CouldNotCreateOrderError),
)
async def stripe_create_checkout_session(data: StripeBuyCoins, user: User = user_auth) -> Any:
    """
    Create a new checkout session to buy coins via Stripe.

    Returns the checkout session url to redirect the user to.

    *Requirements:* **VERIFIED**
    """

    session = await stripe.create_checkout_session(data.coins, data.success_url, data.cancel_url)
    if not session:
        raise CouldNotCreateOrderError

    await models.StripeCheckout.create(session.id, user.id, data.coins)

    return session.url


@router.post("/coins/stripe/webhook", responses=responses(bool), include_in_schema=False)
async def stripe_payment_webhook(request: Request, stripe_signature: str = Header()) -> Any:
    if not (event := await stripe.get_checkout_session_event(await request.body(), stripe_signature)):
        raise CouldNotCaptureOrderError

    if event.type != "checkout.session.completed":
        return False

    if not (checkout := await models.StripeCheckout.get(event.checkout_id)) or not checkout.pending:
        return OrderNotFoundError

    await checkout.capture()

    return True


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
