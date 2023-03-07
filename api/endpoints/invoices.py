import calendar
import hmac
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Path, Response

from api.auth import require_verified_email, user_auth
from api.exceptions.auth import verified_responses
from api.exceptions.coins import UserInfoMissingError
from api.schemas.user import User
from api.services.auth import get_userinfo
from api.settings import settings
from api.utils.invoices import generate_invoice_pdf


router = APIRouter()


@router.get("/credit_notes", dependencies=[require_verified_email], responses=verified_responses(str))
async def get_credit_notes_token(user: User = user_auth) -> Any:
    """Return the token to download credit note pdfs."""

    return f"{user.id}_" + hmac.digest(settings.invoice_secret.encode(), user.id.encode(), "sha256").hex()


@router.get("/credit_notes/{token}/{year}/{month}/credit_note.pdf")
async def download_credit_note(
    year: int = Path(ge=2022), month: int = Path(ge=1, le=12), token: str = Path(regex=r"^[^_]+_[^_]+$")
) -> Any:
    """Download the credit note pdf for a specific month."""

    user_id, token = token.split("_")
    if token != hmac.digest(settings.invoice_secret.encode(), user_id.encode(), "sha256").hex():
        return Response(status_code=401)

    if not (info := await get_userinfo(user_id)):
        raise UserInfoMissingError

    mwst = Decimal("0.19")
    rec = [
        f"{info.first_name} {info.last_name}" if info.first_name or info.last_name else f"{info.display_name}",
        info.street,
        f"{info.zip_code} {info.city}",
        info.country,
    ]

    transactions = [("Webinar blubb", 14), ("Coaching asdf", 100), ("Coding Challenge aosdifjiaosdfo", 1337)]

    # TODO invoice number
    return Response(
        await generate_invoice_pdf(
            "1337",
            "Gutschrift",
            "EUR",
            mwst,
            4,
            2,
            [(name, Decimal("0.01") / (mwst + 1), coins) for name, coins in transactions],
            [r for r in rec if r and r.strip()],
            date(year, month, calendar.monthrange(year, month)[1]),
        ),
        media_type="application/pdf",
    )
