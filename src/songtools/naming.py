import re

from songtools.song_file_types import SongFile


def rename_song(song: SongFile) -> str:
    """Get the filename from the metadata of the file.
    If the file has no metadata, return the styled filename.

    :param Path file: Path to the file.

    :rtype: str
    :return: Filename from the metadata.
    """
    artists = song.get_artists()
    song.get_title()
    return ", ".join(artists) + " - " + song.get_title()


def has_cyrillic(text: str):
    """Find out if text has cyrillic characters.

    :param text:
    :return:
    """
    return bool(re.search("[\u0400-\u04ff]", text))
