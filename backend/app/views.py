from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from .core.db import get_session
from .models import Product
from .schemas import ProductCreate

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
