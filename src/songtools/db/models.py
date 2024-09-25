from sqlalchemy.types import String, Integer, DECIMAL
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class BacklogSong(Base):
    __tablename__ = "backlog_songs"

    path: Mapped[str] = mapped_column(String(500), primary_key=True)
    title: Mapped[str] = mapped_column(String(80))
    artists: Mapped[str] = mapped_column(String(100))

    bpm: Mapped[float] = mapped_column(DECIMAL(6, 3))
    genre: Mapped[str] = mapped_column(String(40))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    key: Mapped[str] = mapped_column(String(5))
    energy: Mapped[int] = mapped_column(Integer)
