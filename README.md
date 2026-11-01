# INVIX - job interview

Каталог товаров: FastAPI + Postgre + minio, Telegram бот на aiogram 3.x и
Mini App на React (Vite). Один SPA - и для сайта, и для Telegram Mini App.

## Это тестовое задание для компании INVIX

Реализовано:

Каталог товаров с картинками, админ-управление через Telegram-бота
(добавление товара - фото + caption, удаление), хранение в minio, БД PostgreSQL.

## Как запустить у себя

```bash
cp .env.example .env
# в .env: TELEGRAM_BOT_TOKEN, пароли, при необходимости ADMIN_IDS
docker compose up -d --build

docker compose ps          # все сервисы должны быть healthy/running
docker compose logs -f     # логи

# проверка
curl http://localhost:5000/health
curl http://localhost:3000
```

Остановка:

```bash
docker compose down       # с сохранением данных
docker compose down -v    # с удалением данных PostgreSQL + MinIO
```

## Что внутри

- Backend (FastAPI) - CRUD товаров, `/health`, `/product/upload/` (multipart, minio, Posgre)
- Frontend (React + Vite, nginx) - SPA: сайт + Mini App, nginx проксирует `/api/` на backend (не знаю next.js, сроки не для изучения)
- Bot (aiogram 3.31) - long polling, `/start`, админ-флоу (кнопка создания и удаления).
- Postgre, minio, volumes `invix_postgres_data` / `invix_minio_data`.

## Переменные окружения

- `.env` (основной) + `.env.example` - шаблон.
- `TELEGRAM_BOT_TOKEN`, `MINI_APP_URL`, `ADMIN_IDS` - бот.
- `POSTGRES_*`, `MINIO_*`, `BACKEND_*` - инфраструктура.
- `PG_*` / `PG_URL` - backend (URL БД).
- `BACKEND_UPSTREAM` - куда nginx фронта проксирует `/api/`.

## Troubleshooting

- Бот не отвечает: смотрим `docker compose logs -f bot`, проверяем `TELEGRAM_API_IP` (обход блокировки).
- Бот: web_app кнопка - только по публичному https; для `http` - текст с ссылкой.
- но как говорится, работает - не трожб)
