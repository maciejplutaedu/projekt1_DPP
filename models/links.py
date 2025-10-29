
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
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(primary_key=True)
    movieId: Mapped[int] = mapped_column(ForeignKey("movie.id"))
    imdbId: Mapped[str] = mapped_column(String(20))
    tmdbId: Mapped[str] = mapped_column(String(20))

    movie: Mapped["Movie"] = relationship(back_populates="links")