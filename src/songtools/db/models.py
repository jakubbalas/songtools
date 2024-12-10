from datetime import datetime
from sqlalchemy import func, TIMESTAMP
from sqlalchemy.types import String, Integer, DECIMAL, Boolean
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class BacklogSong(Base):
    __tablename__ = "song_backlog"

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


class HeardSong(Base):
    __tablename__ = "songs_heard"

    name_hash: Mapped[str] = mapped_column(String(300), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(300), nullable=True)
    in_collection: Mapped[bool] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


class CollectionSong(Base):
    __tablename__ = "song_collection"

    name_hash: Mapped[str] = mapped_column(String(300), primary_key=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
