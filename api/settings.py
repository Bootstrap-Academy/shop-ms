import secrets
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
    root_path: str = ""

    debug: bool = False
    reload: bool = False

    cache_ttl: int = 300

    jwt_secret: str = secrets.token_urlsafe(64)

    auth_url: str = ""

    paypal_base_url: str = "https://api.sandbox.paypal.com"
    paypal_client_id: str = ""
    paypal_secret: str = ""

    stripe_public_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    internal_jwt_ttl: int = 10

    database_url: str = Field(
        "mysql+aiomysql://fastapi:fastapi@mariadb:3306/fastapi",
        regex=r"^(mysql\+aiomysql|postgresql\+asyncpg|sqlite\+aiosqlite)://.*$",
    )
    pool_recycle: int = 300
    pool_size: int = 20
    max_overflow: int = 20
    sql_show_statements: bool = False

    redis_url: str = Field("redis://redis:6379/2", regex=r"^redis://.*$")
    auth_redis_url: str = Field("redis://redis:6379/0", regex=r"^redis://.*$")

    sentry_dsn: str | None = None
    sentry_environment: str = "test"


settings = Settings()
