from sqlalchemy.types import String, Integer, DECIMAL
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class BacklogSong(Base):
    __tablename__ = "backlog_songs"

    path: Mapped[str] = mapped_column(String(500), primary_key=True)
    title: Mapped[str] = mapped_column(String(80), nullable=True)
    artists: Mapped[str] = mapped_column(String(100), nullable=True)

    bpm: Mapped[float] = mapped_column(DECIMAL(6, 3), nullable=True)
    genre: Mapped[str] = mapped_column(String(40), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    key: Mapped[str] = mapped_column(String(5), nullable=True)
    energy: Mapped[int] = mapped_column(Integer, nullable=True)
    file_size_kb: Mapped[int] = mapped_column(Integer, nullable=True)
