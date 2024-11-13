from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import  DeclarativeBase, sessionmaker
from config import settings


engine = create_engine(
    url= settings.DATABASE_URL,
    pool_size=10,          # Increase the pool size
    max_overflow=20
    # echo=True
)




session_factory = sessionmaker(engine)

def get_db_session():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    ...