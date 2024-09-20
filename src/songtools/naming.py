import re

from songtools.song_file_types import SongFile


def build_correct_song_name(song: SongFile) -> str:
    """Get the filename from the metadata of the file.
    If the file has no metadata, return the styled filename.

    :param SongFile song: SongFile object containing metadata.

    :rtype: str
    :return: Valid filename that can be used.
    """
    return ", ".join(song.get_artists()) + " - " + song.get_title()


def has_cyrillic(text: str):
    """Find out if text has cyrillic characters.

    :param text:
    :return:
    """
    return bool(re.search("[\u0400-\u04ff]", text))
