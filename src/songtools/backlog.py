from pathlib import Path

from songtools.naming import has_cyrillic, build_correct_song_name
from songtools.song_file_types import get_song_file

IRRELEVANT_SUFFIXES = [".jpg", ".png", ".m3u", ".nfo", ".cue", ".txt"]
SUPPORTED_MUSIC_TYPES = [
    ".mp3",
]


def rename_songs_from_metadata(root_path: Path) -> None:
    for f in root_path.rglob("*"):
        if f.is_dir() or f.suffix not in SUPPORTED_MUSIC_TYPES:
            continue

        song = get_song_file(f)
        new_name = build_correct_song_name(song)
        if new_name.lower() != f.stem.lower():  # Some filesystems don't like casing
            f.rename(f.with_name(new_name))


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
        for folder in sorted(
            root_path.rglob("*"), key=lambda p: len(p.parts), reverse=True
        ):
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
                empties_exists = True
        nest += 1


def remove_irrelevant_files(root_path: Path) -> None:
    """Remove all irrelevant files from the backlog folder.
    It removes all files that are not music files.
    This is a blacklist approach rather than a whitelist,
    so I won't delete more exotic music suffixes by accident.

    :param Path root_path: Root path to the backlog folder
    """
    for folder in root_path.rglob("*"):
        if folder.is_file() and folder.suffix in IRRELEVANT_SUFFIXES:
            folder.unlink()


def remove_files_with_cyrilic(root_path: Path) -> None:
    """Remove all files that have cyrillic characters in their name.
    It is overwhelmingly Rap and pop that I don't keep.

    :param Path root_path: Root path to the backlog folder
    """
    for f in root_path.rglob("*"):
        if f.is_file() and has_cyrillic(f.name):
            f.unlink()


def clean_preimport_folder(backlog_folder: Path) -> None:
    """Take the backlog folder and clean it.
    It will:
     - Remove all irrelevant files from the backlog folder
     - Rename all songs from metadata (if possible)
     - Remove all empty folders recursively

    The order of operations is important!

    :param Path backlog_folder: Root path to the backlog folder
    """
    remove_irrelevant_files(backlog_folder)
    rename_songs_from_metadata(backlog_folder)
    remove_files_with_cyrilic(backlog_folder)
    remove_empty_folders(backlog_folder)
