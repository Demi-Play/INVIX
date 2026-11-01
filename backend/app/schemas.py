from sqlmodel import Field, SQLModel


### Schemas
# id и created_at заддает сервер
class ProductCreate(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    image_key: str = Field(min_length=1, max_length=255)
