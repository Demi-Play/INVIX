from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlmodel import select

from .models import Product, Session, get_session

router = APIRouter()

@router.get("/")
def get_catalog():
    pass


@router.get("/product/<id>")
def delete_product_by_id(id: int):
    #delete DB data and delete minio data
    pass


# создать prdouct
@router.post("/product/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# получить все products
@router.get("/", response_model=list[Product])
def get_heroes(session: Session = Depends(get_session)):
    request = select(Product)
    products = session.exec(request).all()
    return products

# получить product по ID
@router.get("/product/{id}")
def get_hero(id: int, session: Session = Depends(get_session)):
    request = select(Product).where(Product.id == id)
    product = session.exec(request).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product
