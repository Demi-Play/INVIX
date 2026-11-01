FROM python:3.12-alpine AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apk add --no-cache --virtual .build-deps \
        build-base \
        libffi-dev \
        openssl-dev \
    && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

FROM python:3.12-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN addgroup -g 1001 bot \
    && adduser -u 1001 -G bot -D -H -s /sbin/nologin bot

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=bot:bot main.py config.py handlers.py ./

USER bot

CMD ["python", "main.py"]
