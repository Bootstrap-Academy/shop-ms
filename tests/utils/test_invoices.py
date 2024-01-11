from decimal import Decimal

from api.utils.invoices import generate_invoice_pdf


async def test_generate_invoice_pdf() -> None:
    mwst = Decimal("0.19")
    await generate_invoice_pdf(
        "123456",
        "Test Invoice",
        "EUR",
        mwst,
        4,
        2,
        [("MorphCoins", Decimal("0.01") / (mwst + 1), 1337)],
        ["foo", "bar", "baz"],
    )
