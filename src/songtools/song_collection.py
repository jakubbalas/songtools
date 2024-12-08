import click
from pathlib import Path
from songtools import config
from songtools.naming import build_correct_song_file_name
from songtools.song_file_types import SUPPORTED_MUSIC_TYPES, SongFile, UnableToExtractData


def show_collection_name_inconsistencies():
    """Show inconsistencies in collection names."""

    inconsistencies = get_incorrectly_formatted_collection_names(Path(config.collection_path))
    for i in inconsistencies:
        click.secho(f"rename: {i[0].absolute()} to {i[1]}",  fg="yellow")


def get_incorrectly_formatted_collection_names(collection_path: Path) -> list[(Path, str)]:
    res = []
    for f in collection_path.rglob("*"):
        if f.is_dir() or f.suffix not in SUPPORTED_MUSIC_TYPES:
            continue

        try:
            song = SongFile(f)
            built_name = build_correct_song_file_name(song.artists, song.title)
            if built_name != f.stem:
                res.append((f, built_name))
        except UnableToExtractData:
            click.secho(f"Could not extract data from {f}", fg="red")

    return res
