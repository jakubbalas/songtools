import click
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import select, delete, Engine
from copy import deepcopy

from songtools import config
from songtools.db.models import HeardSong, CollectionSong
from songtools.naming import build_correct_song_file_name
from songtools.song_file_types import (
    SUPPORTED_MUSIC_TYPES,
    SongFile,
    UnableToExtractData,
)


def show_collection_name_inconsistencies():
    """Show inconsistencies in collection names."""

    inconsistencies = get_incorrectly_formatted_collection_names()
    for i in inconsistencies:
        click.secho(f"rename: {i[0].absolute()} to {i[1]}", fg="yellow")


def list_collection_songs_paths() -> list[Path]:
    collection_path = Path(config.collection_path)
    return [
        f
        for f in collection_path.rglob("*")
        if f.is_file() and f.suffix in SUPPORTED_MUSIC_TYPES
    ]


def get_collection_items():
    res = {}
    for x in list_collection_songs_paths():
        song = SongFile(x)
        res[song.name_hash] = song

    return res


def get_incorrectly_formatted_collection_names() -> list[(Path, str)]:
    res = []
    for f in list_collection_songs_paths():
        try:
            song = SongFile(f)
            built_name = build_correct_song_file_name(song.artists, song.title)
            if built_name != f.stem:
                res.append((f, built_name))
        except UnableToExtractData:
            click.secho(f"Could not extract data from {f}", fg="red")

    return res


def recreate_collection_records(
    collection_songs: dict[str, SongFile], db_engine: Engine
):
    with Session(db_engine) as session:
        session.execute(delete(CollectionSong))
        session.commit()

        for song_hash, song in collection_songs.items():
            db_song = CollectionSong(
                name_hash=song.name_hash,
                file_path=song.path.name,
                file_size=song.file_size_kb,
            )
            session.add(db_song)
        session.commit()


def sync_collection_with_heard_songs(
    collection_songs: dict[str, SongFile], db_engine: Engine
):
    # TODO: sync to heard table insert / update
    # TODO: remove non-existing files from heard collection.
    collection_songs = deepcopy(collection_songs)
    with Session(db_engine) as session:
        stm = select(HeardSong).where(HeardSong.in_collection == True)  # noqa
        for song in session.scalars(stm).all():
            if song.name_hash not in collection_songs:
                song.in_collection = False
                session.commit()
            else:
                del collection_songs[song.name_hash]

        for song_hash, song in collection_songs.items():
            item = session.scalars(
                select(HeardSong).where(HeardSong.name_hash == song.name_hash)
            ).first()
            if not item:
                item = HeardSong(
                    name_hash=song.name_hash,
                    file_name=song.path.name,
                    in_collection=True,
                )
                session.add(item)
            else:
                item.in_collection = True
        session.commit()


def sync_collection_items(db_engine: Engine):
    collection_items = get_collection_items()
    recreate_collection_records(collection_items, db_engine)
    sync_collection_with_heard_songs(collection_items, db_engine)
