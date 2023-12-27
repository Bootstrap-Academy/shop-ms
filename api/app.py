"""
## Authentication, Special parameters, Requirements
See [Auth Microservice](/auth/docs).
"""

import asyncio
from typing import Awaitable, Callable, TypeVar

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import __version__
from .database import db, db_context
from .endpoints import ROUTER, TAGS
from .logger import get_logger, setup_sentry
from .models.premium_autopay import run_autopay
from .settings import settings
from .utils.debug import check_responses
from .utils.docs import add_endpoint_links_to_openapi_docs


T = TypeVar("T")

logger = get_logger(__name__)

app = FastAPI(
    title="Bootstrap Academy Backend: Shop Microservice",
    description=__doc__,
    version=__version__,
    root_path=settings.root_path,
    root_path_in_servers=False,
    servers=[{"url": settings.root_path}] if settings.root_path else None,
    openapi_tags=TAGS,
)
app.include_router(ROUTER)

if settings.debug:
    app.middleware("http")(check_responses)


add_endpoint_links_to_openapi_docs(app.openapi())

if settings.sentry_dsn:
    logger.debug("initializing sentry")
    setup_sentry(app, settings.sentry_dsn, "shop-ms", __version__)

if settings.debug:
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )


@app.middleware("http")
async def db_session(request: Request, call_next: Callable[..., Awaitable[T]]) -> T:
    async with db_context():
        return await call_next(request)


@app.exception_handler(StarletteHTTPException)
async def rollback_on_exception(request: Request, exc: HTTPException) -> Response:
    await db.session.rollback()
    return await http_exception_handler(request, exc)


async def autopay_loop() -> None:
    while True:
        try:
            await run_autopay()
        except Exception as e:
            logger.exception(e)
        await asyncio.sleep(60 * 60)


@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(autopay_loop())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    pass


@app.head("/status", include_in_schema=False)
async def status() -> None:
    pass
