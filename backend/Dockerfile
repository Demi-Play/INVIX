# alpine просто меньше, а на моей vps 1 ядрышко и 1 гиг, хз поднимется ли оно
FROM python:3.12-alpine AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# для сборки нативных зависимостей
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

# ---- runtime ----
FROM python:3.12-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN addgroup -g 1001 app \
    && adduser -u 1001 -G app -D -H -s /sbin/nologin app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app ./app
COPY --chown=app:app run.py ./run.py

USER app
EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)"]

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
