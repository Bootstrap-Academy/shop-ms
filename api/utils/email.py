import asyncio
import random
import string
from dataclasses import dataclass
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import aiosmtplib
import email_validator
from jinja2 import Environment, FileSystemLoader

from .async_thread import run_in_thread
from ..logger import get_logger
from ..settings import settings


logger = get_logger(__name__)


env = Environment(loader=FileSystemLoader("templates"), autoescape=True)


@dataclass
class Message:
    title: str
    template: str
    attachments: list[Path]

    async def send(self, recipient: str, *, reply_to: str | None = None, **kwargs: Any) -> None:
        content = env.get_template(self.template).render(**kwargs)
        await send_email(recipient, self.title, content, reply_to=reply_to, attachments=self.attachments)


BOUGHT_COINS = Message(
    title="Kaufbestätigung - Bootstrap Academy",
    template="bought_coins.html",
    attachments=[Path("assets/allgemeine_geschaeftsbedingungen.pdf"), Path("assets/widerrufsbelehrung.pdf")],
)


@run_in_thread
def check_email_deliverability(email: str) -> bool:
    try:
        email_validator.validate_email(email)
    except email_validator.EmailNotValidError:
        return False
    return True


async def send_email(
    recipient: str, title: str, body: str, *, attachments: list[Path] | None = None, reply_to: str | None = None
) -> None:
    if not await check_email_deliverability(recipient):
        raise ValueError("Invalid email address")

    logger.debug(f"Sending email to {recipient} ({title})")

    message = MIMEMultipart()
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message["Subject"] = title
    if reply_to:
        message["Reply-To"] = reply_to
    message.attach(MIMEText(body, "html"))

    for path in attachments or []:
        with path.open(mode="rb") as file:
            part = MIMEApplication(file.read(), Name=path.name)
        part["Content-Disposition"] = f"attachment; filename={path.name}"
        message.attach(part)

    asyncio.create_task(
        aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=settings.smtp_tls,
            start_tls=settings.smtp_starttls,
        )
    )


def generate_verification_code() -> str:
    return "-".join(
        "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)) for _ in range(4)  # noqa: S311
    )
