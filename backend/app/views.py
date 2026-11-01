import logging
import uuid as uuid_lib

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel import Session, select

from .core import storage
from .core.db import get_session
from .models import Product
from .schemas import ProductCreate

# ошибся в написании, 2 раза запускал с ошибкой
logger = logging.getLogger(__name__)

router = APIRouter()


# получить все products
@router.get("/", response_model=list[Product])
def get_catalog(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products


# создать prdouct
@router.post("/product/", response_model=Product)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


# загрузить фото в minio и создать товар через multipartformdataa (name + image)
@router.post("/product/upload/", response_model=Product)
def upload_product(
    name: str = Form(...),
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    image_bytes = image.file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Фото пустое")

    object_name = f"products/{uuid_lib.uuid4().hex}.jpg"
    storage.upload_object(
        object_name,
        image_bytes,
        content_type=image.content_type or "image/jpeg",
    )

    db_product = Product(name=name, image_key=object_name)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


# получить product по ID
@router.get("/product/{product_id}", response_model=Product)
def get_product(product_id: int, session: Session = Depends(get_session)):
    request = select(Product).where(Product.id == product_id)
    product = session.exec(request).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


# удалить product, изображение из MinIO удалим при интеграции хранилища
@router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    request = select(Product).where(Product.id == product_id)
    product = session.exec(request).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    session.delete(product)
    session.commit()


# редактировать не делал, в тз не было требования


# healthcheck для docker compose: проверяем БД и доступность bucket в MinIO
@router.get("/health", include_in_schema=False)
def health(session: Session = Depends(get_session)):
    checks: dict[str, str] = {}

    try:
        session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        logger.exception("Healthcheck: база данных недоступна")
        checks["database"] = "error"

    try:
        checks["storage"] = "ok" if storage.bucket_exists() else "bucket missing"
    except Exception:
        logger.exception("Healthcheck: объектное хранилище недоступно")
        checks["storage"] = "error"

    healthy = all(value == "ok" for value in checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK
        if healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if healthy else "unhealthy", "checks": checks},
    )
