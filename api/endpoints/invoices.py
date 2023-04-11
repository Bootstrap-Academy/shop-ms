import calendar
import hmac
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Path, Response
from sqlalchemy import and_, asc

from api import models
from api.auth import require_verified_email, user_auth
from api.database import db
from api.database.database import filter_by
from api.exceptions.auth import verified_responses
from api.exceptions.coins import InvoiceNotFoundError, UserInfoMissingError
from api.exceptions.invoices import CreditNoteNotYetAvailableError
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

    last_day = calendar.monthrange(year, month)[1]
    issue_date = date(year, month, last_day)

    if issue_date >= date.today():
        raise CreditNoteNotYetAvailableError

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
    if info.business:
        rec.append(f"USt.-IdNr.: {info.vat_id}")

    transactions = [
        (transaction.description, transaction.coins)
        async for transaction in await db.stream(
            filter_by(models.Transaction, user_id=user_id, credit_note=True)
            .where(
                and_(
                    models.Transaction.created_at >= datetime.combine(date(year, month, 1), time.min),
                    models.Transaction.created_at <= datetime.combine(date(year, month, last_day), time.max),
                )
            )
            .order_by(asc(models.Transaction.created_at))
        )
    ]

    public_id = await models.CreditNoteUser.get(user_id)

    return Response(
        await generate_invoice_pdf(
            f"G{year:04}{month:02}-{public_id}",
            "Gutschrift",
            "EUR",
            mwst,
            4,
            2,
            [(name, Decimal("0.01") / (mwst + 1), coins) for name, coins in transactions],
            [r for r in rec if r and r.strip()],
            issue_date,
        ),
        media_type="application/pdf",
    )


@router.get("/invoices/{token}/{invoice_no}/invoice.pdf")
async def download_invoice(invoice_no: int = Path(ge=0), token: str = Path(regex=r"^[^_]+_[^_]+$")) -> Any:
    """Download a specific invoice."""

    user_id, token = token.split("_")
    if token != hmac.digest(settings.invoice_secret.encode(), user_id.encode(), "sha256").hex():
        return Response(status_code=401)

    if not (order := await db.get(models.PaypalOrder, invoice_no=invoice_no, user_id=user_id)):
        raise InvoiceNotFoundError

    if not (info := await get_userinfo(user_id)):
        raise UserInfoMissingError

    mwst = Decimal("0.19")
    rec = [
        f"{info.first_name} {info.last_name}" if info.first_name or info.last_name else f"{info.display_name}",
        info.street,
        f"{info.zip_code} {info.city}",
        info.country,
    ]
    if info.business:
        rec.append(f"USt.-IdNr.: {info.vat_id}")

    return Response(
        await generate_invoice_pdf(
            f"R{order.invoice_no:07}",
            "Rechnung",
            "EUR",
            mwst,
            4,
            2,
            [("MorphCoins", Decimal("0.01") / (mwst + 1), order.coins)],
            [r for r in rec if r and r.strip()],
            order.created_at.date(),
        ),
        media_type="application/pdf",
    )
