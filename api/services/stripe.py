from typing import Any

import stripe
import stripe.error
from pydantic import BaseModel, Extra

from api.settings import settings
from api.utils.async_thread import run_in_thread


stripe.api_key = settings.stripe_secret_key


class CheckoutSession(BaseModel):
    id: str
    url: str


class CheckoutSessionEvent(BaseModel):
    checkout_id: str
    type: str


@run_in_thread
def create_checkout_session(coins: int, success_url: str, cancel_url: str) -> CheckoutSession | None:
    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {"currency": "EUR", "product_data": {"name": "Morphcoins"}, "unit_amount": 1},
                    "quantity": coins,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return CheckoutSession(id=session.id, url=session.url)
    except stripe.error.StripeError:
        return None


@run_in_thread
def get_checkout_session_event(data: dict[str, Any], sig_header: str) -> CheckoutSessionEvent | None:
    try:
        event = stripe.Webhook.construct_event(data, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return None

    checkout_id = event.get("data", {}).get("object", {}).get("id")
    event_type = event.get("type")
    return CheckoutSessionEvent(checkout_id=checkout_id, type=event_type) if checkout_id and event_type else None
