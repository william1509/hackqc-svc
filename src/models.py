from typing import List
from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from dataclasses import dataclass

@dataclass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    plants: Mapped[List["UserPlants"]] = relationship("UserPlants")

    def __repr__(self):
        return f'<User {self.name!r}>'
    
@dataclass
class UserPlants(Base):
    __tablename__ = 'user_plants'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column("users.id")
    plant_id: Mapped[int] = mapped_column("plants.id")
    img_path: Mapped[str] = mapped_column(String(120), unique=True)

    def __repr__(self):
        return f'<User {self.id}, Plant {self.img_path!r}>'
    
@dataclass
class Plants(Base):
    __tablename__ = 'plants'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    img_path: Mapped[str] = mapped_column(String(120), unique=True)

    def __repr__(self):
        return f'<Plant {self.name!r}>'