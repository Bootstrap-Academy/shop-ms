FROM python:3.11-alpine AS builder

RUN apk add --no-cache build-base gcc musl-dev libffi-dev postgresql14-dev git

WORKDIR /build

RUN pip install poetry

COPY pyproject.toml /build/
COPY poetry.lock /build/

RUN set -ex \
    && virtualenv .venv \
    && . .venv/bin/activate \
    && poetry install -n --no-root --without dev


FROM python:3.11-alpine

LABEL org.opencontainers.image.source="https://github.com/Bootstrap-Academy/shop-ms"

WORKDIR /app

RUN set -x \
    && apk add --no-cache curl libpq \
    && addgroup -g 1000 api \
    && adduser -G api -u 1000 -s /bin/sh -D -H api

USER api

EXPOSE 8000

COPY --from=builder /build/.venv/lib /usr/local/lib
COPY alembic /app/alembic
COPY alembic.ini /app/

COPY assets /app/assets/
COPY templates /app/templates/
COPY api /app/api/

HEALTHCHECK --interval=20s --timeout=5s --retries=1 \
    CMD curl -fI http://localhost:${PORT:-8000}/status

CMD python -m alembic upgrade head && python -m api
