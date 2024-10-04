import click
from songtools.utils import echo
from pathlib import Path
from random import randint
from sqlalchemy.orm import Session
from sqlalchemy import Engine, select
from songtools.db.models import BacklogSong
from songtools import config

from songtools.naming import has_cyrillic, build_correct_song_file_name
from songtools.song_file_types import SongFile, UnableToExtractData

IRRELEVANT_SUFFIXES = [
    ".accurip",
    ".bpm",
    ".cue",
    ".docx",
    ".ico",
    ".jpg",
    ".log",
    ".m3u",
    ".nfo",
    ".png",
    ".sfv",
    ".txt",
    ".url",
]
SUPPORTED_MUSIC_TYPES = [".mp3", ".flac"]
MUSIC_MIX_MIN_SECONDS = 1000
META_FILES = [".DS_Store", "desktop.ini"]


def handle_music_files(root_path: Path) -> None:
    """Bundle of all functionality that has to be done on a file
    It is a bit more expensive to load the metadata so in here load it once and
    then do all required operations.

    :param Path root_path: Root path to the backlog folder
    """
    for f in root_path.rglob("*"):
        if f.is_dir():
            continue
        elif f.name in META_FILES:
            echo(f"Skipping meta file {f.stem}", "INFO")
            continue
        elif f.suffix not in SUPPORTED_MUSIC_TYPES:
            echo(f"Unsupported music file {f}", "CHECK")
            continue
        try:
            song = SongFile(f)
        except UnableToExtractData:
            echo(f"Can't extract metadata from file {f}", "CHECK")
            continue
        if remove_music_mixes(f, song):
            continue
        try:
            rename_songs_from_metadata(f, song)
        except OSError as e:
            echo(f"Can't rename file {f}  || Error: {e}", "ERR")


def rename_songs_from_metadata(song_path: Path, song: SongFile) -> None:
    """
    Get artists and title from metadata and style it so it can be used
    to rename files.

    :param song_path: Path to the song file
    :param song: Implementation of a song file object from metadata
    """
    new_name = build_correct_song_file_name(song.artists, song.title)
    # Note: some filesystems don't like if I only change file casing
    #       - that's why I have to make a tmp name first
    if new_name.lower() != song_path.stem.lower():
        song_path.rename(song_path.with_stem(new_name))
        echo(f"Renamed {song_path} to {new_name}", "OK")
    elif new_name != song_path.stem:
        temp_name = new_name + str(randint(10000000, 99999999))
        song_path = song_path.rename(song_path.with_stem(temp_name))
        song_path.rename(song_path.with_stem(new_name))
        echo(f"Fixed song casing {song_path} to {new_name}", "OK")


def remove_empty_folders(root_path: Path) -> None:
    """Recursively remove all empty folders.
    It stops at 100 iterations of nesting to prevent any weird infinite loops.

    :param Path root_path: Root path to start the search
    """
    empties_exists = True
    nest = 0
    max_nested = 100
    while empties_exists and nest < max_nested:
        empties_exists = False
        for f in root_path.rglob("*"):
            if f.is_dir() and not any(f.iterdir()):
                f.rmdir()
                empties_exists = True
            elif f.is_dir() and folder_contains_only_metadata(f):
                for meta_item in f.iterdir():
                    meta_item.unlink()
                f.rmdir()
                empties_exists = True
        nest += 1


def folder_contains_only_metadata(folder: Path) -> bool:
    for f in folder.iterdir():
        if f.is_dir() or (f.is_file() and f.name not in META_FILES):
            return False
    return True


def remove_irrelevant_files(root_path: Path) -> None:
    """Remove all irrelevant files from the backlog folder.
    It removes all files that are not music files.
    This is a blacklist approach rather than a whitelist,
    so I won't delete more exotic music suffixes by accident.

    :param Path root_path: Root path to the backlog folder
    """
    for f in root_path.rglob("*"):
        if f.is_file() and f.suffix.lower() in IRRELEVANT_SUFFIXES:
            echo(f"Removing irrelevant file {f}", "OK")
            f.unlink()


def remove_files_with_cyrilic(root_path: Path) -> None:
    """Remove all files that have cyrillic characters in their name.
    It is overwhelmingly Rap and pop that I don't keep.

    :param Path root_path: Root path to the backlog folder
    """
    for f in root_path.rglob("*"):
        if f.is_file() and has_cyrillic(f.name):
            echo(f"Removing cyrillic file {f}", "OK")
            f.unlink()


def remove_music_mixes(song_path: Path, song: SongFile) -> bool:
    """Remove all music mixes from the backlog folder.
    It removes all files that are shorter than MUSIC_MIX_MIN_SECONDS.

    :param Path song_path: Root path to the backlog folder
    :param SongFile song: Implementation of a song file object from metadata

    :return: True if the dj mix was removed, False otherwise
    """
    if song.duration_seconds > MUSIC_MIX_MIN_SECONDS:
        echo(f"Removing DJ mix {song_path}", "OK")
        song_path.unlink()
        return True
    else:
        return False


def clean_preimport_folder(backlog_folder: Path) -> None:
    """Take the backlog folder and clean it.
    It will:
     - Remove all irrelevant files from the backlog folder
     - Rename all songs from metadata (if possible)
     - Remove all empty folders recursively

    The order of operations is important!

    :param Path backlog_folder: Root path to the backlog folder
    """
    if not backlog_folder.exists() or not backlog_folder.is_dir():
        echo(f"Folder {backlog_folder} does not exist", "ERR")
        return
    remove_irrelevant_files(backlog_folder)
    remove_files_with_cyrilic(backlog_folder)
    handle_music_files(backlog_folder)
    remove_empty_folders(backlog_folder)


def load_backlog_folder_files(
    backlog_folder: Path, db_engine: Engine, store_after: int = 10000
) -> None:
    """Load all songs from the backlog folder into the db
    This makes it easier to search and filter songs based on metadata.
    """
    counter = 0
    songs = []
    for f in backlog_folder.rglob("*"):
        if f.is_file() and f.suffix in SUPPORTED_MUSIC_TYPES:
            path = str(f.relative_to(config.backlog_path))
            songs.append(BacklogSong(path=path))
            counter += 1
            if counter % store_after == 0:
                with Session(db_engine) as session:
                    session.add_all(songs)
                    session.commit()
                    songs = []
                echo(f"Loaded {counter} songs", "INFO")

    if songs:
        with Session(db_engine) as session:
            session.add_all(songs)
            session.commit()
    echo(f"Loaded {counter} songs", "INFO")


def load_backlog_folder_metadata(
    db_engine: Engine, path_select: str | None = None
) -> None:
    """Load all metadata"""
    with Session(db_engine) as session:
        stm = select(BacklogSong).where(BacklogSong.title == None)  # noqa: E711
        if path_select:
            stm = stm.where(BacklogSong.path.ilike(path_select))
        total = session.query(BacklogSong.path).count()
        with click.progressbar(
            session.scalars(stm).all(),
            length=total,
            label="Loading metadata for songs",
        ) as bar:
            for db_song in bar:
                try:
                    song = SongFile(config.backlog_path / Path(db_song.path))
                    db_song.title = song.title
                    db_song.artists = ",".join(song.artists)
                    db_song.bpm = song.bpm
                    db_song.genre = song.genre
                    db_song.duration_seconds = song.duration_seconds
                    db_song.year = song.year
                    db_song.key = song.key
                    db_song.energy = song.energy
                    db_song.file_size_kb = song.file_size_kb

                    session.commit()
                except Exception as e:
                    session.rollback()
                    echo(
                        f"Error loading metadata for {db_song.path} || Error: {e}",
                        "ERR",
                    )
                    continue
