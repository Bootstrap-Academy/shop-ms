from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from borb.pdf import PDF, Document, Page
from borb.pdf.canvas.color.color import HexColor, X11Color
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.text.paragraph import Paragraph

from api.settings import settings
from api.utils.async_thread import run_in_thread


@run_in_thread
def generate_invoice_pdf(
    num: str,
    title: str,
    currency: str,
    mwst: Decimal | None,
    sprec: int,
    prec: int,
    products: list[tuple[str, Decimal, int]],
    recipient: list[str],
    issue_date: date | None = None,
) -> bytes:
    pdf = Document()
    page = Page()
    pdf.add_page(page)

    page_layout = SingleColumnLayout(page, vertical_margin=page.get_page_info().get_height() * Decimal(0.05))

    t = Table(number_of_rows=2, number_of_columns=2)

    t.add(Paragraph(""))
    t.add(
        Image(
            Path("assets/logo-text.png"), width=183, height=51, horizontal_alignment=Alignment.RIGHT, padding_bottom=24
        )
    )

    t.add(Paragraph(title, font_size=32))

    t2 = Table(number_of_rows=7, number_of_columns=1)
    t2.add(Paragraph("bootstrap academy GmbH", font="Helvetica-bold", horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("Wittelsbacherplatz 1", horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("80333 München", horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("+49 89 24 88 62 51 0", horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("hallo@bootstrap.academy", horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("USt.-IdNr.: DE354823768", horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("Handelsregister: HRB 275681", horizontal_alignment=Alignment.RIGHT))
    t2.no_borders()
    t.add(t2)

    t.no_borders()
    page_layout.add(t)

    page_layout.add(Paragraph(""))

    t = Table(number_of_rows=1, number_of_columns=5)

    t2 = Table(number_of_rows=len(recipient), number_of_columns=1)
    for r in recipient:
        t2.add(Paragraph(r))

    t2.no_borders()
    t.add(TableCell(t2, col_span=3))

    t2 = Table(number_of_rows=3, number_of_columns=2)
    t2.add(Paragraph("Datum", font="Helvetica-Bold"))
    t2.add(Paragraph((issue_date or date.today()).strftime("%d.%m.%Y"), horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("Rechnungs-Nr.", font="Helvetica-Bold"))
    t2.add(Paragraph(num if not settings.invoice_test else f"TEST-{num}", horizontal_alignment=Alignment.RIGHT))
    t2.add(Paragraph("Gesamtbetrag", font="Helvetica-Bold"))
    t2.add(
        Paragraph(
            f"{sum(x*y for _, x, y in products) * (1 + (mwst or 0)):.{prec}f} {currency}",
            horizontal_alignment=Alignment.RIGHT,
        )
    )

    t2.no_borders()
    t2.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    t.add(TableCell(t2, col_span=2))

    t.no_borders()
    page_layout.add(t)

    page_layout.add(Paragraph(""))

    t = Table(number_of_rows=len(products) + 1, number_of_columns=12)
    t.add(
        TableCell(
            Paragraph("Bezeichnung", font_color=X11Color("White")), col_span=6, background_color=HexColor("0b5156")
        )
    )
    t.add(
        TableCell(
            Paragraph("Einzelpreis", horizontal_alignment=Alignment.RIGHT, font_color=X11Color("White")),
            col_span=2,
            background_color=HexColor("0b5156"),
        )
    )
    t.add(
        TableCell(
            Paragraph("Menge", horizontal_alignment=Alignment.RIGHT, font_color=X11Color("White")),
            col_span=2,
            background_color=HexColor("0b5156"),
        )
    )
    t.add(
        TableCell(
            Paragraph("Gesamtpreis", horizontal_alignment=Alignment.RIGHT, font_color=X11Color("White")),
            col_span=2,
            background_color=HexColor("0b5156"),
        )
    )

    odd_color = HexColor("BBBBBB")
    even_color = HexColor("FFFFFF")
    for i, (name, price, cnt) in enumerate(products):
        c = even_color if i % 2 == 0 else odd_color
        t.add(TableCell(Paragraph(name), col_span=6, background_color=c))
        t.add(
            TableCell(
                Paragraph(f"{price:.{sprec}f} {currency}", horizontal_alignment=Alignment.RIGHT),
                col_span=2,
                background_color=c,
            )
        )
        t.add(TableCell(Paragraph(f"{cnt}", horizontal_alignment=Alignment.RIGHT), col_span=2, background_color=c))
        t.add(
            TableCell(
                Paragraph(f"{price*cnt:.{prec}f} {currency}", horizontal_alignment=Alignment.RIGHT),
                col_span=2,
                background_color=c,
            )
        )

    t.set_padding_on_all_cells(Decimal(4), Decimal(4), Decimal(4), Decimal(4))
    t.no_borders()
    page_layout.add(t)

    t = Table(number_of_rows=2 + bool(mwst), number_of_columns=4)

    netto = sum(x * y for _, x, y in products)
    t.add(TableCell(Paragraph("Nettobetrag", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT), col_span=3))
    t.add(TableCell(Paragraph(f"{netto:.{prec}f} {currency}", horizontal_alignment=Alignment.RIGHT)))

    if mwst:
        tax = netto * mwst
        t.add(
            TableCell(
                Paragraph(
                    f"zzgl. {(mwst*100).normalize()}% MwSt.",
                    font="Helvetica-Bold",
                    horizontal_alignment=Alignment.RIGHT,
                ),
                col_span=3,
            )
        )
        t.add(TableCell(Paragraph(f"{tax:.{prec}f} {currency}", horizontal_alignment=Alignment.RIGHT)))
    else:
        tax = Decimal(0)

    total = netto + tax
    t.add(TableCell(Paragraph("Gesamtbetrag", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT), col_span=3))
    t.add(TableCell(Paragraph(f"{total:.{prec}f} {currency}", horizontal_alignment=Alignment.RIGHT)))

    t.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    t.no_borders()
    page_layout.add(t)

    out = BytesIO()
    PDF.dumps(out, pdf)
    out.seek(0)
    return out.read()
