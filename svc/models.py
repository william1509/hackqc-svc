from typing import List
from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    plants: Mapped[List["UserPlants"]] = relationship()

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<User {self.name!r}>'
    
class UserPlants(Base):
    __tablename__ = 'user_plants'
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("users.id")
    img_path: Mapped[str] = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<Plant {self.img_path!r}>'