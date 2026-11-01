import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from scalar_fastapi import add_scalar_reference
from sqlalchemy.exc import SQLAlchemyError

from app.core.db import init_db
from app.core.settings import settings
from app.views import router as product_router

loger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="INVIX API",
    description="Каталог товаров INVIX",
    version="0.1.0",
    lifespan=lifespan,
)

# origins перенес в окружение
# aauth будет через Telegram initData в заголовке
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ошибка БД — клиенту отдает 503 без деталей, traceback пишем в лог
@app.exception_handler(SQLAlchemyError)
def handle_db_error(request: Request, exc: SQLAlchemyError):
    loger.exception("Ошибка БД на %s", request.url.path)
    return JSONResponse(status_code=503, content={"detail": "БД недоступна"})


app.include_router(product_router)

# Удобная документация
add_scalar_reference(app)
