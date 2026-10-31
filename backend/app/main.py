import os

from app.models import init_db
from app.views import router as product_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import add_scalar_reference

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация БД при старте
@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(product_router)
# Добавить scalar docs

# Удобная документация
add_scalar_reference(app)

debug = bool(os.getenv("DEBUG", "false").lower() == "true")
host = str(os.getenv("HOST", '0.0.0.0'))
port = os.getenv("PORT", "5000")
