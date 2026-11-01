from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from .settings import settings

### DB

# engine per process, в умных интернетах нашел)
engine = create_engine(url=settings.pg_url, echo=settings.debug, pool_pre_ping=True)


def init_db():
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            # БЛОКИРОВКА ТРАНЗАКЦИЙ ДЛЯ pOSTGRE
            conn.execute(text("SELECT pg_advisory_xact_lock(748364701)"))
            SQLModel.metadata.create_all(conn)
    else:
        SQLModel.metadata.create_all(engine)


# контекст менеджер с закрытием по окончании
def get_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session
