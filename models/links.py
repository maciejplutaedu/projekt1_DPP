
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



class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movieId: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    imdbId: Mapped[str] = mapped_column(String(20))
    tmdbId: Mapped[str] = mapped_column(String(20))

    movie: Mapped["Movie"] = relationship(back_populates="links")