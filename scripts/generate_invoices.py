import asyncio
from decimal import Decimal

from api.database import db, db_context
from api.database.database import filter_by
from api.models.paypal_orders import PaypalOrder
from api.services.auth import get_userinfo
from api.utils.invoices import generate_invoice_pdf


async def _main() -> None:
    mwst = Decimal("0.19")
    recs: dict[str, list[str]] = {}

    async def user_info(id: str) -> list[str] | None:
        if id in recs:
            return recs[id]

        info = await get_userinfo.__wrapped__(id)  # type: ignore
        if info is None:
            return None
        rec = [
            f"{info.first_name} {info.last_name}" if info.first_name or info.last_name else f"{info.display_name}",
            info.street,
            f"{info.zip_code} {info.city}",
            info.country,
        ]
        recs[id] = rec
        return rec

    async with db_context():
        order: PaypalOrder
        async for order in await db.stream(
            filter_by(PaypalOrder, pending=False).where(PaypalOrder.invoice_no != None)  # noqa: E711
        ):
            print(order.id, order.user_id, order.created_at, order.coins, order.invoice_no)
            rec = await user_info(order.user_id)
            if not rec:
                print(f"ERROR: No user info for {order.user_id}")
                rec = [order.user_id]
            invoice = await generate_invoice_pdf(
                (ino := f"R{order.invoice_no:07}"),
                "Rechnung",
                "EUR",
                mwst,
                4,
                2,
                [("MorphCoins", Decimal("0.01") / (mwst + 1), order.coins)],
                [r for r in rec if r and r.strip()],
                order.created_at.date(),
            )
            with open(f"{ino}.pdf", "wb") as f:
                f.write(invoice)


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
