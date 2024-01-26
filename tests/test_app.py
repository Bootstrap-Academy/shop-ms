from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock

from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient
from pytest_mock import MockerFixture

from ._utils import import_module, mock_asynccontextmanager
from api import app


def get_decorated_function(
    fastapi_patch: MagicMock, decorator_name: str, *decorator_args: Any, **decorator_kwargs: Any
) -> tuple[Any, Callable[..., Any]]:
    functions: list[Callable[..., Any]] = []
    decorator = MagicMock(side_effect=functions.append)
    getattr(fastapi_patch(), decorator_name).side_effect = lambda *args, **kwargs: (
        decorator if (args, kwargs) == (decorator_args, decorator_kwargs) else MagicMock()
    )
    fastapi_patch.reset_mock()

    module = import_module(app)

    decorator.assert_called_once()
    assert len(functions) == 1
    return module, functions[0]


async def test__db_session(mocker: MockerFixture) -> None:
    fastapi_patch = mocker.patch("fastapi.FastAPI")
    expected = MagicMock()
    request = MagicMock()

    module, db_session = get_decorated_function(fastapi_patch, "middleware", "http")

    module.db_context, [func_callback], assert_calls = mock_asynccontextmanager(1, None)
    call_next = AsyncMock(side_effect=lambda _: func_callback() or expected)

    result = await db_session(request, call_next)

    assert_calls()
    call_next.assert_called_once_with(request)
    assert result == expected


async def test__rollback_on_exception(mocker: MockerFixture) -> None:
    fastapi_patch = mocker.patch("fastapi.FastAPI")
    db_patch = mocker.patch("api.database.db")
    db_patch.session.rollback = AsyncMock()
    http_exception_patch = mocker.patch("starlette.exceptions.HTTPException")
    http_exception_handler_patch = mocker.patch("fastapi.exception_handlers.http_exception_handler", AsyncMock())

    _, rollback_on_exception = get_decorated_function(fastapi_patch, "exception_handler", http_exception_patch)

    result = await rollback_on_exception(request := MagicMock(), exc := MagicMock())

    db_patch.session.rollback.assert_called_once_with()
    http_exception_handler_patch.assert_called_once_with(request, exc)
    assert result == await http_exception_handler_patch()


async def test__on_startup(mocker: MockerFixture, monkeypatch: MonkeyPatch) -> None:
    fastapi_patch = mocker.patch("fastapi.FastAPI")
    db_patch = mocker.patch("api.database.db")

    module, on_startup = get_decorated_function(fastapi_patch, "on_event", "startup")
    db_patch.create_tables = AsyncMock()

    await on_startup()

    db_patch.create_tables.assert_not_called()  # use alembic migrations instead


async def test__on_shutdown(mocker: MockerFixture) -> None:
    fastapi_patch = mocker.patch("fastapi.FastAPI")

    _, on_shutdown = get_decorated_function(fastapi_patch, "on_event", "shutdown")

    await on_shutdown()


async def test__status(client: AsyncClient) -> None:
    response = await client.head("/status")
    assert response.status_code == 200
