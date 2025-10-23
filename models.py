
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.types import String, Float, Integer


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movie"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    genres: Mapped[str] = mapped_column(String(255))

    links: Mapped[List["Link"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    ratings: Mapped[List["Rating"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship(back_populates="movie", cascade="all, delete-orphan")


class Link(Base):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(primary_key=True)
    movieId: Mapped[int] = mapped_column(ForeignKey("movie.id"))
    imdbId: Mapped[str] = mapped_column(String(20))
    tmdbId: Mapped[str] = mapped_column(String(20))

    movie: Mapped["Movie"] = relationship(back_populates="links")


class Rating(Base):
    __tablename__ = "rating"

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(Integer)
    movieId: Mapped[int] = mapped_column(ForeignKey("movie.id"))
    rating: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[int] = mapped_column(Integer)

    movie: Mapped["Movie"] = relationship(back_populates="ratings")


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(Integer)
    movieId: Mapped[int] = mapped_column(ForeignKey("movie.id"))
    tag: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[int] = mapped_column(Integer)

    movie: Mapped["Movie"] = relationship(back_populates="tags")