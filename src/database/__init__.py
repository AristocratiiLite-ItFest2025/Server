import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", \
    "postgresql://postgres:postgres@db:5432/aristocratii"
)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    return db
