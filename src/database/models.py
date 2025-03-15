from sqlalchemy import VARCHAR, Column, Integer

from src.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(255))
    password = Column(VARCHAR(255))
