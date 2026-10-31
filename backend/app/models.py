from date import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Session, create_engine
import os

### Models
#
#
class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    image_key: str
    created_at: datetime = Field(default_factory=datetime.now)


### DB
#
#
debug = os.getenv("DEBUG")
pg_url = os.getenv("PG_URL", "postgresql+psycopg://postgres:root@localhost:5432/invix_db")
engine = create_engine(pg_url, echo=debug)

def init_db():
    SQLModel.metadata.create_all(engine)

engine = create_engine()
# для добавления сессии в эндпоинты
def get_session():
    with Session(engine) as session:
        yield session
