
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


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(Integer)
    movieId: Mapped[int] = mapped_column(ForeignKey("movie.id"))
    tag: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[int] = mapped_column(Integer)

    movie: Mapped["Movie"] = relationship(back_populates="tags")