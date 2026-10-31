from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


### Models
class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    image_key: str
    # aware UTC datetime — sqlmodel 2.1 не принимает naive-даты
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

# Позже добавлю юзера для имитации корзины и саму корзину
