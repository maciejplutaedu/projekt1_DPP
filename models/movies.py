
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.types import String, Float, Integer
from database import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    genres: Mapped[str] = mapped_column(String(255))

    links: Mapped[List["Link"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    ratings: Mapped[List["Rating"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship(back_populates="movie", cascade="all, delete-orphan")